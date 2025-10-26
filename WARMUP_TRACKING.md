# Warmup Drawing Tracking Feature

## Overview

This feature allows you to track which reference images you've drawn during warmup sessions. When you mark an image as drawn, the system records a timestamp. Later, you can filter to show only "Already Drawn" images sorted by most recently drawn first.

## How It Works

### 1. During Warmup Session

While in a warmup session, you'll see a new **"✓ Drew This"** button next to the timer.

**Before:**
```
[Play/Pause] Timer    Image 5 of 30  [End Session]
```

**After:**
```
[Play/Pause] Timer    Image 5 of 30  [✓ Drew This] [End Session]
```

**To Mark an Image as Drawn:**
1. Complete drawing the reference image
2. Click **"✓ Drew This"** button
3. See confirmation: "✓ Image marked as drawn!"
4. Continue to next image

### 2. Metadata Structure

Each image now stores a drawing timestamp:

```json
{
  "images": {
    "reference/vacation/photo.jpg": {
      "drawn": true,
      "drawnAt": "2025-10-26T14:32:45.123456",
      "mediums": [],
      "updatedAt": "2025-10-26T14:32:45.123456"
    }
  }
}
```

**Key Fields:**
- `drawn`: Boolean - whether the image has been drawn
- `drawnAt`: ISO timestamp - when the drawing was recorded
- `mediums`: Array - type of materials used (optional, for Photo Finder)

### 3. Viewing Drawn Images in Photo Finder

**Filters:**
1. **Photo Collection**: Select **"Reference Photos"**
2. **Status**: Select **"Already Drawn"**

**Result:**
- Shows only images you've marked as drawn
- **Sorted by most recently drawn first** (newest at top)
- Images without timestamps appear at the bottom

### 4. Backend Endpoint

**New Endpoint:** `POST /api/metadata/image/mark-drawn`

**Request:**
```json
{
  "imagePath": "reference/vacation/photo.jpg",
  "mediums": []
}
```

**Response:**
```json
{
  "success": true,
  "imagePath": "reference/vacation/photo.jpg",
  "drawnAt": "2025-10-26T14:32:45.123456",
  "message": "Image marked as drawn at 2025-10-26T14:32:45.123456"
}
```

## Usage Workflow

### Scenario: Tracking Practice Progress

1. **Start Warmup**
   - Navigate to Warmup Sessions
   - Select duration and reference images
   - Begin drawing practice

2. **Mark Completed Drawings**
   - As you finish each image, click **"✓ Drew This"**
   - System records the exact timestamp
   - Continue through session

3. **Review Your Progress**
   - Go to Photo Finder
   - Select "Reference Photos" from Photo Collection
   - Select "Already Drawn" from Status filter
   - See your drawings sorted with most recent first

4. **Track Practice Over Time**
   - Timestamps show when you practiced each image
   - Helps identify which references you practice most frequently
   - Supports practice statistics and goals

## Technical Details

### Frontend Changes (`App.js`)

**1. Mark as Drawn Button** (lines 553-575)
```javascript
<button
  onClick={async () => {
    if (currentImage) {
      await fetch(`${API_URL}/metadata/image/mark-drawn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          imagePath: currentImage.path,
          mediums: []
        })
      });
      alert(`✓ Image marked as drawn!`);
    }
  }}
  className="button button-secondary"
>
  ✓ Drew This
</button>
```

**2. Sorting Logic** (lines 1335-1351)
```javascript
// If showing "Already Drawn", sort by most recently drawn first
if (filters.status === 'Already Drawn') {
  photosData.sort((a, b) => {
    const drawnAtA = metadataData.images?.[a.path]?.drawnAt;
    const drawnAtB = metadataData.images?.[b.path]?.drawnAt;

    if (drawnAtA && drawnAtB) {
      return new Date(drawnAtB) - new Date(drawnAtA);
    }
    if (drawnAtA) return -1;
    if (drawnAtB) return 1;
    return 0;
  });
}
```

### Backend Changes (`app.py`)

**New Endpoint** (lines 1600-1631)
```python
@app.post("/api/metadata/image/mark-drawn")
async def mark_image_as_drawn(data: dict):
    """Mark an image as drawn with timestamp (for warmup sessions)"""
    image_path = data.get("imagePath")
    mediums = data.get("mediums", [])

    metadata["images"][image_path] = {
        **metadata["images"].get(image_path, {}),
        "drawn": True,
        "drawnAt": datetime.now().isoformat(),
        "mediums": mediums,
        "updatedAt": drawn_at
    }
```

## Data Storage

Timestamps are stored in `backend/data/metadata.json`:

```bash
cat backend/data/metadata.json | python -m json.tool | grep -A 5 drawnAt
```

## Future Enhancements

1. **Practice Statistics**
   - Count drawings per image
   - Calculate most frequently practiced references
   - Show practice timeline charts

2. **Mediums Tracking**
   - Allow selecting mediums during warmup
   - Track which materials were used
   - Filter by medium type

3. **Session Linking**
   - Associate marked images with specific warmup sessions
   - Show which session an image was drawn in
   - Calculate practice time per reference

4. **Export Data**
   - Export practice history as CSV
   - Generate practice reports
   - Share progress with instructors

5. **Smart Recommendations**
   - Suggest images you haven't drawn recently
   - Recommend images similar to ones you practice
   - AI-powered skill recommendations based on drawings

## Troubleshooting

**Q: Button doesn't appear in warmup session**
- A: Make sure you're in the "Session" step (actively drawing)
- A: Restart the warmup session if UI doesn't update

**Q: Images not showing as drawn after clicking button**
- A: Check browser console for API errors
- A: Verify backend is running and responding
- A: Refresh Photo Finder to reload metadata

**Q: Sorting not working**
- A: Ensure "Already Drawn" filter is selected
- A: Metadata must be loaded from backend
- A: Images without `drawnAt` timestamp appear at bottom

## API Integration Points

- **POST** `/api/metadata/image/mark-drawn` - Mark image as drawn
- **POST** `/api/metadata/image` - Update general image metadata
- **GET** `/api/metadata` - Retrieve all image metadata
- **GET** `/api/images/reference` - Get reference photos

## Files Modified

1. `frontend/src/App.js` - Added mark button and sorting logic
2. `backend/app.py` - Added new endpoint

All changes are backward compatible with existing functionality.
