# Signal AI Chat Bot

This project implements an AI-powered chatbot that integrates with Signal messenger, allowing users to interact with various AI models (Gemini and Flux right now) through Signal messages.

## Features

- Interaction with AI models (Gemini) via Signal messages
- Image generation capabilities (using Flux and LoRAs)
- Session management for continuous conversations
- Command system for changing bot settings

## Prerequisites

1. A dedicated phone number for the Signal bot
2. A device to link the Signal app to the API
3. [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) set up and running. Use the `json-rpc` for faster chat responses. The command could look like this:
   ```bash
   podman run -p 8080:8080 \
      -v $HOME/.local/share/signal-api:/home/.local/share/signal-cli \
      -e 'MODE=json-rpc' docker.io/bbernhard/signal-cli-rest-api
   ```

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/signal-ai-chat.git
   cd signal-ai-chat
   ```

2. Set up a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set up the required environment variables:
   ```bash
   export GOOGLE_AI_STUDIO_API="your_google_ai_studio_api_key"
   export SIGNAL_PHONE_NUMBER="your_signal_bot_phone_number"
   export TRUSTED_PHONE_NUMBERS="comma,separated,list,of,trusted,numbers"
   export FAL_KEY="your_fal_ai_key"  # Optional, for image generation
   export LORA_PATH_TO_URL='{"triggerword": "<url>"}'  # Optional, for LoRA models
   export PROMPT_REPLACE_DICT='{"replace this": "to this", "and this": "to this"}'  # Optional
   ```

4. Run the Signal AI bot:
   ```bash
   python src/main.py
   ```

## Usage

Once the bot is running, you can interact with it via Signal messages. Available commands include:

- `!help`: Show help message
- `!cp [prompt_name]`: Change system prompt
- `!cm <model_number>`: Change AI model
- `!cup <custom_prompt>`: Set a custom system prompt
- `!im <prompt>`: Generate an image (trusted users only)
- `!is <size_number>`: Change image size

## Configuration

You can customize various settings in the `config.py` file, including:

- Available AI models
- System instructions/personalities
- Image sizes
- Trusted phone numbers
- API endpoints

## Future Ideas

- [ ] Run on a Raspberry PI Zero 2W
- [ ] Use function calling for the bot with useful functions
- [ ] Use the bot in groupe chats

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.