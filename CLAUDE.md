# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Artist Development Hub is a full-stack web application designed to help artists practice and improve their skills through structured warmup sessions, reference image management, artwork critique tracking, and AI-powered art analysis.

The application consists of:
- **Backend**: FastAPI REST API server (Python) with AI/ML capabilities
- **Frontend**: React application with React Router
- **Data Storage**: File-based JSON storage for skills, metadata, and critiques
- **AI Models**: BLIP for image captioning/analysis, CLIP for semantic search and embeddings

## Architecture

### Backend Structure (backend/app.py)

The backend is a FastAPI application that provides:

1. **Skills Management** - CRUD operations for art skills list
2. **Image Management** - Serves images from configured directories with security checks
3. **Warmup Sessions** - Generates random image sets for practice sessions
4. **Artwork Uploads** - Handles file uploads for drawings and artwork
5. **Critique System** - Stores and retrieves critiques for uploaded artwork
6. **AI-Powered Critiques** - Uses BLIP model for comprehensive art analysis (description, composition, mood, interpretation, judgment)
7. **Semantic Image Search** - CLIP-based embedding search for finding images by text queries
8. **Art Movements Database** - 15 art movements with characteristics and guidance (Social Realism, Mexican Muralism, Harlem Renaissance, Feminist Art, etc.)
9. **Paint/Pigment Tracking** - Manage paint collection with RGB color lookup using webcolors
10. **Google Photos Integration** - OAuth2 flow for syncing photos from Google Photos albums
11. **Metadata Storage** - Tracks tags, skills, and relationships between images and artwork

### Data Architecture

All data is stored in `backend/data/` directory as JSON files:

- `skills.json` - Array of skill names (e.g., "Drapery", "Foreshortening", "Perspective")
- `metadata.json` - Object with two keys:
  - `images` - Metadata for reference images (keyed by file path)
  - `artwork` - Metadata for uploaded artwork including associated skills and critique IDs
- `critiques.json` - Array of critique objects with fields: id, artworkPath, skill, critique, createdAt
- `practice_sessions.json` - Array of practice session records with stats tracking
- `drawings.json` - Array of drawing/sketch records with optional AI-generated critiques
- `image_index.json` - CLIP embeddings index for semantic search
- `embeddings.npy` - NumPy array of CLIP image embeddings
- `paints.json` - Array of paint records with RGB values, brand, type, lightfastness
- `google_albums.json` - Synced Google Photos albums metadata
- `google_photos_token.json` - OAuth2 credentials for Google Photos (gitignored)

### Image Path Configuration

The backend uses **configurable paths** via `backend/config.json`. Paths are automatically detected - if primary paths don't exist, it falls back to local `sample_images/` directories.

**Configuration file:** `backend/config.json`

```json
{
  "image_paths": {
    "reference": ["D:\\projects\\art-models\\4", "D:\\projects\\art-models\\5", ...],
    "photos": "D:\\projects\\art-models\\googlephotos",
    "artwork": "D:\\projects\\art models\\my_artwork"
  },
  "fallback_paths": {
    "reference": ["./sample_images/reference"],
    "photos": "./sample_images/photos",
    "artwork": "./sample_images/artwork"
  }
}
```

**How it works:**
1. Backend reads `config.json` on startup (backend/app.py:48-96)
2. Checks if primary paths exist (e.g., D:\projects\art-models\4)
3. If not found, uses fallback paths relative to project root
4. Creates fallback directories automatically if they don't exist

**To use your own image directories:**
- Edit `backend/config.json` with your actual paths
- Backend will auto-detect which paths are available
- Fallback paths ensure the app runs anywhere

### Security Model

The `/api/images/file` endpoint includes path validation to prevent directory traversal attacks. Only files within the configured `IMAGE_PATHS` can be served.

## Development Commands

### Backend

```bash
# Install dependencies (includes AI models: transformers, torch, BLIP, CLIP)
cd backend
pip install -r requirements.txt

# Install AI model dependencies (if not already installed)
pip install transformers torch pillow google-auth-oauthlib google-api-python-client requests webcolors scikit-learn numpy

# Run backend server (development with auto-reload) - DEFAULT PORT 3001
cd backend
python app.py
# OR
uvicorn app:app --reload --host 0.0.0.0 --port 3001

# Run backend server (production)
uvicorn app:app --host 0.0.0.0 --port 3001
```

**Important**: The backend runs on `http://localhost:3001` by default (see app.py line 1988). AI models (BLIP, CLIP) are lazy-loaded on first use to save memory.

### Frontend

The frontend is a React application that:
- Runs on port 3000 (default React development server)
- Uses React Router for client-side routing
- Uses the proxy configured in package.json to route API calls to http://localhost:8000
- Can be built with `npm run build` for production deployment

```bash
# Install frontend dependencies
cd frontend
npm install

# Run development server
npm start

# Build for production
npm run build
```

### Running Full Stack

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

- Frontend will be available at `http://localhost:3000`
- Backend API will be available at `http://localhost:3001`
- **OpenAPI Documentation**: `http://localhost:3001/` (auto-redirects to Swagger UI)
  - Interactive API docs: `http://localhost:3001/docs`
  - Alternative ReDoc: `http://localhost:3001/redoc`
  - OpenAPI schema: `http://localhost:3001/openapi.json`
- Frontend proxies API requests to backend automatically

## AI Features

### AI Models (Lazy-Loaded)

1. **BLIP (Salesforce/blip-image-captioning-base)** - Image captioning and visual question answering
   - Used for: Generating descriptions, analyzing composition, mood, themes
   - Lazy-loaded on first use via `get_blip_model()` (backend/app.py:301-315)

2. **CLIP (openai/clip-vit-base-patch32)** - Image and text embeddings
   - Used for: Semantic image search, similarity matching
   - Lazy-loaded on first use via `get_clip_model()` (backend/app.py:321-335)

### AI-Powered Art Critique

The `generate_art_critique()` function (backend/app.py:423-650) produces comprehensive 6-part critiques:
1. **Description** - What's in the image (BLIP + color analysis)
2. **Composition** - Spatial arrangement, rule of thirds, visual flow
3. **Mood** - Emotional quality based on color temperature and contrast
4. **Analysis** - Design principles (value, contrast, color usage)
5. **Interpretation** - Thematic content and meaning
6. **Judgment** - Strengths and areas for growth

### Image Search

- `/api/images/search` - Semantic text-to-image search using CLIP embeddings
- `/api/images/rebuild-index` - Rebuild CLIP embedding index for all photos
- Embeddings stored in `embeddings.npy`, indexed in `image_index.json`

## API Endpoints

### Core Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | Health check |
| GET | `/api/skills` | Get all skills |
| POST | `/api/skills` | Add new skill |
| DELETE | `/api/skills/{skill}` | Delete skill |

### Image Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/images/reference` | Get all reference images |
| POST | `/api/images/warmup-session` | Generate random image set for warmup |
| GET | `/api/images/file?path=...` | Serve image file (with security check) |
| GET | `/api/images/photos` | Get photos from collection |
| POST | `/api/images/search` | Semantic search using CLIP embeddings |
| POST | `/api/images/rebuild-index` | Rebuild CLIP embedding index |
| GET | `/api/images/index-status` | Get index status |

### Drawings & Critiques
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/drawings/upload` | Upload drawing for critique |
| GET | `/api/drawings` | Get all drawings |
| GET | `/api/drawings/{id}` | Get drawing details |
| DELETE | `/api/drawings/{id}` | Delete drawing |
| POST | `/api/critiques/ai` | Generate AI critique using BLIP |
| POST | `/api/critiques` | Save manual critique |
| GET | `/api/critiques/{artworkPath}` | Get critiques for artwork |

### Art Movements
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/art-movements` | List all art movements |
| GET | `/api/art-movements/{name}` | Get movement details |
| POST | `/api/art-movements/compare` | Compare artwork to movement |

### Paint Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/paints` | Get all paints |
| POST | `/api/paints` | Add paint |
| PUT | `/api/paints/{id}` | Update paint |
| DELETE | `/api/paints/{id}` | Delete paint |
| POST | `/api/paints/lookup-color` | Lookup RGB from color name/hex |

### Google Photos Integration
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/google-photos/auth-status` | Check auth status |
| POST | `/api/google-photos/upload-credentials` | Upload OAuth credentials |
| GET | `/api/google-photos/auth-url` | Get OAuth authorization URL |
| GET | `/api/google-photos/oauth-callback` | OAuth callback handler |
| GET | `/api/google-photos/albums` | List albums |
| POST | `/api/google-photos/sync-album` | Sync album to local storage |
| POST | `/api/google-photos/download-picker-photos` | Download selected photos |

### Analytics
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/stats/practice` | Get practice statistics |
| GET | `/api/stats/skill-progress/{skill}` | Get skill progress timeline |
| POST | `/api/sessions/log` | Log practice session |
| GET | `/api/sessions` | Get practice sessions (with filters) |
| DELETE | `/api/sessions/{id}` | Delete practice session |

### Metadata
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/metadata` | Get all metadata |
| POST | `/api/metadata/image` | Update image metadata |

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

## Testing

### End-to-End Tests (Playwright)

The `playwright-tests/` directory contains Playwright tests for the application.

**Setup:**
```bash
cd playwright-tests
npm install  # Already done
npx playwright install  # Already done
```

**Running tests:**
```bash
cd playwright-tests

# Run all tests
npm test

# Run with UI (interactive)
npm run test:ui

# Run with browser visible
npm run test:headed

# View test report
npm run test:report
```

**Available tests:**
- `google-photos-integration.spec.js` - Tests Google Photos OAuth flow and file picker

The tests will automatically start backend and frontend servers if not already running. See `playwright-tests/README.md` for more details.

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
