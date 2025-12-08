# Results Folder

This is where the image processing results are automatically saved.

## File Types

### 1. Reconstructed Images
Format: `{original_name}_reconstructed_{timestamp}.png`

### 2.  OCR results (JSON)
Format: `{original_name}_ocr_{timestamp}.json`

Content:
```json
{
  "original": "ABC123",
  "reconstructed": "ABC123"
}
```

## Cleanup
You can delete old files from this folder without affecting the client's functionality.
