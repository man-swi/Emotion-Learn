import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

DATASET_PATH = "fer2013.csv"
SAD_LABEL = 4 
NUM_IMAGES_TO_VIEW = 25

if not os.path.exists(DATASET_PATH):
    print(f"Dataset file not found: {DATASET_PATH}")
else:
    print(f"Loading {DATASET_PATH} to view 'Sad' images...")
    data = pd.read_csv(DATASET_PATH)

  
    sad_data = data[data['emotion'] == SAD_LABEL]

    if sad_data.empty:
        print(f"No images found with label {SAD_LABEL} (Sad). Check the label number.")
    else:
        print(f"Found {len(sad_data)} images labeled as Sad. Displaying a sample...")
        # Take a random sample
        sample_indices = np.random.choice(sad_data.index, min(NUM_IMAGES_TO_VIEW, len(sad_data)), replace=False)
        sample_sad_data = sad_data.loc[sample_indices]

        # Determine grid size for plotting
        cols = 5
        rows = int(np.ceil(len(sample_sad_data) / cols))
        plt.figure(figsize=(cols * 2, rows * 2)) # Adjust figure size as needed

        for i, (index, row) in enumerate(sample_sad_data.iterrows()):
            pixels = np.array(row['pixels'].split(), dtype='float32')
            img = pixels.reshape(48, 48)

            plt.subplot(rows, cols, i + 1)
            plt.imshow(img, cmap='gray')
            plt.title(f"Sad (Index: {index})")
            plt.axis('off')

        plt.tight_layout()
        plt.suptitle(f"Sample 'Sad' Images (Label {SAD_LABEL}) from {DATASET_PATH}", y=1.02)
        plt.show() 
