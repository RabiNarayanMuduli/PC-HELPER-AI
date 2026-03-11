#
# from huggingface_hub import InferenceClient
# from PIL import Image
#
# # 🔐 Paste your NEW token here
# client = InferenceClient(
#     model="Salesforce/blip-image-captioning-base",
#     token="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"
# )
#
# def analyze_image(image_path):
#     try:
#         image = Image.open(image_path)
#
#         result = client.image_to_text(image)
#
#         if isinstance(result, list):
#             return result[0]["generated_text"]
#
#         return str(result)
#
#     except Exception as e:
#         return f"Error: {str(e)}"
from huggingface_hub import InferenceClient
from PIL import Image
import traceback

client = InferenceClient(
    model="Salesforce/blip-image-captioning-base",
    token="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"
)

def analyze_image(image_path):
    try:
        image = Image.open(image_path)

        result = client.image_to_text(image)

        print("RAW RESULT:", result)

        if isinstance(result, list):
            return result[0]["generated_text"]

        return str(result)

    except Exception as e:
        print("FULL ERROR:")
        traceback.print_exc()
        return "Image analysis failed. Check terminal."
