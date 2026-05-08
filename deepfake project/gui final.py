import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageDraw
import numpy as np
from mtcnn import MTCNN
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

# Initialize MTCNN detector
detector = MTCNN()

# Load the pre-trained MobileNet model
def build_mobilenet_model():
    model1 = keras.applications.MobileNet(input_shape=(224, 224, 3), weights="imagenet")
    model1.trainable = True
    inputs = Input(shape=(224, 224, 3))
    model = Sequential([
        inputs,
        model1,
        layers.Dense(1024, activation='relu'),
        layers.BatchNormalization(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dense(2, activation='softmax')
    ])
    return model

# Load the pre-trained InceptionNet model
def build_inception_model():
    inputs = Input(shape=(224, 224, 3))
    inception = keras.applications.InceptionV3(
        weights='imagenet',
        include_top=False,
        input_tensor=inputs
    )
    model = Sequential([
        inputs,
        inception,
        layers.GlobalAveragePooling2D(),
        layers.Dense(1024, activation='relu'),
        layers.BatchNormalization(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dense(2, activation='softmax')
    ])
    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

# Load the pre-trained ResNet model
def build_resnet_model():
    inputs = Input(shape=(224, 224, 3))
    resnet = keras.applications.ResNet50(
        weights='imagenet',
        include_top=False,
        input_tensor=inputs
    )
    model = Sequential([
            inputs,
            resnet,
            layers.GlobalAveragePooling2D(),
            layers.Dense(1024, activation='relu'),
            layers.BatchNormalization(),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dense(2, activation='softmax')
        ])
    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

# Global variables for the selected model
current_model = None
current_model_name = None

# Function to load the selected model
def load_model(model_name):
    global current_model, current_model_name
    if model_name == "MobileNet V3":
        current_model = build_mobilenet_model()
        current_model.load_weights("mobilenet_model/mobilenet.h5")  # Update the path to your MobileNet weights file
    elif model_name == "ResNet":
        current_model = build_resnet_model()
        current_model.load_weights("resnet model/resnet.h5")  # Update the path to your ResNet weights file
    elif model_name == "InceptionNet":
        current_model = build_inception_model()
        current_model.load_weights("inceptionet model/inceptionnetv3.h5")  # Update the path to your InceptionNet weights file
    current_model_name = model_name

# Function to detect faces and draw bounding boxes
def detect_faces_and_draw(image_path):
    image = Image.open(image_path).convert("RGB")
    image_np = np.array(image)

    detections = detector.detect_faces(image_np)

    if not detections:
        return image  # Return the original image if no faces detected

    # Draw bounding boxes
    draw = ImageDraw.Draw(image)
    for face in detections:
        x, y, width, height = face['box']
        x2, y2 = x + width, y + height
        draw.rectangle([x, y, x2, y2], outline="green", width=5)

    return image

# Initialize CustomTkinter app
app = ctk.CTk()
app.title("Deepfake Detection")
app.geometry("800x400")
app.minsize(600, 300)
app.columnconfigure(0, weight=1)
app.columnconfigure(1, weight=1)
app.rowconfigure(0, weight=1)

# Global variables for image
selected_image_path = None
selected_model_button = None

# Function to open file dialog and load an image
def open_image():
    global selected_image_path
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if file_path:
        selected_image_path = file_path
        processed_image = detect_faces_and_draw(file_path)
        display_image(processed_image)

# Function to display image in GUI using CTkImage
def display_image(image):
    try:
        img = image.copy()
        img.thumbnail((300, 300))  # Resize for display while keeping aspect ratio
        img = ctk.CTkImage(img, size=(300, 300))
        image_label.configure(image=img, text="")  # Clear the placeholder text
        image_label.image = img  # Keep a reference to avoid garbage collection
    except Exception as e:
        image_label.configure(text="Error loading image")  # Handle image load errors

# Preprocess the image for model input
def preprocess_image(image_path):
    img = Image.open(image_path).convert("RGB")  # Convert image to RGB to remove alpha channel
    img = img.resize((224, 224))  # Resize to match model input shape
    img_array = np.array(img) / 255.0  # Normalize to [0, 1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

# Function to run inference with the selected model
def run_inference():
    global selected_image_path, current_model, current_model_name
    if selected_image_path and current_model:
        img_array = preprocess_image(selected_image_path)
        prediction = current_model.predict(img_array)
        deepfake_prob = prediction[0][0]  # Assuming the 1st output neuron indicates Deepfake
        result_label.configure(
            text=f"{current_model_name} - Deepfake Probability: {deepfake_prob:.2%}"
        )
    elif not selected_image_path:
        result_label.configure(text="Please select an image first.")
    elif not current_model:
        result_label.configure(text="Please select a model first.")

# Function to run inference on all models
def run_inference_all():
    global selected_image_path
    if not selected_image_path:
        result_label.configure(text="Please select an image first.")
        return
 # Prepare the table header
    results = [["Model Name", "Deepfake Probability"]]
    
    # Iterate through all models
    for model_name in model_names:
        load_model(model_name)  # Load the current model
        if current_model:
            img_array = preprocess_image(selected_image_path)
            prediction = current_model.predict(img_array)
            deepfake_prob = prediction[0][0]  # Assuming the 1st neuron indicates Deepfake
            results.append([model_name, f"{deepfake_prob:.2%}"])
    
    # Display results in tabular format in the right panel
    table_text = "\n".join([f"{row[0]:<15} | {row[1]}" for row in results])
    result_label.configure(text=table_text)

# Function to highlight selected model button
def select_model(model_name, button):
    global selected_model_button
    if selected_model_button:
        selected_model_button.configure(fg_color=None)
    selected_model_button = button
    selected_model_button.configure(fg_color="lightblue")
    load_model(model_name)

# Helper function to create model buttons
def create_model_button(name):
    button = ctk.CTkButton(
        right_panel,
        text=name,
        command=lambda: select_model(name, button)
    )
    button.pack(pady=5)
    return button

# Layout configuration
# Left panel for image input
left_panel = ctk.CTkFrame(app, width=200)
left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
left_panel.grid_rowconfigure(0, weight=1)

image_button = ctk.CTkButton(left_panel, text="Select Image", command=open_image)
image_button.pack(pady=10)

image_label = ctk.CTkLabel(left_panel, text="No Image Selected", anchor="center")
image_label.pack(pady=10, fill="both", expand=True)
# Right panel for model selection
right_panel = ctk.CTkFrame(app, width=200)
right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
right_panel.grid_rowconfigure(0, weight=1)

# Model label
model_label = ctk.CTkLabel(right_panel, text="Select a Model")
model_label.pack(pady=10)

# Create model buttons using the helper function
model_names = ["MobileNet V3", "ResNet", "InceptionNet"]
model_buttons = [create_model_button(name) for name in model_names]

# Run inference button
run_button = ctk.CTkButton(right_panel, text="Run Inference", command=run_inference)
run_button.pack(pady=20)

# Run All Inference button
run_all_button = ctk.CTkButton(right_panel, text="Run All Inferences", command=run_inference_all)
run_all_button.pack(pady=20)

# Output label
result_label = ctk.CTkLabel(app, text="", font=("Courier New", 14), anchor="w", justify="left")
result_label.grid(row=1, column=0, columnspan=2, pady=10, sticky="w")

# Enable window resizing
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

# Run the app
app.mainloop()