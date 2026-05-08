import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

# Load the pre-trained MobileNet model (placeholder for real deepfake detection model)
model1=keras.applications.MobileNet(input_shape=(224, 224, 3),weights="imagenet")
model1.trainable=True
def build_model():
    inputs=Input(shape=(224, 224, 3))
    model = Sequential([inputs,
                        model1,
                        layers.Dense(1024,activation='relu'),
                        layers.BatchNormalization(),
                        layers.Dense(512,activation='relu'),
                        layers.BatchNormalization(),
                        layers.Dense(2, activation='softmax')
                        ])
    return model
model=build_model()
model.summary()
model.load_weights("mobilenet_model\model2.h5")

def is_deepfake(frame):
    # Resize frame to the model's input size
    resized_frame = cv2.resize(frame, (224, 224))
    resized_frame = np.expand_dims(resized_frame, axis=0)
    # Use MobileNet for deepfake detection (dummy classification logic here)
    predictions = model.predict(resized_frame)
    return predictions[0][0]
   
class DeepfakeDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Deepfake Detector")

        # Create GUI elements
        self.canvas = tk.Canvas(root, width=640, height=480)
        self.canvas.pack()

        self.btn_load_video = tk.Button(root, text="Load Video", command=self.load_video)
        self.btn_load_video.pack()

        self.video_path = None
        self.video_stream = None
        self.frame = None
        self.playing = False

    def load_video(self):
        # Open file dialog to select a video file
        self.video_path = filedialog.askopenfilename(filetypes=[("Video Files", ".mp4;.avi")])
        if self.video_path:
            self.playing = True
            self.video_stream = cv2.VideoCapture(self.video_path)
            self.play_video()

    def play_video(self):
        if self.playing and self.video_stream.isOpened():
            # Read a frame from the video
            ret, frame = self.video_stream.read()
            if ret:
                # Process frame for deepfake detection
                deepfake_detected = is_deepfake(frame)

                # Convert the frame to RGB for tkinter display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img_tk = ImageTk.PhotoImage(image=img)

                # Display the frame
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
                self.root.image_tk = img_tk  # Keep reference to avoid garbage collection

                # Display "YES/NO" based on deepfake detection
                text = deepfake_detected 
                self.canvas.create_text(50, 30, text=text, fill="red", font=("Helvetica", 24))

                # Continue playing the video
                self.root.after(10, self.play_video)
            else:
                self.video_stream.release()

# Create the tkinter window
root = tk.Tk()
app = DeepfakeDetectorGUI(root)
root.mainloop()