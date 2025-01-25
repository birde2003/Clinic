from PIL import Image, ImageDraw
import os

# Create icons directory if needed
os.makedirs('icons', exist_ok=True)

# Common settings
icon_size = (64, 64)
background_color = (255, 255, 255, 0)  # Transparent
text_color = (0, 0, 0)

def create_icon(name, symbol):
    img = Image.new('RGBA', icon_size, background_color)
    d = ImageDraw.Draw(img)
    
    # Draw symbol in center
    d.text((32,32), symbol, fill=text_color, anchor="mm", font_size=24)
    
    img.save(f'icons/{name}.png')

# Generate basic icons
create_icon('add', '+')
create_icon('edit', '✎')
create_icon('delete', '✖')
create_icon('print', '⎙')
create_icon('save', '💾')
