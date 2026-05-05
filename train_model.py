import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2  # type: ignore
from tensorflow.keras import layers, models # pyright: ignore[reportMissingModuleSource]
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping # pyright: ignore[reportMissingModuleSource]
import matplotlib.pyplot as plt

IMG_SIZE   = 224
BATCH_SIZE = 32
EPOCHS     = 10
DATA_DIR   = 'food-101/images'

SELECTED_CLASSES = [
    'pizza', 'hamburger', 'sushi', 'ice_cream',
    'fried_rice', 'omelette', 'pancakes',
    'samosa', 'cup_cakes', 'caesar_salad'
]

datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=20,
    zoom_range=0.2,
    horizontal_flip=True
)

print("Loading training data...")
train_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    subset='training',
    classes=SELECTED_CLASSES,
    class_mode='categorical'
)

print("Loading validation data...")
val_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    subset='validation',
    classes=SELECTED_CLASSES,
    class_mode='categorical'
)

print(f"Training samples   : {train_gen.samples}")
print(f"Validation samples : {val_gen.samples}")

base_model = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.4),
    layers.Dense(len(SELECTED_CLASSES), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

checkpoint = ModelCheckpoint(
    'food_model.h5',
    monitor='val_accuracy',
    save_best_only=True,
    verbose=1
)

early_stop = EarlyStopping(
    monitor='val_accuracy',
    patience=3,
    verbose=1,
    restore_best_weights=True
)

print("\nStarting training...")
history = model.fit(
    train_gen,
    epochs=EPOCHS,
    validation_data=val_gen,
    callbacks=[checkpoint, early_stop]
)

model.save('food_model.h5')
print("Model saved as food_model.h5")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(history.history['accuracy'],     label='Train Accuracy')
ax1.plot(history.history['val_accuracy'], label='Val Accuracy')
ax1.set_title('Model Accuracy')
ax1.set_xlabel('Epoch')
ax1.legend()

ax2.plot(history.history['loss'],     label='Train Loss')
ax2.plot(history.history['val_loss'], label='Val Loss')
ax2.set_title('Model Loss')
ax2.set_xlabel('Epoch')
ax2.legend()

plt.tight_layout()
plt.savefig('training_graphs.png')
print("Graphs saved as training_graphs.png")
print("\nAll done!")