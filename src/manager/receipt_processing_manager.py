import os
import shutil
from PIL import Image
import io
import base64

from agent.agent_openai_service import AgentOpenAIService
from agent.components.description import RECEIPT_TRACKER_CORRECTER_DESCRIPTION, RECEIPT_TRACKER_DESCRIPTION, TOOLS_DESCRIPTION


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
    and sends the image (with a text prompt) to the LM Studio-compatible vision model.
    Instructs the model to return the tool command it would use without executing it.
    If no tool command was suggested initially, asks explicitly again.
    Moves problematic images to a subdirectory 'problematic_files'.
    """
    agent_service = AgentOpenAIService(tools_description=RECEIPT_TRACKER_DESCRIPTION)

    supported_extensions = ('.jpeg', '.jpg', '.png')
    problematic_dir = os.path.join(folder_path, "problematic_files")
    os.makedirs(problematic_dir, exist_ok=True)

    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(supported_extensions):
            image_path = os.path.join(folder_path, file_name)
            encoded_image = encode_image_to_base64(image_path)

            print(f"Processing receipt: {file_name}")

            full_message, suggested_tool_command = agent_service.chat_with_model(
                user_input_image=encoded_image
            )

            if not suggested_tool_command:
                correction_agent_service = AgentOpenAIService(tools_description=RECEIPT_TRACKER_CORRECTER_DESCRIPTION, model_name="dolphin3.0-qwen2.5-3b")
                full_message, suggested_tool_command = correction_agent_service.chat_with_model(
                    user_input=full_message
                )
               
                if not suggested_tool_command:
                    shutil.copy(image_path, os.path.join(problematic_dir, file_name))
                    print(f"Moved problematic file: {file_name}")

            print(f"Suggested tool command: {suggested_tool_command}\n")
