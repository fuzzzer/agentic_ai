import os
from PIL import Image
import io
import base64


from agent.agent_openai_service import AgentOpenAIService
from agent.components.description import RECEIPT_TRACKER_DESCRIPTION
from agent.simple_tool_user_service import SimpleToolUserService

def encode_image_to_base64(image_path: str) -> str:
    """Encodes an image file to a base64 string."""
    with Image.open(image_path) as img:
        buffered = io.BytesIO()
        img_format = img.format if img.format is not None else "JPEG"
        img.save(buffered, format=img_format)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

def process_receipts_folder(folder_path: str):
    """
    Iterates over image files in the specified folder, resets the conversation history for each image,
    and sends the image (with a text prompt) to LM Studio-compatible vision model.
    """
    agent_service = AgentOpenAIService(tools_description=RECEIPT_TRACKER_DESCRIPTION)

    supported_extensions = ('.jpeg', '.jpg', '.png')

    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(supported_extensions):
            image_path = os.path.join(folder_path, file_name)
            encoded_image = encode_image_to_base64(image_path)

            print(f"Processing receipt: {file_name}")
            answer = agent_service.chat_with_model(user_input_image=encoded_image)
            print(f"AI response for {file_name}:\n{answer}\n")

