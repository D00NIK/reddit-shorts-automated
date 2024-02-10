from utils import *
from html2image import Html2Image
from PIL import Image
from uuid import uuid4
from config import config

hti = Html2Image(output_path=config['TEMP_PATH'])

with open(config['PREVIEW_PATH'], "r") as f:
        previewContent = f.read()

def genPreview(replacements: dict) -> str:
    """
    Generates image preview of a post or a comment, returns path to that file
    """

    content = replaceAll(previewContent, replacements)
    filePath = f"{uuid4()}.png"

    hti.screenshot(html_str=content, save_as=filePath)
    filePath = f"{config['TEMP_PATH']}/{filePath}"

    cropToContent(filePath)

    return filePath

def cropToContent(path) -> None:
    """
    Crops to content of an image as suggested here:
    https://github.com/vgalin/html2image/issues/91#issuecomment-1688750554    
    """

    img = Image.open(path)
    img.crop(img.getbbox()).save(path)
