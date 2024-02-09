from utils import *
from html2image import Html2Image
from PIL import Image
import uuid

TEMP_PATH = "tmp"
POST_PREVIEW_PATH = "previews/post.html"
COMMENT_PREVIEW_PATH = "previews/comment.html"

hti = Html2Image(output_path=TEMP_PATH)

with open(POST_PREVIEW_PATH, "r") as f:
        postContent = f.read()

with open(COMMENT_PREVIEW_PATH, "r") as f:
        commentContent = f.read()

# Generates image preview of a post or a comment, returns path to that file
def genPreview(replacements: dict, isPost: bool = False) -> str:
    content = replaceAll(postContent if isPost else commentContent, replacements)
    filePath = str(uuid.uuid4()) + ".png"

    hti.screenshot(html_str=content, save_as=filePath)
    filePath = TEMP_PATH + '/' + filePath

    cropToContent(filePath)

    return filePath

# As suggested here https://github.com/vgalin/html2image/issues/91#issuecomment-1688750554
def cropToContent(path) -> None:
    img = Image.open(path)
    img.crop(img.getbbox()).save(path)
