import onnxruntime as ort
import os

model_path = os.path.join("agency", "kokoro-v1.0.onnx")
sess = ort.InferenceSession(model_path)

print("Inputs:")
for i in sess.get_inputs():
    print(f"Name: {i.name}, Type: {i.type}, Shape: {i.shape}")

print("\nOutputs:")
for o in sess.get_outputs():
    print(f"Name: {o.name}, Type: {o.type}, Shape: {o.shape}")
