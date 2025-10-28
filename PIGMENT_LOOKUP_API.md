# Pigment Lookup API Documentation

## Overview
The application now has comprehensive pigment code support with lookup, search, and color family organization.

## API Endpoints

### 1. **Lookup Pigment Code**
```
GET /api/pigments/lookup/{pigment_code}
```

**Description:** Look up a specific pigment code and get its RGB and hex color values.

**Parameters:**
- `pigment_code` (path parameter): The pigment code to look up (e.g., "PY 43", "PY43", "PR 188")
  - Case insensitive
  - Supports both "PY 43" and "PY43" formats

**Response (Success):**
```json
{
  "success": true,
  "code": "PY 43",
  "rgb": {
    "r": 255,
    "g": 240,
    "b": 0
  },
  "hex": "#FFF000",
  "valid": true
}
```

**Response (Not Found):**
```json
{
  "success": false,
  "code": "INVALID",
  "valid": false,
  "message": "Pigment code 'INVALID' not found"
}
```

**Example Usage:**
```javascript
// Fetch pigment color by code
fetch('/api/pigments/lookup/PY%2043')  // URL encode the space
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      console.log(`PY 43 is ${data.hex} (RGB: ${data.rgb.r}, ${data.rgb.g}, ${data.rgb.b})`);
    }
  });
```

---

### 2. **Search Pigments by Color**
```
GET /api/pigments/search?query={color_name}
```

**Description:** Search for pigments by color name or family.

**Parameters:**
- `query` (query parameter): Color name to search for
  - Examples: "yellow", "red", "blue", "green", "black", "white", "violet", "orange", "brown"
  - Or specific pigment code like "PY43"

**Response:**
```json
{
  "success": true,
  "query": "yellow",
  "results": [
    {
      "code": "PY 1",
      "rgb": {"r": 255, "g": 255, "b": 0},
      "hex": "#FFFF00",
      "name": "PY 1 - Color"
    },
    {
      "code": "PY 3",
      "rgb": {"r": 254, "g": 244, "b": 0},
      "hex": "#FEF400",
      "name": "PY 3 - Color"
    },
    {
      "code": "PY 43",
      "rgb": {"r": 255, "g": 240, "b": 0},
      "hex": "#FFF000",
      "name": "PY 43 - Color"
    }
    // ... more results
  ]
}
```

**Example Usage:**
```javascript
// Search for all yellow pigments
fetch('/api/pigments/search?query=yellow')
  .then(res => res.json())
  .then(data => {
    data.results.forEach(pigment => {
      console.log(`${pigment.code}: ${pigment.hex}`);
    });
  });
```

---

### 3. **Get All Pigments by Family**
```
GET /api/pigments/all
```

**Description:** Get all available pigments organized by color family.

**Response:**
```json
{
  "success": true,
  "pigments": {
    "Yellows": [
      {"code": "PY 1", "rgb": {"r": 255, "g": 255, "b": 0}, "hex": "#FFFF00"},
      {"code": "PY 3", "rgb": {"r": 254, "g": 244, "b": 0}, "hex": "#FEF400"},
      {"code": "PY 43", "rgb": {"r": 255, "g": 240, "b": 0}, "hex": "#FFF000"},
      // ... more yellows
    ],
    "Reds": [
      // ... reds
    ],
    "Blues": [
      // ... blues
    ],
    // ... other families
  }
}
```

**Example Usage:**
```javascript
// Get all pigments and populate a dropdown
fetch('/api/pigments/all')
  .then(res => res.json())
  .then(data => {
    for (const [family, pigments] of Object.entries(data.pigments)) {
      console.log(`${family}:`, pigments.length, 'pigments');
    }
  });
```

---

## Frontend Implementation Example

### Simple Color Picker Component

```javascript
import React, { useState } from 'react';

function PigmentColorPicker() {
  const [pigmentCode, setPigmentCode] = useState('');
  const [color, setColor] = useState(null);
  const [error, setError] = useState('');

  const lookupPigment = async (code) => {
    try {
      // URL encode the pigment code (replace spaces with %20)
      const encodedCode = encodeURIComponent(code);
      const response = await fetch(`/api/pigments/lookup/${encodedCode}`);
      const data = await response.json();

      if (data.success && data.valid) {
        setColor(data);
        setError('');
      } else {
        setError(`Pigment code "${code}" not found`);
        setColor(null);
      }
    } catch (err) {
      setError('Error looking up pigment: ' + err.message);
      setColor(null);
    }
  };

  const handleInputChange = (e) => {
    const code = e.target.value;
    setPigmentCode(code);
    if (code.trim().length > 0) {
      lookupPigment(code);
    }
  };

  return (
    <div>
      <h2>Pigment Color Lookup</h2>

      <input
        type="text"
        placeholder="Enter pigment code (e.g., PY 43, PR 188, PB 15)"
        value={pigmentCode}
        onChange={handleInputChange}
        style={{padding: '8px', width: '300px'}}
      />

      {error && <p style={{color: 'red'}}>{error}</p>}

      {color && color.valid && (
        <div style={{marginTop: '20px'}}>
          <h3>{color.code}</h3>

          {/* Color preview */}
          <div
            style={{
              width: '100px',
              height: '100px',
              backgroundColor: color.hex,
              border: '2px solid #ccc',
              marginBottom: '10px'
            }}
          />

          {/* Color values */}
          <p><strong>Hex:</strong> {color.hex}</p>
          <p><strong>RGB:</strong> ({color.rgb.r}, {color.rgb.g}, {color.rgb.b})</p>
        </div>
      )}
    </div>
  );
}

export default PigmentColorPicker;
```

---

## Supported Pigment Codes

### Yellows (PY)
- PY 1, PY 3, PY 43, PY 53, PY 83, PY 109, PY 150

### Reds (PR)
- PR 3, PR 4, PR 5, PR 48, PR 57, PR 112, PR 188, PR 200, PR 202

### Blues (PB)
- PB 15, PB 15:1, PB 15:3, PB 29, PB 60

### Greens (PG)
- PG 7, PG 36

### Blacks (PBk)
- PBk 6, PBk 7, PBk 9, PBk 11

### Whites (PW)
- PW 4, PW 6, PW 7

### Violets (PV)
- PV 1, PV 3, PV 19

### Oranges (PO)
- PO 20, PO 36

### Browns (PBr)
- PBr 7

---

## Testing

You can test the endpoints using curl:

```bash
# Lookup a specific pigment
curl http://localhost:3001/api/pigments/lookup/PY%2043

# Search for yellows
curl http://localhost:3001/api/pigments/search?query=yellow

# Get all pigments
curl http://localhost:3001/api/pigments/all
```

---

## Integration with Paint Management

The pigment lookup is already integrated with the existing paint color lookup endpoint:

```
POST /api/paints/lookup-color
```

This endpoint now supports both:
- Standard CSS colors (e.g., "red", "blue")
- Pigment codes (e.g., "PY 43", "PR 188")

**Example:**
```json
{
  "color_name": "PY 43"
}
```

Will return:
```json
{
  "r": 255,
  "g": 240,
  "b": 0
}
```
