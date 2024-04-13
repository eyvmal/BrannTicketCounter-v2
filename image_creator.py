from PIL import Image, ImageDraw, ImageFont
import os


class ImageCreator:
    LOGO_PADDING_TOP = 50
    LOGO_BRANN_X = 200
    LOGO_SECOND_X = 1300
    TEXT_START_Y = 1100

    def __init__(self, background_path: str, brann_logo_path: str):
        """Initialize paths and set the font path relative to the script location."""
        self.background_path = os.path.join(os.path.dirname(__file__), background_path)
        self.brann_logo_path = os.path.join(os.path.dirname(__file__), brann_logo_path)
        self.font_path = os.path.join(os.path.dirname(__file__), "images", "SFMonoRegular.otf")

    def load_image(self, path: str) -> Image:
        """Load an image from the specified file path and handle exceptions."""
        try:
            return Image.open(path)
        except FileNotFoundError as e:
            print(f"Error loading image from {path}: {e}")
            return None

    def find_second_logo(self, first_line: str, image_map: dict) -> tuple:
        """Determine the second logo and title based on the first line of text."""
        for keywords, (image_name, title) in image_map.items():
            if any(keyword in first_line.lower() for keyword in keywords):
                return image_name, title
        return None, None

    def adjust_font_size(self, draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont,
                         image_width: int) -> ImageFont.FreeTypeFont:
        """Adjust font size to ensure the text fits within the specified width."""
        text_width, _ = draw.textsize(text, font=font)
        while text_width > image_width and font.size > 10:
            font = ImageFont.truetype(self.font_path, font.size - 5)
            text_width, _ = draw.textsize(text, font=font)
        return font

    def create_image(self, text: str, image_map: dict, league: str) -> Image:
        background = self.load_image(self.background_path)
        brann_logo = self.load_image(self.brann_logo_path)
        if not background or not brann_logo:
            return None

        first_line = text.split('\n')[0]
        second_logo_name, title = self.find_second_logo(first_line, image_map)
        if not second_logo_name:
            print("No matching keyword found in the first line.")
            return None

        lines = text.split('\n')
        lines[0] = f"{title}, {league}"
        text = '\n'.join(lines)

        second_logo_path = os.path.join(os.path.dirname(__file__), "images", second_logo_name)
        second_logo = self.load_image(second_logo_path)
        if not second_logo:
            return None

        background.paste(brann_logo, (self.LOGO_BRANN_X, self.LOGO_PADDING_TOP), brann_logo)
        background.paste(second_logo, (self.LOGO_SECOND_X, self.LOGO_PADDING_TOP), second_logo)

        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype(self.font_path, 100)
        font = self.adjust_font_size(draw, text, font, background.width)
        text_width, _ = draw.textsize(text, font=font)
        text_position = ((background.width - text_width) / 2, self.TEXT_START_Y)
        draw.text(text_position, text, font=font, fill="white")

        return background

    def save_image(self, image: Image.Image, path: str) -> str | None:
        try:
            savepath = os.path.join(os.path.dirname(__file__), path)
            image.save(savepath)
            print(f"Image saved to {path}")
            return savepath
        except Exception as e:
            print(f"Error saving image to {path}: {e}")
            return None
