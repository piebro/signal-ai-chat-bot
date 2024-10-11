import os
import json
import prompts

WS_BASE_URL = "ws://localhost:8080"
HTTP_BASE_URL = "http://localhost:8080"
SIGNAL_PHONE_NUMBER = os.environ.get("SIGNAL_PHONE_NUMBER")
SESSION_TIMEOUT = 30  # minutes
VALID_MODELS = [
    "(1) gemini-1.5-flash-8b",
    "(2) gemini-1.5-flash-002",
    "(3) gemini-1.5-pro-002",
]
DEFAULT_MODEL = "(2) gemini-1.5-flash-002"
TRUSTED_PHONE_NUMBERS = os.environ.get("TRUSTED_PHONE_NUMBERS", "").split(",")
LORA_PATH_TO_URL = json.loads(os.environ.get("LORA_PATH_TO_URL", "{}"))
PROMPT_REPLACE_DICT = json.loads(os.environ.get("PROMPT_REPLACE_DICT", "{}"))
IMAGE_SIZES = {
    "(1) square": {"width": 512, "height": 512},
    "(2) square_hd": {"width": 1024, "height": 1024},
    "(3) landscape_4_3": {"width": 1024, "height": 768},
    "(4) landscape_16_9": {"width": 1024, "height": 576},
    "(5) portrait_3_4": {"width": 768, "height": 1024},
    "(6) portrait_9_16": {"width": 576, "height": 1024},
}
DEFAULT_IMAGE_SIZE = IMAGE_SIZES["(5) portrait_3_4"]
OUTPUT_DIR = "generated_images"
DEFAULT_LORA_SCALE = 1
DEFAULT_IMG_API_ENDPOINT = "fal-ai/flux-pro/v1.1"  # alternative: fal-ai/flux/schnell


SYSTEM_INSTRUCTIONS = {
    "(1) Standard": None,
    "(2) Smileys": prompts.smileys,
    "(3) Close Friend": prompts.close_friend,
    "(4) Plant": prompts.plant,
    "(5) Spiritual Guide": prompts.spiritual_guide,
    "(6) Wittgenstein": prompts.wittgenstein,
}
DEFAULT_SYSTEM_INSTRUCTION = SYSTEM_INSTRUCTIONS["(1) Standard"]
