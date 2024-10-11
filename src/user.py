import requests
import base64
from datetime import datetime, timedelta
import google.generativeai as genai
import config


class User:
    def __init__(self, phone_number, default_system_instruction, default_model):
        self.phone_number = phone_number
        self.current_system_instruction = default_system_instruction
        self.current_model = default_model
        self.trusted = phone_number in config.TRUSTED_PHONE_NUMBERS
        self.last_activity = None
        self.chat_session = None
        self.image_size = config.DEFAULT_IMAGE_SIZE

    def is_session_inactive(self, timeout=config.SESSION_TIMEOUT):
        if self.last_activity is None:
            return True
        return datetime.now() - self.last_activity > timedelta(minutes=timeout)

    def reset_session(self):
        self.chat_session = None

    def get_or_create_chat_session(self):
        if self.chat_session is None or self.is_session_inactive():
            model_name = self.current_model.split(" ")[1]
            if self.current_system_instruction is None:
                model = genai.GenerativeModel(model_name=model_name)
            else:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=self.current_system_instruction,
                )
            self.chat_session = model.start_chat(history=[])
            self.last_activity = datetime.now()
        return self.chat_session

    def set_model(self, model_name):
        self.current_model = model_name
        self.reset_session()

    def set_system_instruction(self, system_instruction):
        self.current_system_instruction = system_instruction
        self.reset_session()

    def set_image_size(self, size):
        self.image_size = size

    def send_message(self, content, attachment=None):
        url = f"{config.HTTP_BASE_URL}/v2/send"
        payload = {
            "number": config.SIGNAL_PHONE_NUMBER,
            "recipients": [self.phone_number],
        }
        if isinstance(content, str):
            payload["message"] = content
        if attachment:
            encoded = base64.b64encode(attachment).decode("utf-8")
            payload["base64_attachments"] = [encoded]
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            print(f"Message sent successfully to {self.phone_number}")
        except requests.RequestException as e:
            print(f"Error sending message: {e}")
