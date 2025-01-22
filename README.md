# WhatsApp Chat Media Processor

This Python script processes WhatsApp chat exports by converting voice notes to text and generating descriptions for images. It uses OpenAI's Whisper for audio transcription and Ollama for image description.

## Features

- Converts voice notes (.opus files) to text using Whisper
- Generates descriptions for images using Ollama's vision models
- Maintains original chat formatting
- Creates a processed version of the chat with media content replaced inline
- Detailed logging for troubleshooting

## Prerequisites

- Python 3.8 or higher
- FFmpeg installed and in your system PATH
- Ollama running locally with a vision-capable model (e.g., llava)

### Installing FFmpeg

- **Windows**: 
  - Using Chocolatey: `choco install ffmpeg`
  - Or download from [FFmpeg website](https://ffmpeg.org/download.html)
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

### Installing Ollama

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Start the Ollama server:
   ```bash
   ollama serve
   ```
3. Pull the required model:
   ```bash
   ollama pull llama3.2-vision:latest
   ```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Learning-Gen-AI/WhatsAppTranscribeAndSearch.git
   cd WhatsAppTranscribeAndSearch
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Prepare your WhatsApp chat folder:
   ```
   chat_folder/
   ├── _chat.txt              # Original WhatsApp chat export
   ├── audio1.opus            # Voice notes
   └── image1.jpg             # Images
   ```

2. Run the script:
   ```bash
   python main.py
   ```

3. Enter the path to your chat folder when prompted.

4. The script will create a `processed_chat.txt` file with all media content replaced:
   - Voice notes: `[VOICE NOTE: {transcription}]`
   - Images: `[IMAGE: {description}]`

## Example

Original chat:
```
[2024/01/22, 17:25:03] John: ‎<attached: 00000019-AUDIO-2024-01-22-17-25-03.opus>
[2024/01/22, 17:25:30] Jane: Ok, got it
‎[2024/01/22, 17:28:47] John: ‎<attached: 00000021-PHOTO-2024-01-22-17-28-47.jpg>
```

Processed chat:
```
[2024/01/22, 17:25:03] John: [VOICE NOTE: I'll be there in about 15 minutes]
[2024/01/22, 17:25:30] Jane: Ok, see you now
[2024/01/22, 17:28:47] John: [IMAGE: A red car parked in front of a building]
```

## Troubleshooting

1. FFmpeg errors:
   - Ensure FFmpeg is installed and accessible from command line
   - Try running `ffmpeg -version` to verify installation

2. Ollama errors:
   - Ensure Ollama server is running (`ollama serve`)
   - Verify model is installed (`ollama list`)
   - Check if the model supports vision features

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[Apache 2.0](LICENSE)