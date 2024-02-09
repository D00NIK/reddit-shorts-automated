from utils import *
from html2image import Html2Image
from PIL import Image
from uuid import uuid4
from config import config

hti = Html2Image(output_path=config['TEMP_PATH'])

with open(config['PREVIEW_PATH'], "r") as f:
        previewContent = f.read()

# Generates image preview of a post or a comment, returns path to that file
def genPreview(replacements: dict) -> str:
    content = replaceAll(previewContent, replacements)
    filePath = f"{uuid4()}.png"

    hti.screenshot(html_str=content, save_as=filePath)
    filePath = f"{config['TEMP_PATH']}/{filePath}"

    cropToContent(filePath)

    return filePath

# As suggested here https://github.com/vgalin/html2image/issues/91#issuecomment-1688750554
def cropToContent(path) -> None:
    img = Image.open(path)
    img.crop(img.getbbox()).save(path)
