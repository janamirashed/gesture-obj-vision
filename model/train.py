import os
import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from architecture import create_gesture_model

# paths for processed data, model saving, and plots
processed_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
saved_model_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
plots_dir = os.path.join(os.path.dirname(__file__), 'plots')

# create directories if they don't exist
os.makedirs(saved_model_dir, exist_ok=True)
os.makedirs(plots_dir, exist_ok=True)

def main():
    print("\n--- starting model training ---")

    # load processed training data (x: 42 landmarks per sample, y: integer class label 0-4)
    landmarks_csv = os.path.join(processed_dir, 'landmarks.csv')
    labels_csv = os.path.join(processed_dir, 'labels.csv')
    X = pd.read_csv(landmarks_csv).values
    y = pd.read_csv(labels_csv).values.ravel() # flattens 2d array to 1d for target labels
 
    # split dataset into train and validation sets (20% for validation)
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"dataset split: {X_train.shape[0]} training samples, {X_val.shape[0]} validation samples")

    # build and compile neural network architecture
    model = create_gesture_model(input_shape=42, num_classes=5)
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # early stopping callback halts training if val_loss doesn't improve for 5 epochs
    # (prevents overfitting by restoring weights from the best performing epoch)
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss', 
        patience=5, 
        restore_best_weights=True
    )

    # train model using mini-batch gradient descent (batch size 32)
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=30,
        batch_size=32,
        callbacks=[early_stop]
    )

    # evaluate final trained model on unseen validation dataset
    val_loss, val_acc = model.evaluate(X_val, y_val)
    print(f"\nfinal validation accuracy: {val_acc * 100:.2f}%")

    # save trained model to disk for backend inference
    model_save_path = os.path.join(saved_model_dir, 'gesture_classifier.keras')
    model.save(model_save_path)
    print(f"model saved to: {model_save_path}")

    # plot and save accuracy / loss curves to model/plots/
    plt.figure(figsize=(12, 4))

    # plot accuracy
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='train accuracy')
    plt.plot(history.history['val_accuracy'], label='val accuracy')
    plt.title('model accuracy')
    plt.xlabel('epoch')
    plt.ylabel('accuracy')
    plt.legend()

    # plot loss
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='train loss')
    plt.plot(history.history['val_loss'], label='val loss')
    plt.title('model loss')
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.legend()

    plot_path = os.path.join(plots_dir, 'training_history.png')
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    print(f"training history plot saved to: {plot_path}\n")

if __name__ == '__main__':
    main()

# notes

# 1. stratify=y preserves exact class distribution across splits:
#    without stratify, random splitting might put 95% of a gesture (e.g. fist) into training 
#    and only 5% into validation, causing an unbalanced evaluation set.
#    stratify=y guarantees every class maintains the exact same 80% train / 20% validation ratio.

# 2. early stopping monitors val_loss:
#    if val_loss stops improving for 5 consecutive epochs, training halts automatically
#    and restore_best_weights=True reloads weights from the peak epoch (lowest val_loss)

# 3. model.save('gesture_classifier.keras'):
#    saves trained architecture and 14,085 learned weights so backend loads it for instant real-time predictions
