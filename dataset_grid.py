import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")           
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import confusion_matrix, classification_report

# ── 1. Config 
MODEL_PATH       = "backend/efficientnet_b0_101_best.h5"   
CLASS_NAMES_PATH = "backend/class_names.json"              # list of 101 class strings
FOOD101_TEST_DIR = "food-101/images"         
                                                   
TEST_SPLIT_FILE  = "food-101/meta/test.txt"   # food101 test split list
IMG_SIZE         = (224, 224)
BATCH_SIZE       = 64
OUTPUT_DIR       = "."

# Load model and class names 
print("Loading model...")
model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_NAMES_PATH) as f:
    CLASS_NAMES = json.load(f)   # list of 101 strings e.g. ["apple_pie", "baby_back_ribs", ...]

print(f"Model loaded. Classes: {len(CLASS_NAMES)}")

# Build test dataset from food101 test split 
#
# Food-101 structure:
#   data/food-101/images/<class_name>/<image_id>.jpg
#
# test.txt contains lines like: "apple_pie/1011328"
#
print("Building test dataset...")

preprocess = tf.keras.applications.efficientnet.preprocess_input

def load_and_preprocess(path):
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    img = tf.image.resize(img, IMG_SIZE)
    img = preprocess(tf.cast(img, tf.float32))
    return img

# Read test split
with open(TEST_SPLIT_FILE) as f:
    test_items = [line.strip() for line in f if line.strip()]

# Build (path, label_index) pairs
image_paths = []
true_labels = []

for item in test_items:
    class_name = item.split("/")[0]
    if class_name not in CLASS_NAMES:
        continue
    label_idx = CLASS_NAMES.index(class_name)
    img_path  = os.path.join(FOOD101_TEST_DIR, item + ".jpg")
    if os.path.exists(img_path):
        image_paths.append(img_path)
        true_labels.append(label_idx)

print(f"Test images found: {len(image_paths)}")

# Build tf.data pipeline
image_paths_tensor = tf.constant(image_paths, dtype=tf.string)
path_ds  = tf.data.Dataset.from_tensor_slices(image_paths_tensor)
img_ds   = path_ds.map(load_and_preprocess, num_parallel_calls=tf.data.AUTOTUNE)
test_ds  = img_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

# Run inference 
print("Running inference (this may take a few minutes)...")
all_probs = model.predict(test_ds, verbose=1)
pred_labels = np.argmax(all_probs, axis=1)
true_labels = np.array(true_labels)

# Compute metrics 
print("\nClassification Report (first 20 classes):")
print(classification_report(
    true_labels[:5000], pred_labels[:5000],
    target_names=[CLASS_NAMES[i] for i in range(20)]
))

overall_acc = np.mean(pred_labels == true_labels)
print(f"\nOverall Test Accuracy: {overall_acc*100:.2f}%")

# Full 101×101 Confusion Matrix 
print("\nComputing confusion matrix...")
cm = confusion_matrix(true_labels, pred_labels, labels=list(range(len(CLASS_NAMES))))
cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)   # row-normalise

fig, ax = plt.subplots(figsize=(28, 24))
sns.heatmap(
    cm_norm,
    ax=ax,
    cmap="RdYlGn",             # red = low, green = high
    vmin=0.0, vmax=1.0,
    xticklabels=[c.replace("_", "\n") for c in CLASS_NAMES],
    yticklabels=[c.replace("_", "\n") for c in CLASS_NAMES],
    linewidths=0.0,
    cbar_kws={"label": "Recall (fraction of true class predicted correctly)"},
    square=True,
)
ax.set_xlabel("Predicted Class", fontsize=11, labelpad=10)
ax.set_ylabel("True Class",      fontsize=11, labelpad=10)
ax.set_title(
    f"Normalised Confusion Matrix — EfficientNet-B0 on Food-101 Test Set\n"
    f"Overall Accuracy: {overall_acc*100:.2f}%",
    fontsize=13, pad=15
)
ax.tick_params(axis="both", labelsize=5.5)
plt.tight_layout()
out_path = os.path.join(OUTPUT_DIR, "confusion_matrix_heatmap.png")
fig.savefig(out_path, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {out_path}")

# Find the 20 off-diagonal cells with the highest normalised confusion rate
print("\nFinding top-20 confused pairs...")
cm_copy = cm_norm.copy()
np.fill_diagonal(cm_copy, 0)       # zero out diagonal (correct predictions)

# Flatten, sort, pick top-20
flat_indices = np.dstack(np.unravel_index(
    np.argsort(cm_copy.ravel())[::-1], cm_copy.shape
))[0]
top20 = flat_indices[:20]

labels_top20 = [
    f"{CLASS_NAMES[t].replace('_',' ').title()} →\n{CLASS_NAMES[p].replace('_',' ').title()}"
    for t, p in top20
]
values_top20 = [cm_copy[t, p] for t, p in top20]

# Colour by severity
colours = plt.cm.RdYlGn_r(np.linspace(0.1, 0.9, len(values_top20)))

fig2, ax2 = plt.subplots(figsize=(12, 8))
bars = ax2.barh(
    range(len(labels_top20)),
    values_top20,
    color=colours,
    edgecolor="white",
    linewidth=0.5,
)
ax2.set_yticks(range(len(labels_top20)))
ax2.set_yticklabels(labels_top20, fontsize=8.5)
ax2.invert_yaxis()
ax2.set_xlabel("Confusion Rate (fraction of true class predicted as shown class)", fontsize=10)
ax2.set_title(
    "Top-20 Most Confused Class Pairs — EfficientNet-B0 on Food-101",
    fontsize=12, pad=12
)
ax2.set_xlim(0, max(values_top20) * 1.15)
for bar, val in zip(bars, values_top20):
    ax2.text(
        bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
        f"{val*100:.1f}%", va="center", fontsize=8
    )
ax2.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
out_path2 = os.path.join(OUTPUT_DIR, "confusion_matrix_top20.png")
fig2.savefig(out_path2, dpi=200, bbox_inches="tight")
plt.close(fig2)
print(f"Saved: {out_path2}")

# Per-class accuracy bar chart (bonus) 
per_class_acc = cm_norm.diagonal()
sorted_idx    = np.argsort(per_class_acc)

fig3, ax3 = plt.subplots(figsize=(22, 8))
bar_colours = plt.cm.RdYlGn(per_class_acc[sorted_idx])
ax3.bar(
    range(len(CLASS_NAMES)),
    per_class_acc[sorted_idx] * 100,
    color=bar_colours,
    width=0.85,
    edgecolor="none",
)
ax3.set_xticks(range(len(CLASS_NAMES)))
ax3.set_xticklabels(
    [CLASS_NAMES[i].replace("_", "\n") for i in sorted_idx],
    fontsize=4.5, rotation=90
)
ax3.set_ylabel("Per-Class Accuracy (%)", fontsize=11)
ax3.set_title(
    f"Per-Class Test Accuracy — EfficientNet-B0 on Food-101 "
    f"(Mean: {per_class_acc.mean()*100:.2f}%)",
    fontsize=12, pad=12
)
ax3.set_ylim(0, 110)
ax3.axhline(per_class_acc.mean() * 100, color="navy", linestyle="--",
            linewidth=1.2, label=f"Mean = {per_class_acc.mean()*100:.2f}%")
ax3.legend(fontsize=9)
ax3.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
out_path3 = os.path.join(OUTPUT_DIR, "per_class_accuracy.png")
fig3.savefig(out_path3, dpi=200, bbox_inches="tight")
plt.close(fig3)
print(f"Saved: {out_path3}")

print("\n✅ All figures saved successfully.")
print("Use confusion_matrix_heatmap.png  → full 101×101 matrix for paper")
print("Use confusion_matrix_top20.png    → cleaner top-20 confused pairs")
print("Use per_class_accuracy.png        → sorted per-class bar chart")