from PIL import Image, ImageDraw, ImageFont
import os


class ImageCreator:
    LOGO_PADDING_TOP = 50
    LOGO_FIRST_X = 200
    LOGO_SECOND_X = 1300
    TEXT_START_Y = 1100

    def __init__(self, background_path: str, hometeam_logo_path: str, home_team_name: str):
        """Initialize paths and set the font path relative to the script location."""
        self.background_path = os.path.join(os.path.dirname(__file__), background_path)
        self.hometeam_logo_path = os.path.join(os.path.dirname(__file__), hometeam_logo_path)
        self.font_path = os.path.join(os.path.dirname(__file__), "images", "SFMonoRegular.otf")
        self.home_team_name = home_team_name

    def load_image(self, path: str) -> Image:
        """Load an image from the specified file path and handle exceptions."""
        try:
            return Image.open(path)
        except FileNotFoundError as e:
            print(f"Error loading image from {path}: {e}")
            return None

    def find_opponent_logo(self, opponent: str, image_map: dict):
        """Determine the opponent logo and title based on the first line of text."""
        for keywords, (image_name, opponent_name) in image_map.items():
            if any(keyword in opponent.lower() for keyword in keywords):
                return image_name, opponent_name
        return None, None

    def adjust_font_size(self, draw, text: str, font, image_width: int):
        """Adjust font size to ensure the text fits within the specified width."""
        text_width, _ = draw.textsize(text, font=font)
        while text_width > image_width and font.size > 10:
            font = ImageFont.truetype(self.font_path, font.size - 5)
            text_width, _ = draw.textsize(text, font=font)
        return font

    def create_image(self, text: str, image_map: dict, league: str):
        background = self.load_image(self.background_path)
        hometeam_logo = self.load_image(self.hometeam_logo_path)
        if not background or not hometeam_logo:
            print("Couldn't load club logo and/or background.")
            return None

        first_line = text.split('\n')[0]
        opponent = first_line.split('-')[1]
        opponent_logo_name, opponent_name = self.find_opponent_logo(opponent, image_map)
        opponent_found = True
        if not opponent_logo_name:
            print("Couldn't find opposing team in image_map.")
            opponent_found = False

        if opponent_found:
            opponent_logo_path = os.path.join(os.path.dirname(__file__), "images", opponent_logo_name)
            opponent_logo = self.load_image(opponent_logo_path)

            background.paste(hometeam_logo, (self.LOGO_FIRST_X, self.LOGO_PADDING_TOP), hometeam_logo)
            background.paste(opponent_logo, (self.LOGO_SECOND_X, self.LOGO_PADDING_TOP), opponent_logo)

            lines = text.split('\n')
            lines[0] = f"{self.home_team_name} - {opponent_name}, {league}"
            text = '\n'.join(lines)
        else:
            background.paste(hometeam_logo, (int((background.width - hometeam_logo.width) / 2), self.LOGO_PADDING_TOP), hometeam_logo)

        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype(self.font_path, 100)
        font = self.adjust_font_size(draw, text, font, background.width)
        text_width, _ = draw.textsize(text, font=font)
        text_position = ((background.width - text_width) / 2, self.TEXT_START_Y)
        draw.text(text_position, text, font=font, fill="white")

        return background

    def save_image(self, image, path: str):
        try:
            savepath = os.path.join(os.path.dirname(__file__), path)
            image.save(savepath)
            print(f"Image saved to {path}")
            return savepath
        except Exception as e:
            print(f"Error saving image to {path}: {e}")
            return None
