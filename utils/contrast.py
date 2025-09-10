from PIL import Image, ImageEnhance
import pandas as pd
from os import getcwd
from os.path import join

def create_document_look(input_path, output_path, contrast_factor=2.0, threshold=140):
    """
    Converts a color image of a stamp into a high-contrast,
    black-and-white document-style image.

    Args:
        input_path (str): The path to the source image file.
        output_path (str): The path to save the processed image file.
        contrast_factor (float): The enhancement factor for contrast.
                                 1.0 is original, >1.0 increases contrast.
        threshold (int): The brightness value (0-255) for binarization.
                         Pixels darker than this become black.
    """
    try:
        # 1. Open the image
        img = Image.open(input_path)
        
        # 2. Convert to grayscale ('L' mode for luminance)
        img_gray = img.convert('L')
        
        # 3. Enhance the contrast
        enhancer = ImageEnhance.Contrast(img_gray)
        img_contrast = enhancer.enhance(contrast_factor)
        
        # 4. Apply a binary threshold to get a pure black and white image
        #    The 'point' method with a lambda function is perfect for this.
        #    Pixels with a value < threshold become 0 (black), others 255 (white).
        #    The mode '1' creates a true 1-bit black and white image.
        img_bw = img_contrast.point(lambda x: 0 if x < threshold else 255, '1')

        # 5. Save the final image
        img_bw.save(output_path)
        
        print(f"✅ Successfully processed '{input_path}' and saved to '{output_path}'")

    except FileNotFoundError:
        print(f"❌ Error: The file '{input_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


PRESENTATION_DIR = join(getcwd(), "presentation")
INPUT_CSV = join(PRESENTATION_DIR, "data", "stamps.csv")
OUTPUT_DIR = join(PRESENTATION_DIR, "data")

if __name__ == "__main__":
    custom_contrast = 2.5
    custom_threshold = 150
    df = pd.read_csv(INPUT_CSV)
    for _, row in list(df.iterrows())[:]:
        fullpath = join(PRESENTATION_DIR, row['path'])
        output_path = fullpath.replace('/stamps/', '/bw-stamps/')
        create_document_look(
            fullpath,
            output_path,
            contrast_factor=custom_contrast,
            threshold=custom_threshold
        )