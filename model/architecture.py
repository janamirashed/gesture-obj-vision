import tensorflow as tf
from tensorflow.keras import layers, models

def create_gesture_model(input_shape = 42, num_classes = 5):

    model = models.Sequential([

        # accepts the 42 normalized landmarks (x, y) coordinates 
        layers.Input(shape=(input_shape,)),

        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3), # turns off neurons during training to avoid overfitting

        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),

        layers.Dense(num_classes, activation='softmax')
    ])

    return model

    # compile & fit in different file to reuse this network without triggering training

if __name__ == "__main__":
    model = create_gesture_model()
    model.summary()


# notes

# softmax activation is used on the final layer instead of linear (logits)
# 1. linear + from_logits=True is slightly more numerically stable during training,
#    but softmax directly outputs normalized probabilities
# 2. returning softmax probabilities directly from model.predict() simplifies backend websocket streaming
#    so the server can pass confidence scores straight to react without manually computing tf.nn.softmax() per frame
