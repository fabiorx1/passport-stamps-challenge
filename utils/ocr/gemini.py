from google import genai
from google.genai import types
from PIL import Image
import pandas as pd, mimetypes
from os import getcwd, getenv
from os.path import join
from dotenv import load_dotenv
from time import sleep

load_dotenv()
API_KEY = getenv('GENAI_API_KEY')
PRESENTATION_DIR = join(getcwd(), "presentation")
INPUT_CSV = join(PRESENTATION_DIR, "data", "stamps.csv")
OUTPUT_DIR = join(PRESENTATION_DIR, "data")

def main(col: str = 'GEM.FLASH2.5'):
    client = genai.Client(api_key=API_KEY)
    df = pd.read_csv(INPUT_CSV)
    if col not in df.columns: df[col] = pd.Series(dtype=str)
    idx, max_idx = 0, 100
    while idx < max_idx:
        row = df.iloc[idx]
        print(f'{idx}/{len(df)} {row["path"].split("/")[-1]}')
        path = row["path"]
        mime_type, _ = mimetypes.guess_type(path.split("/")[-1])
        with open(join(PRESENTATION_DIR, path), 'rb') as f: image_bytes = f.read()
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    'This is a photo of a passport visa stamp. You should find and extract the date of this stamp.'
                    'Dates are usually in the center and can be presented in any format.'
                    'You should also classify it between entry stamp, exit stamp or general stamp based on the words read context.'
                    'Return it as a tuple: (Date, Classification)'])
            text = response.text
            print('\tTEXT:', text)
            df.at[idx, col] = text
        except Exception as e:
            print('Ocorreu um erro com o Gemini.', e)
            sleep(5)
            idx -= 1
        finally:
            sleep(5)
            idx += 1
        df.to_csv(INPUT_CSV, index=False)

if __name__ == "__main__":
    main()
    # df = pd.read_csv(INPUT_CSV)
    # genai = df['GEM.FLASH2.5'].to_list()
    # df = df.drop(index=len(df)-1)
    # df['GEM.FLASH2.5'] = genai[1:]
    # df.to_csv(INPUT_CSV, index=False)