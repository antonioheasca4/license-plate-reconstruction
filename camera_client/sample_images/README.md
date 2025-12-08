# Camera Client - Sample Images

Put images with license plates in this folder.

When you add a new image, the client camera will automatically detect it and send it to the server for processing.

## Supported Formats
- `.jpg` / `.jpeg`
- `.png`

## Example
```bash
# Windows
copy path\to\license_plate.jpg sample_images\

# Linux/macOS
cp path/to/license_plate.jpg sample_images/
```

The client camera will automatically process the image and save the results in the `results/` folder.
