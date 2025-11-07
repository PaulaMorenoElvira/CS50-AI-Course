import cv2
import numpy as np
import os
import sys
import tensorflow as tf # libreria de redes neuronales

from sklearn.model_selection import train_test_split # para dividir el train/test automaticamente

EPOCHS = 10
IMG_WIDTH = 30 #pixels
IMG_HEIGHT = 30
NUM_CATEGORIES = 43 # tenemos 43 tipos de traffic signs
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file so that we can later use it
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    images = []
    labels = []

    # Each category is one of the folders that contains images of the same type
    for category in range(NUM_CATEGORIES):
        # example: gtsrb/0
        category_directory = os.path.join(data_dir, str(category))

        # Verify the directory exists
        if os.path.isdir(category_directory):
            for filename in os.listdir(category_directory):
                # example: gtsrb/0/00000_000000.ppm
                image_path = os.path.join(category_directory, filename)
                
                # Load image using OpenCV
                image = cv2.imread(image_path)
                if image is None:
                    continue # skip unreadable files

                # Resize to target size
                image = cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT)) # convierte todas las imgs en 30x30 pixels
                #image = image / 255.0  # <-- Normaliza la imagen
                
                # Segun avanza el loop vamos llenando las listas de imagenes y labels
                images.append(image)
                labels.append(category)

    print(f" Total imágenes cargadas: {len(images)}")
    print(f" Total labels cargados: {len(labels)}")
    print(f" Clases únicas encontradas: {set(labels)}")

    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    # Primero llamamos el modelo
    model = tf.keras.models.Sequential([

        # Aplicamos las Concolutional layers
        
        # 1st Convolutional layer y 1st pooling layer ( tenemos 32 filtros, cada uno sera un 3x3 kernel)
        # el 3 representa el num de channels como las imagenes son RGB son 3
        tf.keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)), 
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)), # miramos regiones de 2x2 y cogemos el valor mas alto

        # 2nd Convolutional layer and pooling
        tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # 3rd Conv layer (2nd trial)
        tf.keras.layers.Conv2D(128, (3, 3), activation="relu"),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # Flatten the units into a single layer que pasamos a la neural network
        tf.keras.layers.Flatten(),

        # Add hidden layer (con 128 unidades en 1er trial y 256 en el 2o trial)
        tf.keras.layers.Dense(256, activation="relu"),
        tf.keras.layers.Dropout(0.5),  # regularization to prevent overfitting

        # Output layer with 43 units, one for each category that we are classifying
        # The softmax takes the output and turns it into a probability distribution
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])

    # Compile model
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"])

    return model

if __name__ == "__main__":
    main()
