import io
from datetime import datetime
from typing import Dict
from PIL import Image
import requests
import google.generativeai as genai
import fal_client
from config import *
from user import User

genai.configure(api_key=os.environ["GOOGLE_AI_STUDIO_API"])

users = {}
HELP_MESSAGE = f"""
Available commands
- !help: Show this help message
- !cp [prompt_name]: Change system prompt: {', '.join(SYSTEM_INSTRUCTIONS.keys())}
- !cm <model_number>: Change AI model {', '.join(VALID_MODELS)}
- !cup <custom_prompt_number>: Set a custom system prompt
- !im <prompt>: Generate an image
- !is <size_numer>: Change image size {', '.join(IMAGE_SIZES.keys())}
"""


def download_attachment(attachment_id: str):
    url = f"{HTTP_BASE_URL}/v1/attachments/{attachment_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error downloading attachment: {e}")
        return None


def get_or_create_user(sender):
    if sender not in users:
        users[sender] = User(sender, DEFAULT_SYSTEM_INSTRUCTION, DEFAULT_MODEL)
    return users[sender]


def handle_change_prompt_cmd(user, system_instruction_number):
    if system_instruction_number.isdigit() and 1 <= int(
        system_instruction_number
    ) <= len(SYSTEM_INSTRUCTIONS):
        system_prompt_name = list(SYSTEM_INSTRUCTIONS.keys())[
            int(system_instruction_number) - 1
        ]
        print(system_prompt_name)
        user.set_system_instruction(SYSTEM_INSTRUCTIONS[system_prompt_name])
        user.send_message(f'System prompt changed to "{system_prompt_name}"')
    else:
        user.send_message(
            f"Available system prompts:\n{'\n'.join(SYSTEM_INSTRUCTIONS.keys())}"
        )


def handle_change_model_cmd(user, ai_model_number):
    if ai_model_number.isdigit() and 1 <= int(ai_model_number) <= len(VALID_MODELS):
        user.set_model(VALID_MODELS[int(ai_model_number) - 1])
        user.send_message(f'AI model changed to: "{user.current_model}"')
    else:
        user.send_message(f"Available AI models:\n{'\n'.join(VALID_MODELS)}")


def handle_custom_prompt_cmd(user, custom_prompt):
    if custom_prompt == "":
        user.send_message("Please provide a custom prompt.")
    else:
        user.set_system_instruction(custom_prompt)
        user.send_message(
            f"System prompt changed to:\n{user.current_system_instruction}"
        )


def handle_image_size_cmd(user, size_number):
    if size_number.isdigit() and 1 <= int(size_number) <= len(IMAGE_SIZES):
        image_size_name = list(IMAGE_SIZES.keys())[int(size_number) - 1]
        user.set_image_size(IMAGE_SIZES[image_size_name])
        user.send_message(
            f'Image size changed to: "{image_size_name}" with {user.image_size})'
        )
    else:
        user.send_message(
            f"Invalid image size. Available sizes:\n{'\n'.join(IMAGE_SIZES.keys())}"
        )


def handle_generate_image_cmd(user, prompt):
    for old_word, new_word in PROMPT_REPLACE_DICT.items():
        prompt = prompt.replace(old_word, new_word)

    lora_arguments = []
    for lora_name in LORA_PATH_TO_URL.keys():
        if lora_name in prompt:
            lora_arguments.append(
                {"path": LORA_PATH_TO_URL[lora_name], "scale": DEFAULT_LORA_SCALE}
            )

    api_endpoint = (
        DEFAULT_IMG_API_ENDPOINT if len(lora_arguments) == 0 else "fal-ai/flux-lora"
    )

    arguments = {
        "prompt": prompt,
        "image_size": user.image_size,
        "num_images": 1,
        "enable_safety_checker": False,
        "output_format": "png",
    }

    if api_endpoint == "fal-ai/flux/schnell":
        arguments = {
            **arguments,
            "num_inference_steps": 4,
        }
    elif api_endpoint == "fal-ai/flux-lora":
        arguments = {
            **arguments,
            "num_inference_steps": 28,
            "guidance_scale": 3.5,
            "loras": lora_arguments,
        }
    elif api_endpoint == "fal-ai/flux-pro/v1.1":
        arguments = {**arguments, "num_inference_steps": 28, "guidance_scale": 3.5}
    else:
        raise Exception(f"unknown fal.ai API endpoint: {api_endpoint}")

    print("Generating an image with these arguments:", arguments)

    handler = fal_client.submit(api_endpoint, arguments)

    result = handler.get()

    if "images" in result and result["images"]:
        image_data = result["images"][0]
        response = requests.get(image_data["url"])
        if response.status_code == 200:
            user.send_message("", attachment=response.content)
    else:
        user.send_message("Failed to generate the image.")


def handle_ai_message(user, content, attachments):
    message_components = [content] if content else []

    for attachment in attachments:
        attachment_id = attachment.get("id")
        if attachment_id:
            attachment_data = download_attachment(attachment_id)
            if attachment_data:
                image = Image.open(io.BytesIO(attachment_data))
                message_components.append(image)

    if message_components:
        try:
            chat = user.get_or_create_chat_session()
            response = chat.send_message(message_components)
            ai_response = response.text
        except Exception as e:
            print(f"Error generating AI response: {e}")
            ai_response = "Sorry, I couldn't generate a response at this time."
        user.send_message(ai_response)
    else:
        user.send_message("I received your message, but it seems to be empty.")


def process_message(message: Dict):
    if "envelope" not in message or "dataMessage" not in message["envelope"]:
        return

    sender = message["envelope"]["source"]
    content = message["envelope"]["dataMessage"].get("message", "")
    timestamp = datetime.fromtimestamp(message["envelope"]["timestamp"] / 1000.0)
    attachments = message["envelope"]["dataMessage"].get("attachments", [])

    print(f"Received message from {sender} at {timestamp}: {content}")

    parts = content.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1].strip() if len(parts) > 1 else ""

    user = get_or_create_user(sender)

    if command == "!help":
        user.send_message(HELP_MESSAGE)
    elif command == "!cp":
        handle_change_prompt_cmd(user, args)
    elif command == "!cm":
        handle_change_model_cmd(user, args)
    elif command == "!cup":
        handle_custom_prompt_cmd(user, args)
    elif command == "!im" and user.trusted:
        handle_generate_image_cmd(user, args)
    elif command == "!is":
        handle_image_size_cmd(user, args)
    else:
        handle_ai_message(user, content, attachments)
