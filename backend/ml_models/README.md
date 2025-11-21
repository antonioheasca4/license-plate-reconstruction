# ML Models Directory

## Model Requirements

Place your trained Pix2Pix model file here:

**Required:** Any `.keras` model file (e.g., `generator_256x128noSkew.keras`, `model.keras`, etc.)

### Model Specifications
- **Input shape:** (batch_size, 128, 256, 3)
- **Output shape:** (batch_size, 128, 256, 3)
- **Model type:** Pix2Pix Generator
- **Framework:** TensorFlow/Keras
- **Purpose:** License plate image reconstruction

### How to Add Your Model

1. Copy your trained `.keras` model file to this directory
2. The file can have any name (e.g., `generator.keras`, `model.keras`, `generator_256x128noSkew.keras`)
3. Restart the backend server
4. The first `.keras` file found will be loaded automatically at startup

### Model Loading

The model is loaded once at application startup (see `main.py`):
- On successful load, you'll see: "✓ ML model loaded successfully!"
- On failure, you'll see a warning message

### Inference

Images are automatically:
- Resized to 256x128 (width x height)
- Normalized to [-1, 1] range
- Processed through the model
- Converted back to PNG format

### Testing

Check model status: `GET /api/model/status`

Expected response when loaded:
```json
{
  "model_loaded": true,
  "model_path": "ml_models/<your_model_file>.keras",
  "status": "ready"
}
```
