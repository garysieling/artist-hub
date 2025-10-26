# Photo Indexer

The Photo Indexer is a Python script that scans your photo collections and automatically generates a comprehensive JSON index with AI-powered metadata. It uses Hugging Face models to analyze image content and suggest relevant art skills, lighting conditions, subject types, and more.

## Features

- **AI-Powered Analysis**: Uses state-of-the-art vision models from Hugging Face
- **Multiple Collections**: Organizes metadata by photo collection (My Photos, Reference Photos, My Art)
- **Smart Skill Suggestions**: Recommends relevant art skills based on image content
- **Flexible Indexing**: Can index all collections, specific collections, or individual images
- **Comprehensive Metadata**: Extracts subject type, gender, lighting, and skill suggestions for each image

## Metadata Fields

For each image, the indexer generates:

- **subject_type**: `People`, `Animals`, `Buildings`, `Landscapes`, or `All`
- **gender**: `Female`, `Male`, or `All` (for images with people)
- **lighting**: `Bright`, `Dark`, `High Contrast`, `Colorful`, or `All`
- **skills**: Array of 1-4 relevant art skills (e.g., `["Anatomy", "Proportion", "Gesture"]`)

## Installation

First, install the required dependencies:

```bash
cd backend
pip install transformers torch pillow scikit-learn
```

For GPU acceleration (optional but recommended):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Usage

### Index All Collections

```bash
cd backend
python photo_indexer.py
```

This scans all configured collections:
- **My Photos**: Google Photos directory
- **Reference Photos**: Reference images for practice
- **My Art**: Your uploaded artwork

### Index Specific Collection

```bash
python photo_indexer.py --collection my-photos
python photo_indexer.py --collection reference-photos
python photo_indexer.py --collection my-art
```

### Index Single Image

```bash
python photo_indexer.py --single /path/to/image.jpg
```

### Custom Output Location

```bash
python photo_indexer.py --output /custom/path/photo_index.json
```

## Output Format

The indexer creates `backend/data/photo_index.json` with the following structure:

```json
{
  "metadata": {
    "created": "2025-10-25T21:45:30.123456",
    "version": "1.0"
  },
  "collections": {
    "My Photos": {
      "photo1.jpg": {
        "subject_type": "People",
        "gender": "Female",
        "lighting": "Bright",
        "skills": ["Proportion", "Anatomy", "Gesture", "Composition"]
      },
      "photo2.jpg": {
        "subject_type": "Landscapes",
        "gender": "All",
        "lighting": "Colorful",
        "skills": ["Perspective", "Composition", "Light And Shadow", "Atmosphere"]
      }
    },
    "Reference Photos": {
      "ref1.jpg": { ... }
    },
    "My Art": {
      "artwork1.jpg": { ... }
    }
  }
}
```

## Models Used

The indexer uses these Hugging Face models:

1. **google/vit-base-patch16-224**: Image classification for general scene understanding
2. **openai/clip-vit-base-patch32**: Zero-shot classification for specific attributes (subject type, gender, lighting, skills)

## Performance Notes

- **First Run**: May take several minutes depending on the number of images. Models are downloaded and cached on first use.
- **GPU**: Recommended for faster processing. The script automatically detects and uses CUDA if available.
- **Memory**: Requires ~4-6GB of RAM. GPU memory requirements depend on batch size.

## Example Workflow

1. **Index your photos:**
   ```bash
   python photo_indexer.py
   ```

2. **Check the output:**
   ```bash
   cat data/photo_index.json | python -m json.tool | head -50
   ```

3. **Use the index in your app**: The front-end can now use this metadata for advanced filtering and recommendations

## Future Enhancements

- Batch processing for faster indexing
- Custom skill taxonomies
- Manual metadata editing UI
- Incremental indexing (only new/changed images)
- Caching of analysis results
- Integration with the main app API

## Troubleshooting

### Models won't download
Ensure you have internet connectivity and sufficient disk space (~5GB for models)

### Out of memory errors
Reduce the batch size in the ImageAnalyzer class, or use CPU-only mode:
```python
# In ImageAnalyzer.__init__, change device parameter:
device=-1  # Force CPU
```

### No images found
Check that your image paths in `config.json` are correct and directories exist

## API Integration

Once the index is created, you can integrate it with the frontend by:

1. Loading `photo_index.json` during app startup
2. Using metadata for filter suggestions
3. Implementing smart search based on indexed skills
4. Providing user recommendations based on image analysis
