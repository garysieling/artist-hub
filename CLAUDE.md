# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Artist Development Hub is a full-stack web application designed to help artists practice and improve their skills through structured warmup sessions, reference image management, and artwork critique tracking.

The application consists of:
- **Backend**: FastAPI REST API server (Python)
- **Frontend**: React application
- **Data Storage**: File-based JSON storage for skills, metadata, and critiques

## Architecture

### Backend Structure (backend/app.py)

The backend is a FastAPI application that provides:

1. **Skills Management** - CRUD operations for art skills list
2. **Image Management** - Serves images from configured directories with security checks
3. **Warmup Sessions** - Generates random image sets for practice sessions
4. **Artwork Uploads** - Handles file uploads via multer
5. **Critique System** - Stores and retrieves critiques for uploaded artwork
6. **Metadata Storage** - Tracks tags, skills, and relationships between images and artwork

### Data Architecture

All data is stored in `data/` directory as JSON files:

- `skills.json` - Array of skill names (e.g., "Drapery", "Foreshortening", "Perspective")
- `metadata.json` - Object with two keys:
  - `images` - Metadata for reference images (keyed by file path)
  - `artwork` - Metadata for uploaded artwork including associated skills and critique IDs
- `critiques.json` - Array of critique objects with fields: id, artworkPath, skill, critique, createdAt
- `practice_sessions.json` - Array of practice session records
- `drawings.json` - Array of drawing/sketch records
- `image_index.json` - Indexed cache of images for faster retrieval
- `paints.json` - Array of paint/color records

### Image Path Configuration

The backend accesses images from hardcoded Windows paths (backend/app.py:45-54):
- **Reference images**: Multiple directories under `D:\projects\art-models\`
  - `D:\projects\art-models\4`
  - `D:\projects\art-models\5`
  - `D:\projects\art-models\8`
  - `D:\projects\art-models\reference.pictures`
- **Photos**: `D:\projects\art-models\googlephotos`
- **Artwork uploads**: `D:\projects\art models\my_artwork`

**Important**: These paths are environment-specific. When deploying or running on different machines, update the `IMAGE_PATHS` constant in backend/app.py:45-54.

### Security Model

The `/api/images/file` endpoint includes path validation to prevent directory traversal attacks. Only files within the configured `IMAGE_PATHS` can be served.

## Development Commands

### Backend

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run backend server (development with auto-reload)
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Run backend server (production)
uvicorn app:app --host 0.0.0.0 --port 8000
```

The backend runs on `http://localhost:8000`

### Frontend

The frontend is a React application that:
- Runs on port 3000 (default React development server)
- Uses the proxy configured in package.json to route API calls to http://localhost:8000
- Can be built with `npm run build` for production deployment

### Running Full Stack

1. Start backend: `cd backend && uvicorn app:app --reload`
2. Start frontend: `cd frontend && npm start`
3. Frontend will be available at `http://localhost:3000`
4. Backend API will be available at `http://localhost:8000`

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | Health check |
| GET | `/api/skills` | Get all skills |
| POST | `/api/skills` | Add new skill |
| DELETE | `/api/skills/:skill` | Delete skill |
| GET | `/api/images/reference` | Get all reference images |
| POST | `/api/images/warmup-session` | Generate random image set for warmup |
| GET | `/api/images/file?path=...` | Serve image file (with security check) |
| GET | `/api/images/photos` | Get photos from collection |
| GET | `/api/metadata` | Get all metadata |
| POST | `/api/metadata/image` | Update image metadata |
| POST | `/api/artwork/upload` | Upload artwork with multer |
| GET | `/api/artwork` | Get all uploaded artwork with metadata |
| POST | `/api/critiques` | Save critique for artwork |
| GET | `/api/critiques/:artworkPath` | Get critiques for specific artwork |

## Key Implementation Details

### Image Discovery

The backend recursively scans directories for image files (.jpg, .jpeg, .png, .gif, .bmp, .webp) and returns metadata including path, name, size, and modification date. This functionality is implemented in backend/app.py.

### Metadata Linking

- Images and artwork are linked via file paths as keys
- Critiques are linked to artwork via `artworkPath` field
- Artwork metadata stores an array of critique IDs for quick lookup
- Skills can be associated with both reference images and uploaded artwork

### File Upload Flow

1. Client sends POST to `/api/artwork/upload` with multipart form data
2. FastAPI UploadFile saves file to artwork directory with timestamped filename
3. Server creates metadata entry with skills, reference image link, and empty critiques array
4. Response includes file path and metadata

## Common Workflows

### Adding a New Skill

The skills list is used throughout the app for tagging and filtering. Skills are stored as a simple string array.

### Creating a Warmup Session

1. Client requests `/api/images/warmup-session` with count and optional skill filters
2. Server collects all images from reference directories
3. Images are shuffled randomly and limited to requested count
4. Skill filtering is implemented in the backend/app.py

### Uploading and Critiquing Artwork

1. Upload artwork via `/api/artwork/upload` with associated skills
2. Artwork appears in gallery via `/api/artwork`
3. Submit critiques via `/api/critiques` which updates both critiques.json and artwork metadata
4. Retrieve critiques via `/api/critiques/:artworkPath`
