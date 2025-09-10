import os, pandas as pd
from os.path import join
from PIL import Image
from transformers import pipeline

PRESENTATION_DIR = join(os.getcwd(), "presentation")
INPUT_CSV = join(PRESENTATION_DIR, "data", "stamps.csv")
OUTPUT_DIR = join(PRESENTATION_DIR, "data")
MS_COL, MS_MODEL = 'MS/TROCR/PRINTED', "microsoft/trocr-base-printed"
MS_COL2, MS_MODEL2 = 'MS/TROCR/HNDWRTN', "microsoft/trocr-base-handwritten"
MS_COL3, MS_MODEL3 = 'MS/TROCR/STG1', "microsoft/trocr-base-stage1"

def main(col: str, model: str):
    pipe = pipeline("image-to-text", model=model)
    df = pd.read_csv(INPUT_CSV)
    df[col] = pd.Series(dtype=str)
    for idx, row in list(df.iterrows())[50:]:
        path = row["PROCESSED IMG"]
        image = Image.open(join(PRESENTATION_DIR, path))
        image = image.convert("RGB")
        text = pipe.predict(image)
        print(f'{idx}/{len(df)} {row["path"].split("/")[-1]}')
        print('\tOUTPUT:', text)
        text = [part['generated_text'] for part in text]
        text = " ".join(text)
        print('\tTEXT:', text)
        df.at[idx, col] = text
    df.to_csv(join(OUTPUT_DIR, "stamps.csv"), index=False)

def show_filled_rows(col: str):
    df = pd.read_csv(join(OUTPUT_DIR, "stamps.csv"))
    df = df[df[col].notna()]
    print(df.head())

if __name__ == "__main__":
    main('TROCR/PRINTED PROCESSED', MS_MODEL)
    # df = pd.read_csv(INPUT_CSV)
    # df['PROCESSED IMG'] = df['path'].apply(lambda x: x.replace('/stamps/', '/bw-stamps/'))
    # df.to_csv(INPUT_CSV, index=False)
    # models = [(MS_COL, MS_MODEL), (MS_COL2, MS_MODEL2), (MS_COL3, MS_MODEL3)]
    # for column, model in models:
    #     main(column, model)