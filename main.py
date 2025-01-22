import os
import json
import base64
import whisper
import requests
import logging
from pathlib import Path
from typing import Optional

MODEL = 'llama3.2-vision:latest'

class WhatsAppChatProcessor:
    def __init__(self, folder_path: str):
        """
        Initialize the WhatsApp chat processor.
        
        Args:
            folder_path: Path to the folder containing chat and media files
            ollama_model: Name of the Ollama model to use for image processing
        """
        self.folder_path = Path(folder_path)
        self.ollama_model = MODEL
        self.chat_content = ""
        self.whisper_model = None  # Lazy loading for faster initialization
        self.logger = self._setup_logger()
        self._check_ffmpeg()
        
    def _setup_logger(self) -> logging.Logger:
        """Configure logging for the processor."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def _check_ffmpeg(self) -> None:
        """Check if FFmpeg is properly installed and accessible."""
        try:
            import subprocess
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            self.logger.error("FFmpeg is not installed or not found in PATH")
            print("\nFFmpeg is required but not found. Please install FFmpeg:")
            print("- Windows: Download from https://ffmpeg.org/download.html")
            print("- Mac: Run 'brew install ffmpeg'")
            print("- Linux: Run 'sudo apt-get install ffmpeg'")
            raise RuntimeError("FFmpeg not found")

    def _load_whisper_model(self) -> None:
        """Lazy load the Whisper model when needed."""
        if self.whisper_model is None:
            self.logger.info("Loading Whisper model...")
            try:
                self.whisper_model = whisper.load_model("base")
            except Exception as e:
                self.logger.error(f"Error loading Whisper model: {str(e)}")
                raise RuntimeError(f"Failed to load Whisper model: {str(e)}")

    def process_audio(self, audio_path: Path) -> str:
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            self.logger.info(f"Processing audio file: {audio_path}")
            
            # Verify file exists and is readable
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Convert path to absolute path
            audio_path = audio_path.absolute()
            
            # Load model (this will also verify FFmpeg installation)
            self._load_whisper_model()
            
            # Log the exact path being used
            self.logger.info(f"Transcribing audio from path: {audio_path}")
            
            # Perform transcription
            result = self.whisper_model.transcribe(str(audio_path))
            
            # Return only the transcribed text, cleaned
            return result["text"].strip()
            
        except FileNotFoundError as e:
            self.logger.error(f"Audio file not found: {audio_path}")
            return f"[Error: Audio file not found]"
        except Exception as e:
            self.logger.error(f"Error processing audio file {audio_path}: {str(e)}")
            return f"[Error transcribing audio: {str(e)}]"

    def process_image(self, image_path: Path) -> str:
        """
        Process image using Ollama model.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Image description
        """
        try:
            self.logger.info(f"Processing image file: {image_path}")
            
            with open(image_path, 'rb') as img_file:
                # Convert image to base64
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                
                # Prepare the request
                url = "http://localhost:11434/api/generate"
                payload = {
                    "model": self.ollama_model,
                    "prompt": "Describe this image in detail but concisely",
                    "images": [image_base64]
                }
                
                # Make the request
                response = requests.post(url, json=payload)
                response.raise_for_status()
                
                # Parse the streaming response
                description = ""
                for line in response.text.strip().split('\n'):
                    if line:
                        try:
                            response_data = json.loads(line)
                            if 'response' in response_data:
                                description += response_data['response']
                        except json.JSONDecodeError:
                            continue
                
                return description.strip()
                
        except Exception as e:
            self.logger.error(f"Error processing image file {image_path}: {str(e)}")
            return f"[Error processing image: {str(e)}]"

    def read_chat_file(self) -> bool:
        """
        Read the _chat.txt file into memory.
        
        Returns:
            Boolean indicating success
        """
        chat_file = self.folder_path / "_chat.txt"
        try:
            self.logger.info("Reading chat file")
            with open(chat_file, 'r', encoding='utf-8') as f:
                self.chat_content = f.read()
            return True
        except Exception as e:
            self.logger.error(f"Error reading chat file: {str(e)}")
            return False

    def replace_media_references(self, filename: str, media_type: str, content: str) -> None:
        """
        Replace media references in the chat content.
        
        Args:
            filename: Original filename to replace
            media_type: Type of media ('VOICE NOTE' or 'IMAGE')
            content: Content to replace the reference with
        """
        try:
            original_pattern = f"<attached: {filename}>"
            replacement = f"[{media_type}: {content}]"
            self.chat_content = self.chat_content.replace(original_pattern, replacement)
        except Exception as e:
            self.logger.error(f"Error replacing media reference: {str(e)}")

    def save_processed_chat(self) -> bool:
        """
        Save the processed chat content to a new file.
        
        Returns:
            Boolean indicating success
        """
        output_file = self.folder_path / "processed_chat.txt"
        try:
            self.logger.info("Saving processed chat")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(self.chat_content)
            return True
        except Exception as e:
            self.logger.error(f"Error saving processed chat: {str(e)}")
            return False

    def process_folder(self) -> bool:
        """
        Process all media files in the folder and update the chat content.
        
        Returns:
            Boolean indicating success
        """
        try:
            # Read the chat file first
            if not self.read_chat_file():
                return False

            # Process all files in the folder
            for file_path in self.folder_path.iterdir():
                if file_path.name == "_chat.txt" or file_path.name == "processed_chat.txt":
                    continue

                if file_path.suffix.lower() == '.opus':
                    self.logger.info(f"Found audio file: {file_path.name}")
                    transcription = self.process_audio(file_path)
                    self.replace_media_references(file_path.name, "VOICE NOTE", transcription)
                
                elif file_path.suffix.lower() == '.jpg':
                    self.logger.info(f"Found image file: {file_path.name}")
                    description = self.process_image(file_path)
                    self.replace_media_references(file_path.name, "IMAGE", description)

            # Save the processed chat
            return self.save_processed_chat()

        except Exception as e:
            self.logger.error(f"Error processing folder: {str(e)}")
            return False

def main():
    """
    Main function to demonstrate usage of the WhatsAppChatProcessor.
    
    Example folder structure:
    chat_folder/
    ├── _chat.txt
    ├── 00000019-AUDIO-2024-12-09-17-25-03.opus
    └── 00000021-PHOTO-2024-12-09-17-28-47.jpg
    """
    # Get the folder path from user input or use a default
    folder_path = input("Enter the path to your WhatsApp chat folder: ").strip()
    if not folder_path:
        folder_path = "chat_folder"  # Default folder name
    
    # Create processor instance
    processor = WhatsAppChatProcessor(
        folder_path=folder_path,
    )
    
    # Process the folder
    print(f"\nProcessing WhatsApp chat folder: {folder_path}")
    print("This may take a while depending on the number of files...")
    
    if processor.process_folder():
        print("\nSuccess! Chat processing completed.")
        print(f"Processed chat saved to: {os.path.join(folder_path, 'processed_chat.txt')}")
    else:
        print("\nError: Chat processing failed. Check the logs for details.")

if __name__ == "__main__":
    main()