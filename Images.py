import os, pygame
IMAGES = {}

def load_images():
    """
    Load all .png images from /Images into a dictionary
    """
    global IMAGES
    image_dir = os.path.join(os.getcwd(), 'Images')
    for file in os.listdir(image_dir):
        if file.endswith('.png'):
            key = file[:-4].upper()
            IMAGES[key] = pygame.image.load(os.path.join(image_dir, file)).convert_alpha()

