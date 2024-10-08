import os
from PIL import Image, ImageDraw, ImageFont
from slugify import slugify
import datetime
import requests
from io import BytesIO

# Get image from URL
def get_image(url):
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

# Prepare image
def prepare(home_team, away_team, home_logo_url, away_logo_url, match_date, league_name, league_image):
    # Load the background image
    background_path = "./assets/img/field.png"
    image = Image.open(background_path).convert("RGBA")

    # Initialize drawing context
    draw = ImageDraw.Draw(image)

    # Load font
    font_path = "./assets/fonts/FiraGO-SemiBold.ttf"

    # Draw text with specified position
    def draw_text(draw, text, font_size, center_x, y):
        font = ImageFont.truetype(font_path, font_size)
        (width, height), (offset_x, offset_y) = font.font.getsize(text)
        x_centered = center_x - (width // 2)
        draw.text((x_centered, y), text, fill='white', font=font)

    # Download and resize team logos
    home_logo = get_image(home_logo_url).convert("RGBA")
    away_logo = get_image(away_logo_url).convert("RGBA")
    logo_size = (80, 80)
    home_logo = home_logo.resize(logo_size, Image.LANCZOS)
    away_logo = away_logo.resize(logo_size, Image.LANCZOS)

    # Calculate logo positions
    home_logo_x = 220
    home_logo_y = 206
    away_logo_x = 587
    away_logo_y = 206

    # Paste logos onto the image
    image.paste(home_logo, (home_logo_x, home_logo_y), home_logo)
    image.paste(away_logo, (away_logo_x, away_logo_y), away_logo)

    # Home team name
    draw_text(draw, home_team, 30, home_logo_x + logo_size[0] // 2, home_logo_y + logo_size[1] + 10)

    # Away team name
    draw_text(draw, away_team, 30, away_logo_x + logo_size[0] // 2, away_logo_y + logo_size[1] + 10)

    # Download, resize and position league logo
    league_logo = get_image(league_image).convert("RGBA")
    logo_size = (35, 35)
    league_logo = league_logo.resize(logo_size, Image.LANCZOS)
    league_logo_x = 420
    league_logo_y = 458
    image.paste(league_logo, (league_logo_x, league_logo_y), league_logo)

    # League name
    league_name_x = 420
    league_name_y = 503
    draw_text(draw, league_name, 20, league_name_x + logo_size[0] // 2, league_name_y)

    # Save the image
    current_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    output_directory = "./generated"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    image_path = os.path.join(output_directory, f"{slugify(home_team)}-vs-{slugify(away_team)}-{current_date}.png")
    image.save(image_path)
    return image_path

# Generate image based on API data
def generate(match_id):
    try:
        res = requests.get(f"https://prosoccer.tv/api/fixtures?t=info&id={match_id}")
        res.raise_for_status()
        
        data = res.json()
        match = data.get('data')
        
        if match is None:
            return 'No match data found.'

        home_team = match['teams']['home']['name']
        away_team = match['teams']['away']['name']
        home_logo_url = match['teams']['home']['img']
        away_logo_url = match['teams']['away']['img']
        match_date = match['time']['datetime']
        league_name = match['league']['name']
        league_image = f"https://cdn.soccersapi.com/images/soccer/leagues/50/{match['league']['id']}.png"

        return prepare(home_team, away_team, home_logo_url, away_logo_url, match_date, league_name, league_image)
    except Exception as e:
        return f'An unexpected error occurred: {e}'

# Terminal input
match_id = input('Match ID: ')
if match_id:
    generate(match_id)
else:
    print('No Match ID provided.')