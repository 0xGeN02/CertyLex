"""
    Model test for TensorFlow models and dependencies and cpp23 compatibility.
"""

import os
import tensorflow as tf
# Suppress TensorFlow GPU warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def test_tensorflow_installation():
    """
    Test TensorFlow installation by creating a simple computation graph.
    """
    try:
        a = tf.constant(5)
        b = tf.constant(3)
        c = tf.add(a, b)
        print(f"TensorFlow addition result: {c.numpy()}")
        print("TensorFlow installation is working correctly.")
    except Exception as e:
        print(f"TensorFlow installation test failed: {e}")

def test_model(model, test_dataset, threshold=0.9):
    """
    Test a TensorFlow model on a given test dataset.

    Parameters:
        model (tf.keras.Model): The TensorFlow model to test.
        test_dataset (tf.data.Dataset): Dataset for testing the model.
        threshold (float): The accuracy threshold to determine success.

    Returns:
        float: The accuracy of the model on the test dataset.
        bool: Whether the test passed the accuracy threshold.
    """
    # Evaluate the model
    loss, accuracy = model.evaluate(test_dataset)
    print(f"Test Loss: {loss:.4f}, Test Accuracy: {accuracy:.4f}")

    # Check if accuracy meets the threshold
    return accuracy, accuracy >= threshold

if __name__ == "__main__":
    # Example usage
    import sys
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Flatten
    from tensorflow.keras.datasets import mnist

    # Load MNIST dataset for testing
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_test = x_test.astype('float32') / 255.0  # Normalize the data

    # Create a simple model for demonstration purposes
    tf_model = Sequential([
        Flatten(input_shape=(28, 28)),
        Dense(128, activation='relu'),
        Dense(10, activation='softmax')
    ])

    # Compile the model
    tf_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Train the model on the training dataset
    x_train = x_train.astype('float32') / 255.0  # Normalize the data
    train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train)).batch(32)
    tf_model.fit(train_dataset, epochs=5)

    # Create a test dataset
    test_data = tf.data.Dataset.from_tensor_slices((x_test, y_test)).batch(32)

    # Test TensorFlow installation and model accuracy
    test_tensorflow_installation()
    acc, passed = test_model(tf_model, test_data)
    print(f"Model accuracy: {acc:.2f}, Passed: {passed}")
    sys.exit(0 if passed else 1)
