import pandas as pd
import numpy as np
import cv2
import tensorflow as tf

from tensorflow.keras.models import load_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import os


DATASET_PATH = "fer2013.csv"
MODEL_SAVE_PATH = "emotion_model_augmented_weighted.h5" 
CHECKPOINT_PATH = "model_checkpoint_weighted.keras"
IMG_HEIGHT, IMG_WIDTH = 48, 48
NUM_CLASSES = 7
BATCH_SIZE = 64
EPOCHS = 75 

if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(f"Dataset file not found: {DATASET_PATH}")

if not os.path.exists(CHECKPOINT_PATH):
    print(f"Checkpoint file {CHECKPOINT_PATH} not found. Running full training...")
    
    data = pd.read_csv(DATASET_PATH)
    print("Dataset loaded.")
    X = []
    y = []
    print("Processing pixels...")
    for index, row in data.iterrows():
        pixels = np.array(row["pixels"].split(), dtype="float32")
        if pixels.size != IMG_HEIGHT * IMG_WIDTH: continue
        X.append(pixels.reshape(IMG_HEIGHT, IMG_WIDTH))
        y.append(row["emotion"])
    if not X: raise ValueError("No valid data loaded from the CSV file.")
    X = np.array(X)
    y = np.array(y)
    X = X / 255.0
    X = X.reshape(-1, IMG_HEIGHT, IMG_WIDTH, 1)
    y_one_hot = to_categorical(y, num_classes=NUM_CLASSES)
    print(f"Data prepared: X shape={X.shape}, y_one_hot shape={y_one_hot.shape}")
    X_train, X_val, y_train_one_hot, y_val_one_hot, y_train_int, y_val_int = train_test_split(
        X, y_one_hot, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train data: {X_train.shape}, Validation data: {X_val.shape}")
    class_labels = np.unique(y_train_int)
    class_weights_array = compute_class_weight(class_weight='balanced', classes=class_labels, y=y_train_int)
    class_weight_dict = dict(zip(class_labels, class_weights_array))
    print(f"Using Class Weights: {class_weight_dict}")
    train_datagen = ImageDataGenerator( rotation_range=15, width_shift_range=0.1, height_shift_range=0.1, shear_range=0.1, zoom_range=0.1, horizontal_flip=True, fill_mode='nearest' )
    val_datagen = ImageDataGenerator()
    train_generator = train_datagen.flow(X_train, y_train_one_hot, batch_size=BATCH_SIZE)
    validation_generator = val_datagen.flow(X_val, y_val_one_hot, batch_size=BATCH_SIZE)
    print("Data generators created.")
    model = Sequential([ Conv2D(64, (3, 3), activation='relu', padding='same', input_shape=(IMG_HEIGHT, IMG_WIDTH, 1)), BatchNormalization(), MaxPooling2D(2, 2), Conv2D(128, (3, 3), activation='relu', padding='same'), BatchNormalization(), MaxPooling2D(2, 2), Conv2D(256, (3, 3), activation='relu', padding='same'), BatchNormalization(), MaxPooling2D(2, 2), Conv2D(512, (3, 3), activation='relu', padding='same'), BatchNormalization(), MaxPooling2D(2, 2), Flatten(), Dense(256, activation='relu'), BatchNormalization(), Dropout(0.5), Dense(NUM_CLASSES, activation='softmax') ])
    model.summary()
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.0005)
    model.compile(loss="categorical_crossentropy", optimizer=optimizer, metrics=["accuracy"])
    print("Model compiled.")
    early_stopping = EarlyStopping( monitor='val_loss', patience=15, verbose=1, restore_best_weights=False )
    reduce_lr = ReduceLROnPlateau( monitor='val_loss', factor=0.3, patience=7, verbose=1, min_lr=1e-7 )
    model_checkpoint = ModelCheckpoint( filepath=CHECKPOINT_PATH, monitor='val_loss', save_best_only=True, save_weights_only=False, verbose=1 )
    print("Starting training with class weights...")
    history = model.fit( train_generator, steps_per_epoch=len(X_train) // BATCH_SIZE, epochs=EPOCHS, validation_data=validation_generator, validation_steps=len(X_val) // BATCH_SIZE, callbacks=[early_stopping, reduce_lr, model_checkpoint], class_weight=class_weight_dict )
    print("Training finished.")

print(f"Loading best model from checkpoint: {CHECKPOINT_PATH}")
if os.path.exists(CHECKPOINT_PATH):
    try:
       
        best_model = load_model(CHECKPOINT_PATH)
        print("Best model loaded successfully from checkpoint.")
        print(f"Saving loaded best model to HDF5 format: {MODEL_SAVE_PATH}")
        best_model.save(MODEL_SAVE_PATH)
        print(f"Best model saved to {MODEL_SAVE_PATH}")

    except Exception as e:
        print(f"ERROR: Could not load model from checkpoint {CHECKPOINT_PATH} or save to HDF5. Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"ERROR: Checkpoint file {CHECKPOINT_PATH} not found. Cannot load best model.")

try:
    if 'history' in locals(): 
        def plot_history(history):
            acc = history.history['accuracy']
            val_acc = history.history['val_accuracy']
            loss = history.history['loss']
            val_loss = history.history['val_loss']
            epochs_range = range(len(acc))

            plt.figure(figsize=(12, 5))
            plt.subplot(1, 2, 1)
            plt.plot(epochs_range, acc, label='Train Accuracy')
            plt.plot(epochs_range, val_acc, label='Validation Accuracy')
            plt.legend(loc='lower right')
            plt.title('Training and Validation Accuracy')
            plt.xlabel('Epochs')
            plt.ylabel('Accuracy')

            plt.subplot(1, 2, 2)
            plt.plot(epochs_range, loss, label='Train Loss')
            plt.plot(epochs_range, val_loss, label='Validation Loss')
            plt.legend(loc='upper right')
            plt.title('Training and Validation Loss')
            plt.xlabel('Epochs')
            plt.ylabel('Loss')

            plt.tight_layout()
            plt.savefig('training_history_augmented_weighted.png')
            print("Training history plot saved as training_history_augmented_weighted.png")
            # plt.show()
        plot_history(history)
    else:
        print("Skipping plotting history as full training was not run.")
except Exception as e:
    print(f"Could not plot history. Error: {e}")