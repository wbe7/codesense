import tensorflow as tf

print("TensorFlow version:", tf.__version__)
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

if len(tf.config.list_physical_devices('GPU')) > 0:
    print("GPU is available and configured.")
    for gpu in tf.config.list_physical_devices('GPU'):
        print("Name:", gpu.name, "  Type:", gpu.device_type)
    try:
        with tf.device('/GPU:0'):
            a = tf.constant([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
            b = tf.constant([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
            c = tf.matmul(a, b)
            print("GPU calculation successful:\n", c.numpy())
    except RuntimeError as e:
        print("Error performing GPU calculation:", e)
else:
    raise RuntimeError("No GPU devices found. This code requires a GPU.")