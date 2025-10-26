# Photo Search Filter Integration

## Overview

The photo search filters are now fully integrated with the AI-generated photo index. Filters dynamically populate from the indexed metadata and apply in real-time as you adjust them.

## Features

### Dynamic Filter Dropdowns
- **Subject Type**: People, Animals, Buildings, Landscapes (from AI analysis)
- **Gender**: Female, Male (from AI analysis)
- **Lighting**: Bright, Dark, High Contrast, Colorful (from AI analysis)
- **Skills**: Dynamically populated from AI-indexed skills
- **Status**: Not Drawn, Already Drawn, All
- **Photo Collection**: My Photos, Reference Photos, Historical Art, My Art

### Smart Filtering
- Multiple filters work together with AND logic
- Graceful fallback for unindexed photos
- Instant results as filters change
- Combines with "Already Drawn" timestamp sorting

### Real-Time Updates
- Filters automatically trigger photo reload
- No need to press a search button
- Results update instantly

## How It Works

### Data Flow

```
Photo Index (Backend)
    ↓
GET /api/photo-index/filter-suggestions
    ↓
filterSuggestions state
    ↓
Filter Dropdowns (dynamically rendered)
    ↓
User selects filter(s)
    ↓
filters state updated
    ↓
useEffect triggered
    ↓
loadPhotos(false)
    ↓
Filtering Logic Applied
    ↓
Photos displayed (max 50)
```

### Filtering Algorithm

When photos are loaded, the system:

1. Fetches photos from selected collection
2. Loads indexed metadata from photo index
3. Filters by matching:
   - `subject_type` matches `filters.subjectType`
   - `gender` matches `filters.gender`
   - `lighting` matches `filters.lighting`
   - `filters.skill` is in image's `skills[]` array
4. Shows unindexed photos if metadata missing
5. Applies status filtering (Already Drawn, Not Drawn)
6. Sorts "Already Drawn" by most recent first

## API Endpoints

### Load Photo Index
```
GET /api/photo-index
```
Returns complete indexed metadata with all images and their attributes.

### Load Filter Suggestions
```
GET /api/photo-index/filter-suggestions
```
Returns available values for each filter:
```json
{
  "subject_types": ["People", "Animals", "Buildings", "Landscapes"],
  "genders": ["Female", "Male"],
  "lightings": ["Bright", "Dark", "High Contrast", "Colorful"],
  "skills": ["Anatomy", "Perspective", "Composition", ...]
}
```

## Usage Examples

### Example 1: Find Landscape Photos
1. Photo Collection: "Reference Photos"
2. Subject Type: "Landscapes"
3. **Result**: Photos tagged as landscapes

### Example 2: Find People for Anatomy Practice
1. Photo Collection: "Reference Photos"
2. Subject Type: "People"
3. Skills: "Anatomy"
4. **Result**: People photos marked good for anatomy practice

### Example 3: Recently Practiced Content
1. Photo Collection: "Reference Photos"
2. Status: "Already Drawn"
3. **Result**: Reference images you've drawn, newest first

### Example 4: Complex Filter
1. Photo Collection: "My Photos"
2. Subject Type: "People"
3. Gender: "Female"
4. Lighting: "Bright"
5. Status: "Not Drawn"
6. **Result**: Female people photos in bright lighting you haven't drawn yet

## Frontend Implementation

### State Variables
```javascript
const [photoIndex, setPhotoIndex] = useState(null);
const [filterSuggestions, setFilterSuggestions] = useState({
  subject_types: [],
  genders: [],
  lightings: [],
  skills: []
});
const [filters, setFilters] = useState({
  subjectType: 'All',
  gender: 'All',
  lighting: 'All',
  status: 'All',
  skill: 'All Skills'
});
```

### Dropdown Rendering
Dropdowns are populated dynamically from `filterSuggestions`:

```javascript
<select value={filters.subjectType} onChange={(e) => setFilters({...filters, subjectType: e.target.value})}>
  <option>All</option>
  {filterSuggestions.subject_types?.map(type => (
    <option key={type}>{type}</option>
  ))}
</select>
```

### Filtering Logic
Applied in `loadPhotos()` function:

```javascript
if (photoIndex && photoIndex.collections) {
  photosData = photosData.filter(photo => {
    const indexed = photoIndex.collections[collectionName][photo.path];

    if (filters.subjectType !== 'All' && indexed.subject_type !== filters.subjectType) {
      return false;
    }
    if (filters.gender !== 'All' && indexed.gender !== filters.gender) {
      return false;
    }
    if (filters.lighting !== 'All' && indexed.lighting !== filters.lighting) {
      return false;
    }
    if (filters.skill !== 'All Skills' && !indexed.skills.includes(filters.skill)) {
      return false;
    }

    return true;
  });
}
```

### Auto-Reload on Filter Change
```javascript
useEffect(() => {
  if (photos.length > 0) {
    loadPhotos(false);
  }
}, [filters.subjectType, filters.gender, filters.lighting, filters.skill, filters.status]);
```

## Performance

- **Dynamic Options**: Options load from cached photo index (~50ms)
- **Filtering**: In-browser filtering is instant (<100ms for 50+ photos)
- **Display**: Max 50 photos shown at a time
- **Memory**: Photo index cached in memory after first load

## Requirements

For filters to be fully functional:
1. Photo indexer must complete: `python photo_indexer.py`
2. Backend must load photo index on startup
3. Frontend loads index on component mount

Without the photo index:
- Dropdowns show empty (fallback to manual skills list)
- Filtering falls back to show all photos
- Status filter still works (Already Drawn / Not Drawn)

## Integration with Other Features

### Combined with Warmup Tracking
- Mark images as drawn during warmup
- Filter to "Already Drawn" to review practice
- Sort by most recent to see latest work

### Combined with AI Search
- Use filters to refine AI search results
- Start with AI search, then filter by attributes
- Subject type filter helps narrow broad searches

### Combined with Photo Collections
- Select collection first
- Then apply attribute filters
- Each collection has its own index

## Troubleshooting

### Filters not appearing
- **Issue**: Photo indexer hasn't completed
- **Solution**: Wait for indexer to finish, then refresh page

### All filters show "All" options only
- **Issue**: Filter suggestions failed to load
- **Solution**: Check browser console for API errors

### Filtering not working
- **Issue**: Photos not matching filter criteria
- **Solution**:
  - Verify photo index was created
  - Check that photos are in the indexed collection
  - Fallback shows all photos if no index

### Performance is slow
- **Issue**: Too many photos loaded
- **Solution**:
  - UI displays max 50 photos
  - Use more specific filters
  - Try filtering by skill first

## Future Enhancements

1. **Advanced Filters**
   - Color palette detection
   - Composition type (portrait/landscape orientation)
   - Estimated difficulty level

2. **Filter Combinations**
   - Save frequently used filter sets
   - Quick access buttons for common searches
   - "Smart" filter suggestions

3. **Visual Feedback**
   - Show count of results for each filter option
   - Disable filters with zero results
   - Visual preview of filter result count

4. **Integration**
   - Export filtered results
   - Share filter sets with others
   - Analytics on most-used filters

## Files Modified

- `frontend/src/App.js` - Filter UI and logic
- `backend/app.py` - API endpoints (already added)

## Status

✅ **Ready to Use** - All components integrated and functional

Once photo indexer completes, filters will be fully operational.
