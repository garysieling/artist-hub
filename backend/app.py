from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import random
import logging
import shutil
from PIL import Image
import io
import base64
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration, CLIPProcessor, CLIPModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import requests
import webcolors

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Artist Development Hub API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration - Load from config.json if it exists, otherwise use fallback paths
_PROJECT_ROOT = Path(__file__).parent.parent
_CONFIG_FILE = Path(__file__).parent / "config.json"

def load_image_paths():
    """Load image paths from config.json with fallback to sample directories"""
    if _CONFIG_FILE.exists():
        try:
            config = json.loads(_CONFIG_FILE.read_text())
            paths = config.get("image_paths", {})

            # Check if primary paths exist, otherwise use fallback
            fallback = config.get("fallback_paths", {})
            result = {}

            # Check reference paths
            ref_paths = paths.get("reference", [])
            valid_ref_paths = [p for p in ref_paths if Path(p).exists()]
            if valid_ref_paths:
                result["reference"] = valid_ref_paths
            else:
                fallback_refs = fallback.get("reference", [])
                result["reference"] = [str(_PROJECT_ROOT / p) if not Path(p).is_absolute() else p
                                      for p in fallback_refs]

            # Check photos path
            photos_path = paths.get("photos", "")
            if photos_path and Path(photos_path).exists():
                result["photos"] = photos_path
            else:
                fallback_photos = fallback.get("photos", "./sample_images/photos")
                result["photos"] = str(_PROJECT_ROOT / fallback_photos) if not Path(fallback_photos).is_absolute() else fallback_photos

            # Check artwork path
            artwork_path = paths.get("artwork", "")
            if artwork_path and Path(artwork_path).exists():
                result["artwork"] = artwork_path
            else:
                fallback_artwork = fallback.get("artwork", "./sample_images/artwork")
                result["artwork"] = str(_PROJECT_ROOT / fallback_artwork) if not Path(fallback_artwork).is_absolute() else fallback_artwork

            return result
        except Exception as e:
            logger.warning(f"Error loading config.json: {e}, using fallback paths")

    # Default fallback - use sample directories
    return {
        "reference": [str(_PROJECT_ROOT / "sample_images" / "reference")],
        "photos": str(_PROJECT_ROOT / "sample_images" / "photos"),
        "artwork": str(_PROJECT_ROOT / "sample_images" / "artwork")
    }

IMAGE_PATHS = load_image_paths()

# Data directory for JSON storage
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Uploads directory for user artwork
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

SKILLS_FILE = DATA_DIR / "skills.json"
METADATA_FILE = DATA_DIR / "metadata.json"
CRITIQUES_FILE = DATA_DIR / "critiques.json"
PRACTICE_SESSIONS_FILE = DATA_DIR / "practice_sessions.json"
DRAWINGS_FILE = DATA_DIR / "drawings.json"
IMAGE_INDEX_FILE = DATA_DIR / "image_index.json"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.npy"
GOOGLE_PHOTOS_CREDENTIALS_FILE = DATA_DIR / "google_photos_credentials.json"
GOOGLE_PHOTOS_TOKEN_FILE = DATA_DIR / "google_photos_token.json"
GOOGLE_ALBUMS_FILE = DATA_DIR / "google_albums.json"
PAINTS_FILE = DATA_DIR / "paints.json"

# Google Photos OAuth scopes - using Google Photos Picker API
# Note: photoslibrary.readonly was deprecated on March 31, 2025
GOOGLE_PHOTOS_SCOPES = [
    'https://www.googleapis.com/auth/photospicker.mediaitems.readonly'
]

# Initialize data files
def init_data_files():
    if not SKILLS_FILE.exists():
        default_skills = [
            'Drapery', 'Drawing Hands', 'Drawing Feet', 'Drawing Volumes',
            '2 Point Perspective', '3 Point Perspective', 'Cubical Perspective',
            'Spherical Perspective', 'High Horizon Perspective', 'Low Horizon Perspective',
            'People in Landscape with Perspective', 'Foreshortening with Perspective',
            'Foreshortening with Value', 'Composition', 'Portraiture'
        ]
        SKILLS_FILE.write_text(json.dumps(default_skills, indent=2))
    
    if not METADATA_FILE.exists():
        METADATA_FILE.write_text(json.dumps({"images": {}, "artwork": {}}, indent=2))
    
    if not CRITIQUES_FILE.exists():
        CRITIQUES_FILE.write_text(json.dumps([], indent=2))
    
    if not PRACTICE_SESSIONS_FILE.exists():
        PRACTICE_SESSIONS_FILE.write_text(json.dumps([], indent=2))

    if not DRAWINGS_FILE.exists():
        DRAWINGS_FILE.write_text(json.dumps([], indent=2))

    if not IMAGE_INDEX_FILE.exists():
        IMAGE_INDEX_FILE.write_text(json.dumps({
            "images": [],
            "last_updated": None,
            "total_indexed": 0
        }, indent=2))

    if not GOOGLE_ALBUMS_FILE.exists():
        GOOGLE_ALBUMS_FILE.write_text(json.dumps({
            "synced_albums": [],
            "last_sync": None
        }, indent=2))

    if not PAINTS_FILE.exists():
        PAINTS_FILE.write_text(json.dumps([], indent=2))

    # Create artwork directory
    Path(IMAGE_PATHS["artwork"]).mkdir(parents=True, exist_ok=True)

init_data_files()

# ============= ART MOVEMENTS DATABASE =============
ART_MOVEMENTS = {
    "Social Realism": {
        "description": "Art depicting the struggles of working people and social injustice",
        "key_characteristics": [
            "Focus on everyday life of workers, farmers, and marginalized communities",
            "Documentary-style realism emphasizing truth over idealization",
            "Strong narrative content highlighting social inequalities",
            "Often features industrial settings, labor, or urban poverty",
            "Muted, earthy color palette reflecting harsh realities"
        ],
        "guidance": "To achieve Social Realist aesthetics: Choose subjects from everyday working life; avoid romanticization; use straightforward, honest depiction; emphasize the dignity of labor; include contextual details that reveal social conditions; use lighting that feels natural and unmanipulated; favor compositions that place subjects in their social environment rather than isolating them."
    },
    "Mexican Muralism": {
        "description": "Large-scale public art addressing social and political themes",
        "key_characteristics": [
            "Monumental scale with bold, dramatic compositions",
            "Themes of revolution, indigenous rights, and social justice",
            "融合 of pre-Columbian and European artistic traditions",
            "Strong linear design and dynamic movement",
            "Vibrant colors symbolizing cultural identity"
        ],
        "guidance": "To work toward Mexican Muralist style: Create bold, dynamic compositions with strong diagonals; incorporate symbolic elements representing social struggles; use vibrant, culturally significant colors; design with public visibility in mind; integrate historical and contemporary narratives; emphasize heroic scale and gestures; connect individual figures to collective movements."
    },
    "Harlem Renaissance": {
        "description": "African American cultural movement celebrating Black identity and experience",
        "key_characteristics": [
            "Celebration of Black culture, beauty, and dignity",
            "Synthesis of African artistic traditions with modernism",
            "Jazz-influenced rhythm and improvisation in visual composition",
            "Portraits emphasizing humanity and individuality",
            "Rich, warm color palettes honoring Black skin tones"
        ],
        "guidance": "To embrace Harlem Renaissance aesthetics: Center Black subjects with dignity and complexity; incorporate African design motifs and patterns; use warm, rich colors that celebrate diverse skin tones; create rhythmic, musical compositions; balance modernist techniques with cultural specificity; emphasize community and cultural pride; challenge stereotypical representations."
    },
    "Feminist Art": {
        "description": "Art challenging patriarchal structures and celebrating women's experiences",
        "key_characteristics": [
            "Subject matter from women's lived experiences",
            "Reclamation of traditionally 'feminine' materials and techniques",
            "Challenge to male-dominated art historical narratives",
            "Body-positive and diverse representations",
            "Collaborative and community-oriented practices"
        ],
        "guidance": "To develop Feminist Art approaches: Center women's perspectives and experiences; question traditional beauty standards; explore domestic and private spaces as sites of meaning; embrace crafts and materials historically devalued; create work that speaks to diverse women's identities; challenge the male gaze; consider collaborative creation processes."
    },
    "Chicano Art Movement": {
        "description": "Mexican-American art asserting cultural identity and civil rights",
        "key_characteristics": [
            "Blending of indigenous, Mexican, and American cultural symbols",
            "Bold graphics influenced by poster and print traditions",
            "Themes of immigration, labor rights, and cultural pride",
            "Use of Spanish language and bilingual text",
            "Bright, symbolic color choices"
        ],
        "guidance": "To work in Chicano Art tradition: Incorporate cultural symbols (Aztec, Catholic, American); use bold, graphic design elements; address issues of identity and borders; include text in Spanish or bilingually; draw from lowrider, tattoo, and street art aesthetics; celebrate mestizo heritage; make work accessible to community."
    },
    "Black Arts Movement": {
        "description": "Radical Black aesthetic linked to Black Power movement",
        "key_characteristics": [
            "Explicitly political content supporting Black liberation",
            "Afrocentric imagery and symbolism",
            "Community-based and accessible art practices",
            "Bold, confrontational aesthetics",
            "Integration of African design principles"
        ],
        "guidance": "To align with Black Arts Movement: Create unapologetically political work; use African and African American cultural symbols; make art accessible to Black communities; employ bold, assertive visual language; challenge white aesthetic norms; center Black joy and resistance; consider art as activism."
    },
    "Guerrilla Girls/Activist Art": {
        "description": "Anonymous collective using art to expose discrimination",
        "key_characteristics": [
            "Data-driven visual activism",
            "Humor and wit to convey serious messages",
            "Public space interventions",
            "Bold typography and graphic design",
            "Focus on institutional critique"
        ],
        "guidance": "To create Guerrilla Girls-style activist art: Use facts and statistics visually; employ humor to make difficult subjects approachable; create work for public spaces; use clear, bold graphics; maintain focus on systemic issues; challenge institutions directly; make information accessible and shareable."
    },
    "AIDS Activism/ACT UP Aesthetic": {
        "description": "Graphic activism during AIDS crisis demanding action and visibility",
        "key_characteristics": [
            "Urgent, direct messaging ('SILENCE = DEATH')",
            "High contrast, readable graphics for protests",
            "Pink triangle and other reclaimed symbols",
            "Agitprop poster traditions",
            "Community collaboration and rapid response"
        ],
        "guidance": "To work in AIDS activism aesthetic: Create clear, urgent messaging; use high-contrast, legible design; design for reproduction and distribution; reclaim oppressive symbols; make work quickly in response to current crises; prioritize communication over decoration; center affected communities."
    },
    "Expressionism": {
        "description": "Emotional intensity over realistic representation",
        "key_characteristics": [
            "Distorted forms expressing inner feelings",
            "Intense, non-naturalistic colors",
            "Visible, energetic brushwork",
            "Themes of anxiety, alienation, and raw emotion",
            "Rejection of academic techniques"
        ],
        "guidance": "To develop Expressionist style: Prioritize emotional truth over visual accuracy; use color for emotional impact rather than realism; let brushstrokes show energy and feeling; distort forms to convey psychological states; embrace rawness and spontaneity; explore themes of human condition and inner turmoil."
    },
    "Surrealism": {
        "description": "Unconscious mind and dreams as source of truth",
        "key_characteristics": [
            "Unexpected juxtapositions and dreamlike imagery",
            "Automatism and chance operations",
            "Challenge to rational thought and bourgeois values",
            "Symbolic, psychologically charged content",
            "Hyperrealistic technique with impossible content"
        ],
        "guidance": "To work Surrealistically: Combine unrelated objects in strange ways; tap into dreams and unconscious imagery; use automatic drawing or writing techniques; create technically refined but logically impossible scenes; explore Freudian symbolism; challenge viewer's expectations of reality."
    },
    "Pop Art": {
        "description": "Mass culture and consumerism as high art subjects",
        "key_characteristics": [
            "Imagery from advertising, comics, and mass media",
            "Bright, flat colors and bold outlines",
            "Repetition and serial imagery",
            "Critique of consumer culture through appropriation",
            "Accessible, democratic art language"
        ],
        "guidance": "To create Pop Art: Appropriate images from popular culture; use bright, commercial color schemes; employ repetition and multiples; keep compositions flat and graphic; reference advertising and media aesthetics; blur lines between high and low culture; maintain ironic distance."
    },
    "Street Art/Graffiti": {
        "description": "Public art claiming urban space and voice",
        "key_characteristics": [
            "Bold, large-scale work in public spaces",
            "Tag-based calligraphy and letter design",
            "Stencils, wheat paste, and rapid techniques",
            "Community identity and territorial marking",
            "Anti-authoritarian, democratic access"
        ],
        "guidance": "To work in Street Art tradition: Design for large scale and distance viewing; develop distinctive personal style/tag; use techniques allowing quick execution; consider public site specificity; make work that speaks to local community; embrace impermanence; challenge ownership of public space."
    },
    "Documentary Photography Tradition": {
        "description": "Truth-telling through photographic evidence of social conditions",
        "key_characteristics": [
            "Unstaged, candid moments capturing reality",
            "Focus on social issues and human conditions",
            "Black and white for timelessness and seriousness",
            "Intimate access to subjects' lives",
            "Ethical relationship with subjects"
        ],
        "guidance": "To develop documentary approach: Build trust with subjects; capture unposed, authentic moments; focus on social significance; use available light; consider ethical implications; tell stories of marginalized communities; maintain journalistic integrity; let subjects retain dignity."
    },
    "Agitprop/Constructivism": {
        "description": "Revolutionary art in service of social transformation",
        "key_characteristics": [
            "Geometric abstraction with political purpose",
            "Bold diagonals suggesting dynamic change",
            "Limited color palette (red, black, white)",
            "Typography integrated with image",
            "Emphasis on reproducibility and distribution"
        ],
        "guidance": "To create Agitprop/Constructivist work: Use strong diagonal compositions; limit palette to red, black, white; integrate bold typography; design for poster format; emphasize geometric forms; create clear political messaging; prioritize mass reproduction over unique art objects."
    },
    "Impressionism": {
        "description": "Capturing fleeting moments of light and modern life",
        "key_characteristics": [
            "Visible, broken brushstrokes",
            "Emphasis on light and its changing qualities",
            "Ordinary, contemporary subjects",
            "Bright, unmixed colors",
            "Outdoor painting (plein air)"
        ],
        "guidance": "To paint Impressionistically: Work quickly to capture changing light; use broken color and visible brushwork; paint outdoors when possible; depict modern, everyday scenes; avoid black; let colors mix optically on canvas; prioritize immediate visual experience over detail."
    }
}

# ============= AI MODEL INITIALIZATION =============
# Initialize BLIP model for image understanding (lazy loading)
_blip_processor = None
_blip_model = None

def get_blip_model():
    """Lazy load BLIP model for image captioning and analysis"""
    global _blip_processor, _blip_model

    if _blip_processor is None or _blip_model is None:
        logger.info("Loading BLIP model for image analysis...")
        _blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        _blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

        # Move to GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _blip_model = _blip_model.to(device)
        logger.info(f"BLIP model loaded on {device}")

    return _blip_processor, _blip_model

# Initialize CLIP model for image embeddings and search (lazy loading)
_clip_processor = None
_clip_model = None

def get_clip_model():
    """Lazy load CLIP model for image embeddings"""
    global _clip_processor, _clip_model

    if _clip_processor is None or _clip_model is None:
        logger.info("Loading CLIP model for image search...")
        _clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        _clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

        # Move to GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _clip_model = _clip_model.to(device)
        logger.info(f"CLIP model loaded on {device}")

    return _clip_processor, _clip_model

def get_image_embedding(image_path: str) -> np.ndarray:
    """Generate CLIP embedding for an image"""
    processor, model = get_clip_model()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        image = Image.open(image_path).convert('RGB')
        inputs = processor(images=image, return_tensors="pt").to(device)

        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
            # Normalize the embedding
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        return image_features.cpu().numpy()[0]
    except Exception as e:
        logger.error(f"Error generating embedding for {image_path}: {e}")
        return None

def get_text_embedding(text: str) -> np.ndarray:
    """Generate CLIP embedding for text query"""
    processor, model = get_clip_model()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    inputs = processor(text=[text], return_tensors="pt", padding=True).to(device)

    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
        # Normalize the embedding
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

    return text_features.cpu().numpy()[0]

def analyze_image_with_blip(image_path: str, prompt: str = None) -> str:
    """Analyze image using BLIP model with optional prompt"""
    processor, model = get_blip_model()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load and process image
    image = Image.open(image_path).convert('RGB')

    if prompt:
        # Conditional generation with prompt
        inputs = processor(image, prompt, return_tensors="pt").to(device)
    else:
        # Unconditional image captioning
        inputs = processor(image, return_tensors="pt").to(device)

    # Generate caption
    with torch.no_grad():
        output = model.generate(**inputs, max_length=100, num_beams=5)

    caption = processor.decode(output[0], skip_special_tokens=True)
    return caption

def analyze_image_colors(image: Image.Image) -> dict:
    """Analyze color composition of the image"""
    # Resize for faster processing
    img_small = image.resize((100, 100))
    pixels = list(img_small.getdata())

    # Calculate average brightness
    brightness_values = [sum(p[:3])/3 for p in pixels]
    avg_brightness = sum(brightness_values) / len(brightness_values)

    # Determine if high contrast
    brightness_std = (sum((b - avg_brightness)**2 for b in brightness_values) / len(brightness_values)) ** 0.5

    # Color presence
    colors = {
        'red': sum(1 for p in pixels if p[0] > p[1] + 30 and p[0] > p[2] + 30),
        'green': sum(1 for p in pixels if p[1] > p[0] + 30 and p[1] > p[2] + 30),
        'blue': sum(1 for p in pixels if p[2] > p[0] + 30 and p[2] > p[1] + 30),
        'warm': sum(1 for p in pixels if p[0] + p[1] > p[2] * 1.5),
        'cool': sum(1 for p in pixels if p[2] > (p[0] + p[1]) / 2)
    }

    return {
        'brightness': 'bright' if avg_brightness > 150 else 'dark' if avg_brightness < 100 else 'balanced',
        'contrast': 'high' if brightness_std > 60 else 'low' if brightness_std < 30 else 'moderate',
        'dominant_temp': 'warm' if colors['warm'] > colors['cool'] else 'cool',
        'has_strong_red': colors['red'] > 1000,
        'has_strong_blue': colors['blue'] > 1000,
        'has_strong_green': colors['green'] > 1000
    }

def generate_art_critique(image_path: str) -> dict:
    """Generate comprehensive art critique using AI models"""
    logger.info(f"Generating AI critique for: {image_path}")

    # Load image for analysis
    image = Image.open(image_path).convert('RGB')
    width, height = image.size
    aspect_ratio = width / height

    # 1. DESCRIPTION - Using BLIP for detailed caption
    description_base = analyze_image_with_blip(image_path)

    # Add technical details
    color_analysis = analyze_image_colors(image)

    orientation = "portrait" if aspect_ratio < 0.9 else "landscape" if aspect_ratio > 1.1 else "square"

    description = (
        f"This {orientation} format artwork ({width}x{height} pixels) depicts {description_base}. "
        f"The piece exhibits {color_analysis['contrast']} contrast with {color_analysis['brightness']} overall tonality. "
        f"The color palette leans toward {color_analysis['dominant_temp']} tones, creating a specific atmospheric quality."
    )

    # 2. COMPOSITION ANALYSIS - Detailed spatial analysis
    try:
        composition_base = analyze_image_with_blip(
            image_path,
            "describe the composition and arrangement of elements in this artwork"
        )

        spatial_description = analyze_image_with_blip(
            image_path,
            "describe where objects are positioned in this image and how they relate to each other"
        )

        # Build comprehensive composition commentary
        composition_parts = []

        # Spatial arrangement
        composition_parts.append(f"**Spatial Arrangement**: {spatial_description}")

        # Visual flow based on orientation
        if orientation == "portrait":
            composition_parts.append(
                "The vertical format creates an upward visual flow, drawing the eye from bottom to top. "
                "This orientation naturally emphasizes height and can suggest themes of growth, ascension, or human presence."
            )
        elif orientation == "landscape":
            composition_parts.append(
                "The horizontal format creates lateral visual movement, guiding the eye across the composition. "
                "This orientation naturally emphasizes breadth and expanse, ideal for panoramic views or narrative sequences."
            )
        else:
            composition_parts.append(
                "The square format provides equal weight to all directions, creating a centered, balanced composition. "
                "This format naturally draws attention to the center while maintaining equilibrium."
            )

        # Additional compositional observations
        composition_parts.append(f"{composition_base}")

        # Rule of thirds/golden ratio inference based on orientation
        if aspect_ratio > 1.4 and aspect_ratio < 1.8:
            composition_parts.append(
                "The aspect ratio suggests potential use of the golden ratio or rule of thirds for compositional balance."
            )

        composition = " ".join(composition_parts)

    except Exception as e:
        logger.error(f"Error in composition analysis: {e}")
        composition = (
            f"The {orientation} composition organizes visual elements across the picture plane. "
            f"Objects are arranged to create visual interest and guide the viewer's eye through the work. "
            f"The spatial relationships between elements contribute to the overall visual narrative."
        )

    # 3. MOOD ANALYSIS - Dedicated emotional/atmospheric analysis
    try:
        mood_base = analyze_image_with_blip(
            image_path,
            "what is the mood and emotional quality of this artwork"
        )

        atmosphere_description = analyze_image_with_blip(
            image_path,
            "describe the atmosphere and feeling this image conveys"
        )

        # Build mood commentary with color psychology
        mood_parts = []

        mood_parts.append(f"**Emotional Quality**: {mood_base}")
        mood_parts.append(f"**Atmospheric Presence**: {atmosphere_description}")

        # Analyze mood through color temperature
        if color_analysis['dominant_temp'] == 'warm':
            mood_parts.append(
                "The warm color palette (reds, oranges, yellows) creates feelings of energy, passion, and vitality. "
                "Warm tones tend to advance visually, creating intimacy and emotional intensity."
            )
        else:
            mood_parts.append(
                "The cool color palette (blues, greens, purples) evokes feelings of calm, contemplation, and serenity. "
                "Cool tones tend to recede visually, creating space, distance, and tranquility."
            )

        # Mood through contrast
        if color_analysis['contrast'] == 'high':
            mood_parts.append(
                "The high contrast creates dramatic tension and emotional impact, suggesting conflict, dynamism, or strong emotional states."
            )
        elif color_analysis['contrast'] == 'low':
            mood_parts.append(
                "The low contrast creates a harmonious, peaceful mood, suggesting unity, subtlety, or dreamlike states."
            )
        else:
            mood_parts.append(
                "The moderate contrast balances visual interest with harmony, creating an accessible and engaging mood."
            )

        # Brightness and mood
        if color_analysis['brightness'] == 'bright':
            mood_parts.append("The bright tonality suggests optimism, clarity, or ethereal qualities.")
        elif color_analysis['brightness'] == 'dark':
            mood_parts.append("The dark tonality suggests mystery, introspection, or dramatic gravitas.")
        else:
            mood_parts.append("The balanced tonality creates a naturalistic, grounded emotional quality.")

        mood = " ".join(mood_parts)

    except Exception as e:
        logger.error(f"Error in mood analysis: {e}")
        mood = (
            f"The artwork conveys a {color_analysis['dominant_temp']} emotional atmosphere through its color choices. "
            f"The {color_analysis['contrast']} contrast and {color_analysis['brightness']} values work together to create "
            f"a specific mood that influences viewer perception and emotional response."
        )

    # 4. ANALYSIS - Using BLIP with prompts for design elements
    try:
        # Analyze design principles
        analysis_parts = []

        analysis_parts.append(
            f"**Value & Contrast**: The artwork demonstrates {color_analysis['contrast']} contrast, "
            f"with {color_analysis['brightness']} values that {'create dramatic focal points' if color_analysis['contrast'] == 'high' else 'maintain visual harmony'}."
        )

        if color_analysis['has_strong_red'] or color_analysis['has_strong_blue'] or color_analysis['has_strong_green']:
            color_notes = []
            if color_analysis['has_strong_red']: color_notes.append("strong reds")
            if color_analysis['has_strong_blue']: color_notes.append("vivid blues")
            if color_analysis['has_strong_green']: color_notes.append("prominent greens")
            analysis_parts.append(
                f"**Color Usage**: The presence of {', '.join(color_notes)} provides visual interest and directs attention. "
                f"These color choices create focal points and influence the overall mood."
            )

        analysis = " ".join(analysis_parts)

    except Exception as e:
        logger.error(f"Error in analysis phase: {e}")
        analysis = (
            f"The artwork demonstrates {color_analysis['contrast']} contrast with {color_analysis['brightness']} values. "
            f"The {orientation} format and {color_analysis['dominant_temp']} color temperature work together to create visual impact."
        )

    # 5. INTERPRETATION - Using BLIP for thematic understanding
    try:
        theme_analysis = analyze_image_with_blip(
            image_path,
            "what themes or ideas does this artwork explore"
        )

        interpretation = (
            f"The artist appears to be exploring {theme_analysis}. "
            f"The compositional choices work in concert with the color palette and mood to suggest deeper meaning. "
            f"The work invites viewers to engage with both its formal qualities and implied narrative content, "
            f"creating a dialogue between visual presentation and conceptual interpretation."
        )

    except Exception as e:
        logger.error(f"Error in interpretation phase: {e}")
        interpretation = (
            f"The work suggests deliberate exploration of visual elements and their expressive potential. "
            f"The {color_analysis['dominant_temp']} tonality and {color_analysis['contrast']} contrast work together "
            f"to create layers of meaning, inviting contemplation and personal interpretation."
        )

    # 6. JUDGMENT - Synthesized evaluation
    strengths = []
    areas_for_growth = []

    # Evaluate based on technical execution
    if color_analysis['contrast'] in ['moderate', 'high']:
        strengths.append("effective use of value contrast to create depth and focal points")
    else:
        areas_for_growth.append("exploring stronger value contrasts to enhance visual hierarchy")

    if orientation == 'square':
        strengths.append("balanced composition that centers the viewer's attention")
    elif aspect_ratio > 2 or aspect_ratio < 0.5:
        strengths.append("bold format choice that emphasizes directional movement")

    # Add general artistic merit
    strengths.append("clear understanding of foundational design principles")
    strengths.append("thoughtful integration of mood and composition")
    areas_for_growth.append("continued experimentation with personal artistic voice and unique stylistic choices")

    judgment = (
        f"This artwork demonstrates technical competence and thoughtful composition. "
        f"**Strengths**: {'; '.join(strengths)}. "
        f"**Areas for Growth**: {'; '.join(areas_for_growth)}. "
        f"The piece successfully communicates through visual means and shows promise for further artistic development. "
        f"Continued practice with observational studies and experimental techniques will help refine the artist's unique perspective."
    )

    logger.info("AI critique generation completed")

    return {
        "description": description,
        "composition": composition,
        "mood": mood,
        "analysis": analysis,
        "interpretation": interpretation,
        "judgment": judgment
    }

# Pydantic models
class Skill(BaseModel):
    skill: str

class WarmupRequest(BaseModel):
    count: int
    skills: List[str] = []

class SessionLog(BaseModel):
    type: str
    duration: int
    skills: List[str] = []
    imageCount: int = 0
    completedAt: str

class ImageMetadata(BaseModel):
    imagePath: str
    metadata: Dict[str, Any]

class Critique(BaseModel):
    artworkPath: str
    critique: str
    skill: Optional[str] = None

class DrawingUpload(BaseModel):
    drawingId: str
    comment: Optional[str] = None

class AICritiqueRequest(BaseModel):
    drawingId: str

# Helper functions
def get_images_from_directory(directory: str, recursive: bool = True) -> List[Dict]:
    """Get all image files from a directory"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    images = []

    logger.info(f"Scanning directory: {directory} (recursive={recursive})")

    try:
        path = Path(directory)
        if not path.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return []

        logger.info(f"Directory exists: {directory}")

        if recursive:
            files = path.rglob('*')
        else:
            files = path.glob('*')

        file_count = 0
        image_count = 0

        for file_path in files:
            file_count += 1
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                if suffix in image_extensions:
                    image_count += 1
                    stat = file_path.stat()
                    images.append({
                        "path": str(file_path),
                        "name": file_path.name,
                        "directory": str(file_path.parent),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                    if image_count <= 5:  # Log first 5 images found
                        logger.info(f"  Found image: {file_path.name}")

        logger.info(f"Scanned {file_count} files, found {image_count} images in {directory}")

    except PermissionError as e:
        logger.error(f"Permission denied reading directory {directory}: {e}")
    except Exception as e:
        logger.error(f"Error reading directory {directory}: {e}", exc_info=True)

    return images

# ============= SKILLS ENDPOINTS =============

@app.get("/api/skills")
async def get_skills():
    """Get all skills"""
    skills = json.loads(SKILLS_FILE.read_text())
    return skills

@app.post("/api/skills")
async def add_skill(skill_data: Skill):
    """Add a new skill"""
    skills = json.loads(SKILLS_FILE.read_text())
    
    if skill_data.skill not in skills:
        skills.append(skill_data.skill)
        SKILLS_FILE.write_text(json.dumps(skills, indent=2))
        return {"success": True, "skills": skills}
    else:
        raise HTTPException(status_code=400, detail="Skill already exists")

@app.delete("/api/skills/{skill}")
async def delete_skill(skill: str):
    """Delete a skill"""
    skills = json.loads(SKILLS_FILE.read_text())
    
    if skill in skills:
        skills.remove(skill)
        SKILLS_FILE.write_text(json.dumps(skills, indent=2))
        return {"success": True, "skills": skills}
    else:
        raise HTTPException(status_code=404, detail="Skill not found")

# ============= IMAGE ENDPOINTS (FULLY IMPLEMENTED) =============

@app.get("/api/images/reference")
async def get_reference_images(skills: Optional[str] = Query(None)):
    """Get all reference images"""
    logger.info(f"GET /api/images/reference called with skills={skills}")
    all_images = []

    logger.info(f"Configured reference directories: {IMAGE_PATHS['reference']}")

    for directory in IMAGE_PATHS["reference"]:
        images = get_images_from_directory(directory)
        logger.info(f"Found {len(images)} images in {directory}")
        all_images.extend(images)

    # TODO: Filter by skills using metadata when implemented
    if skills:
        skill_list = skills.split(',')
        logger.info(f"Skill filtering requested but not yet implemented: {skill_list}")
        # For now, return all images. Later, filter by metadata
        pass

    logger.info(f"Returning {len(all_images)} total reference images")
    return all_images

@app.post("/api/images/warmup-session")
async def create_warmup_session(request: WarmupRequest):
    """Get random images for warmup session"""
    logger.info(f"POST /api/images/warmup-session called with count={request.count}, skills={request.skills}")
    all_images = []

    for directory in IMAGE_PATHS["reference"]:
        images = get_images_from_directory(directory)
        all_images.extend(images)

    logger.info(f"Total images available: {len(all_images)}")

    # TODO: Filter by skills using metadata when implemented
    if request.skills:
        logger.info(f"Skill filtering requested but not yet implemented: {request.skills}")
        # For now, use all images. Later, filter by metadata
        pass

    # Shuffle and select random images
    random.shuffle(all_images)
    selected = all_images[:request.count]

    logger.info(f"Selected {len(selected)} random images for warmup session")
    return selected

@app.get("/api/images/file")
async def get_image_file(path: str = Query(...)):
    """Serve a specific image file"""
    file_path = Path(path)

    # Security check - ensure path is in allowed directories
    is_allowed = False
    allowed_dirs = IMAGE_PATHS["reference"] + [IMAGE_PATHS["photos"], IMAGE_PATHS["artwork"], str(UPLOADS_DIR)]
    for allowed_dir in allowed_dirs:
        try:
            file_path.resolve().relative_to(Path(allowed_dir).resolve())
            is_allowed = True
            break
        except ValueError:
            continue

    if not is_allowed:
        raise HTTPException(status_code=403, detail="Access denied")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(file_path)

# ============= PHOTO COLLECTION ENDPOINTS =============

@app.get("/api/images/photos")
async def get_photos():
    """Get all photos from collection"""
    logger.info(f"GET /api/images/photos called")
    logger.info(f"Photos directory: {IMAGE_PATHS['photos']}")
    images = get_images_from_directory(IMAGE_PATHS["photos"], recursive=True)
    logger.info(f"Returning {len(images)} photos")
    return images

def build_image_index(force_rebuild: bool = False):
    """Build or update the image embedding index"""
    logger.info("Building image index...")

    # Load existing index
    index_data = json.loads(IMAGE_INDEX_FILE.read_text())
    existing_images = {img["path"]: img for img in index_data.get("images", [])}

    # Get all photos
    all_photos = get_images_from_directory(IMAGE_PATHS["photos"], recursive=True)
    logger.info(f"Found {len(all_photos)} photos")

    # Determine which images need embeddings
    images_to_process = []
    for photo in all_photos:
        photo_path = photo["path"]
        if force_rebuild or photo_path not in existing_images:
            images_to_process.append(photo)

    if not images_to_process:
        logger.info("No new images to process")
        return index_data

    logger.info(f"Processing {len(images_to_process)} images...")

    # Generate embeddings for new images
    new_embeddings = []
    updated_images = list(existing_images.values())

    for i, photo in enumerate(images_to_process):
        if i % 10 == 0:
            logger.info(f"Processing image {i+1}/{len(images_to_process)}")

        embedding = get_image_embedding(photo["path"])
        if embedding is not None:
            photo["embedding_index"] = len(existing_images) + len(new_embeddings)
            updated_images.append(photo)
            new_embeddings.append(embedding)

    # Load existing embeddings if any
    if EMBEDDINGS_FILE.exists() and not force_rebuild:
        existing_embeddings = np.load(str(EMBEDDINGS_FILE))
        all_embeddings = np.vstack([existing_embeddings, np.array(new_embeddings)])
    else:
        all_embeddings = np.array(new_embeddings)

    # Save embeddings and index
    np.save(str(EMBEDDINGS_FILE), all_embeddings)

    index_data["images"] = updated_images
    index_data["total_indexed"] = len(updated_images)
    index_data["last_updated"] = datetime.now().isoformat()
    IMAGE_INDEX_FILE.write_text(json.dumps(index_data, indent=2))

    logger.info(f"Image index built: {len(updated_images)} images indexed")
    return index_data

@app.post("/api/images/search")
async def search_images(request: dict):
    """AI-powered semantic image search"""
    query = request.get("query", "")
    filters = request.get("filters", {})
    max_results = request.get("max_results", 50)

    if not query:
        return {"error": "Query text is required"}

    # Check if index exists
    if not EMBEDDINGS_FILE.exists() or not IMAGE_INDEX_FILE.exists():
        logger.info("Index doesn't exist, building...")
        build_image_index()

    # Load index
    index_data = json.loads(IMAGE_INDEX_FILE.read_text())
    embeddings = np.load(str(EMBEDDINGS_FILE))

    if len(index_data["images"]) == 0:
        return {"results": [], "total": 0}

    # Generate query embedding
    query_embedding = get_text_embedding(query)
    query_embedding = query_embedding.reshape(1, -1)

    # Compute similarities
    similarities = cosine_similarity(query_embedding, embeddings)[0]

    # Get top results
    top_indices = np.argsort(similarities)[::-1][:max_results]

    results = []
    for idx in top_indices:
        if idx < len(index_data["images"]):
            image = index_data["images"][idx].copy()
            image["similarity_score"] = float(similarities[idx])

            # Apply filters if provided
            if filters:
                # TODO: Add filter logic based on metadata
                pass

            results.append(image)

    return {
        "results": results,
        "total": len(results),
        "query": query
    }

@app.post("/api/images/rebuild-index")
async def rebuild_index(force: bool = False):
    """Rebuild the image search index"""
    try:
        result = build_image_index(force_rebuild=force)
        return {
            "success": True,
            "total_indexed": result["total_indexed"],
            "last_updated": result["last_updated"]
        }
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}", exc_info=True)
        return {"error": str(e)}

@app.get("/api/images/index-status")
async def get_index_status():
    """Get the current status of the image index"""
    if not IMAGE_INDEX_FILE.exists():
        return {
            "indexed": False,
            "total_indexed": 0,
            "last_updated": None
        }

    index_data = json.loads(IMAGE_INDEX_FILE.read_text())
    return {
        "indexed": True,
        "total_indexed": index_data.get("total_indexed", 0),
        "last_updated": index_data.get("last_updated")
    }

@app.post("/api/images/tag")
async def tag_image():
    """Tag image with metadata - STUB"""
    # TODO: Implement metadata tagging
    return {"error": "Not implemented yet"}

# ============= ARTWORK/DRAWING ENDPOINTS =============

@app.post("/api/drawings/upload")
async def upload_drawing(
    file: UploadFile = File(...),
    comment: Optional[str] = None
):
    """Upload a new drawing for critique"""
    try:
        # Generate unique ID for drawing
        drawing_id = str(int(datetime.now().timestamp() * 1000))

        # Save the file
        file_extension = Path(file.filename).suffix
        filename = f"{drawing_id}{file_extension}"
        file_path = UPLOADS_DIR / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load drawings database
        drawings = json.loads(DRAWINGS_FILE.read_text())

        # Create drawing record
        new_drawing = {
            "id": drawing_id,
            "filename": filename,
            "path": str(file_path),
            "originalName": file.filename,
            "comment": comment or "",
            "uploadedAt": datetime.now().isoformat(),
            "critique": None
        }

        drawings.append(new_drawing)
        DRAWINGS_FILE.write_text(json.dumps(drawings, indent=2))

        logger.info(f"Drawing uploaded: {drawing_id}")
        return {"success": True, "drawing": new_drawing}

    except Exception as e:
        logger.error(f"Error uploading drawing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/drawings")
async def get_drawings():
    """Get all uploaded drawings"""
    drawings = json.loads(DRAWINGS_FILE.read_text())
    return drawings

@app.get("/api/drawings/{drawing_id}")
async def get_drawing_detail(drawing_id: str):
    """Get specific drawing details"""
    drawings = json.loads(DRAWINGS_FILE.read_text())
    drawing = next((d for d in drawings if d["id"] == drawing_id), None)

    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    return drawing

@app.put("/api/drawings/{drawing_id}/comment")
async def update_drawing_comment(drawing_id: str, data: dict):
    """Update drawing comment"""
    drawings = json.loads(DRAWINGS_FILE.read_text())
    drawing = next((d for d in drawings if d["id"] == drawing_id), None)

    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    drawing["comment"] = data.get("comment", "")
    drawing["updatedAt"] = datetime.now().isoformat()

    DRAWINGS_FILE.write_text(json.dumps(drawings, indent=2))
    return {"success": True, "drawing": drawing}

@app.delete("/api/drawings/{drawing_id}")
async def delete_drawing(drawing_id: str):
    """Delete a drawing"""
    drawings = json.loads(DRAWINGS_FILE.read_text())
    drawing = next((d for d in drawings if d["id"] == drawing_id), None)

    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    # Delete file
    file_path = Path(drawing["path"])
    if file_path.exists():
        file_path.unlink()

    # Remove from database
    drawings = [d for d in drawings if d["id"] != drawing_id]
    DRAWINGS_FILE.write_text(json.dumps(drawings, indent=2))

    return {"success": True}

# Serve drawing files
@app.get("/api/drawings/{drawing_id}/file")
async def get_drawing_file(drawing_id: str):
    """Serve the drawing image file"""
    drawings = json.loads(DRAWINGS_FILE.read_text())
    drawing = next((d for d in drawings if d["id"] == drawing_id), None)

    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    file_path = Path(drawing["path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)

# ============= ART MOVEMENTS ENDPOINTS =============

@app.get("/api/art-movements")
async def get_art_movements():
    """Get list of all art movements"""
    movements = []
    for name, data in ART_MOVEMENTS.items():
        movements.append({
            "name": name,
            "description": data["description"]
        })
    return movements

@app.get("/api/art-movements/{movement_name}")
async def get_movement_details(movement_name: str):
    """Get detailed information about a specific art movement"""
    # URL decode and match movement name
    movement_key = movement_name.replace("-", " ").replace("_", " ")

    for key in ART_MOVEMENTS.keys():
        if key.lower() == movement_key.lower():
            return {
                "name": key,
                **ART_MOVEMENTS[key]
            }

    raise HTTPException(status_code=404, detail="Art movement not found")

@app.post("/api/art-movements/compare")
async def compare_to_movement(data: dict):
    """Compare artwork to specific art movement and provide guidance"""
    drawing_id = data.get("drawingId")
    movement_name = data.get("movementName")

    if not drawing_id or not movement_name:
        raise HTTPException(status_code=400, detail="drawingId and movementName required")

    # Load drawing
    drawings = json.loads(DRAWINGS_FILE.read_text())
    drawing = next((d for d in drawings if d["id"] == drawing_id), None)

    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")

    # Find movement
    movement = None
    for key in ART_MOVEMENTS.keys():
        if key.lower() == movement_name.lower().replace("-", " ").replace("_", " "):
            movement = ART_MOVEMENTS[key]
            movement_key = key
            break

    if not movement:
        raise HTTPException(status_code=404, detail="Art movement not found")

    # Generate comparison and guidance
    guidance_text = (
        f"**Comparing to {movement_key}**\n\n"
        f"{movement['description']}\n\n"
        f"**Key Characteristics of {movement_key}:**\n"
    )

    for char in movement['key_characteristics']:
        guidance_text += f"• {char}\n"

    guidance_text += f"\n**How to Move Closer to {movement_key}:**\n\n{movement['guidance']}"

    logger.info(f"Generated movement comparison for {drawing_id} to {movement_key}")

    return {
        "success": True,
        "movement": movement_key,
        "guidance": guidance_text
    }

# ============= CRITIQUE ENDPOINTS =============

@app.post("/api/critiques")
async def save_critique(critique: Critique):
    """Save a critique"""
    critiques = json.loads(CRITIQUES_FILE.read_text())
    
    new_critique = {
        "id": str(int(datetime.now().timestamp() * 1000)),
        "artworkPath": critique.artworkPath,
        "skill": critique.skill,
        "critique": critique.critique,
        "createdAt": datetime.now().isoformat()
    }
    
    critiques.append(new_critique)
    CRITIQUES_FILE.write_text(json.dumps(critiques, indent=2))
    
    return {"success": True, "critique": new_critique}

@app.get("/api/critiques/{artwork_path:path}")
async def get_critiques(artwork_path: str):
    """Get critiques for specific artwork"""
    critiques = json.loads(CRITIQUES_FILE.read_text())
    artwork_critiques = [c for c in critiques if c["artworkPath"] == artwork_path]
    return artwork_critiques

@app.post("/api/critiques/batch")
async def batch_critique():
    """Batch critique by skill - STUB"""
    # TODO: Implement batch critique
    return {"error": "Not implemented yet"}

@app.post("/api/critiques/ai")
async def ai_critique(request: AICritiqueRequest):
    """Generate AI-powered art critique using HuggingFace BLIP model"""
    try:
        # Load the drawing
        drawings = json.loads(DRAWINGS_FILE.read_text())
        drawing = next((d for d in drawings if d["id"] == request.drawingId), None)

        if not drawing:
            raise HTTPException(status_code=404, detail="Drawing not found")

        # Load image
        image_path = Path(drawing["path"])
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image file not found")

        # Generate comprehensive AI critique using BLIP model
        logger.info(f"Starting AI critique generation for drawing: {request.drawingId}")
        critique = generate_art_critique(str(image_path))

        # Update drawing with critique
        drawing["critique"] = critique
        drawing["critiqueGeneratedAt"] = datetime.now().isoformat()

        # Save updated drawing
        for i, d in enumerate(drawings):
            if d["id"] == request.drawingId:
                drawings[i] = drawing
                break

        DRAWINGS_FILE.write_text(json.dumps(drawings, indent=2))

        logger.info(f"AI critique successfully generated for drawing: {request.drawingId}")
        return {"success": True, "critique": critique}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating AI critique: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ============= PRACTICE SESSION ENDPOINTS =============

@app.post("/api/sessions/log")
async def log_session(session: SessionLog):
    """Log a practice session"""
    sessions = json.loads(PRACTICE_SESSIONS_FILE.read_text())
    
    completed_at = datetime.fromisoformat(session.completedAt.replace('Z', '+00:00'))
    
    new_session = {
        "id": str(int(datetime.now().timestamp() * 1000)),
        "type": session.type,
        "duration": session.duration,
        "skills": session.skills,
        "imageCount": session.imageCount,
        "completedAt": session.completedAt,
        "date": completed_at.strftime("%Y-%m-%d")
    }
    
    sessions.append(new_session)
    PRACTICE_SESSIONS_FILE.write_text(json.dumps(sessions, indent=2))
    
    return {"success": True, "session": new_session}

@app.get("/api/sessions")
async def get_sessions(
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    skill: Optional[str] = None,
    type: Optional[str] = None
):
    """Get practice sessions with filters"""
    sessions = json.loads(PRACTICE_SESSIONS_FILE.read_text())

    # Apply filters
    if startDate:
        sessions = [s for s in sessions if s["date"] >= startDate]
    if endDate:
        sessions = [s for s in sessions if s["date"] <= endDate]
    if skill:
        sessions = [s for s in sessions if skill in s["skills"]]
    if type:
        sessions = [s for s in sessions if s["type"] == type]

    return sessions

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific practice session"""
    sessions = json.loads(PRACTICE_SESSIONS_FILE.read_text())

    # Find and remove the session
    original_count = len(sessions)
    sessions = [s for s in sessions if s["id"] != session_id]

    if len(sessions) == original_count:
        raise HTTPException(status_code=404, detail="Session not found")

    # Save updated sessions
    PRACTICE_SESSIONS_FILE.write_text(json.dumps(sessions, indent=2))

    logger.info(f"Deleted practice session: {session_id}")
    return {"success": True, "message": "Session deleted successfully"}

# ============= ANALYTICS ENDPOINTS =============

@app.get("/api/stats/practice")
async def get_practice_stats(period: str = "month"):
    """Get practice statistics"""
    sessions = json.loads(PRACTICE_SESSIONS_FILE.read_text())
    
    # Calculate date range
    now = datetime.now()
    if period == "week":
        start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    elif period == "month":
        start_date = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    elif period == "year":
        start_date = (now - timedelta(days=365)).strftime("%Y-%m-%d")
    else:
        start_date = "1970-01-01"
    
    filtered_sessions = [s for s in sessions if s["date"] >= start_date]
    
    # Calculate statistics
    total_sessions = len(filtered_sessions)
    total_minutes = sum(s.get("duration", 0) for s in filtered_sessions)
    total_images = sum(s.get("imageCount", 0) for s in filtered_sessions)
    
    # Sessions by type
    sessions_by_type = {}
    for s in filtered_sessions:
        sessions_by_type[s["type"]] = sessions_by_type.get(s["type"], 0) + 1
    
    # Practice by skill
    practice_by_skill = {}
    for s in filtered_sessions:
        for skill in s.get("skills", []):
            if skill not in practice_by_skill:
                practice_by_skill[skill] = {"sessions": 0, "minutes": 0, "images": 0}
            practice_by_skill[skill]["sessions"] += 1
            practice_by_skill[skill]["minutes"] += s.get("duration", 0)
            practice_by_skill[skill]["images"] += s.get("imageCount", 0)
    
    # Practice by day
    practice_by_day = {}
    for s in filtered_sessions:
        date = s["date"]
        if date not in practice_by_day:
            practice_by_day[date] = {"sessions": 0, "minutes": 0, "images": 0}
        practice_by_day[date]["sessions"] += 1
        practice_by_day[date]["minutes"] += s.get("duration", 0)
        practice_by_day[date]["images"] += s.get("imageCount", 0)
    
    # Calculate streak
    current_streak = 0
    check_date = now.date()
    while True:
        date_str = check_date.strftime("%Y-%m-%d")
        has_practice = any(s["date"] == date_str for s in sessions)
        
        if has_practice:
            current_streak += 1
            check_date = check_date - timedelta(days=1)
        elif current_streak == 0 and date_str == now.strftime("%Y-%m-%d"):
            check_date = check_date - timedelta(days=1)
        else:
            break
    
    return {
        "period": period,
        "totalSessions": total_sessions,
        "totalMinutes": total_minutes,
        "totalHours": round(total_minutes / 60, 1),
        "totalImages": total_images,
        "averageSessionMinutes": round(total_minutes / total_sessions) if total_sessions > 0 else 0,
        "sessionsByType": sessions_by_type,
        "practiceBySkill": practice_by_skill,
        "practiceByDay": practice_by_day,
        "currentStreak": current_streak
    }

@app.get("/api/stats/artwork")
async def get_artwork_stats():
    """Get artwork statistics - STUB"""
    # TODO: Implement artwork statistics
    return {
        "totalArtwork": 0,
        "recentArtworkCount": 0,
        "artworkByMonth": {},
        "artworkBySkill": {},
        "totalCritiques": 0,
        "critiquesBySkill": {},
        "averageCritiquesPerArtwork": 0
    }

@app.get("/api/stats/skill-progress/{skill}")
async def get_skill_progress(skill: str):
    """Get progress for specific skill"""
    sessions = json.loads(PRACTICE_SESSIONS_FILE.read_text())
    skill_sessions = [s for s in sessions if skill in s.get("skills", [])]
    
    # Calculate timeline by month
    timeline = {}
    for s in skill_sessions:
        month = s["date"][:7]  # YYYY-MM
        if month not in timeline:
            timeline[month] = {"practice": 0, "artwork": 0, "critiques": 0}
        timeline[month]["practice"] += 1
    
    return {
        "skill": skill,
        "totalPracticeSessions": len(skill_sessions),
        "totalPracticeMinutes": sum(s.get("duration", 0) for s in skill_sessions),
        "totalArtwork": 0,  # TODO: Implement
        "totalCritiques": 0,  # TODO: Implement
        "timeline": timeline,
        "recentSessions": list(reversed(skill_sessions[-10:])),
        "recentArtwork": []  # TODO: Implement
    }

# ============= METADATA ENDPOINTS =============

@app.get("/api/metadata")
async def get_metadata():
    """Get all metadata"""
    metadata = json.loads(METADATA_FILE.read_text())
    return metadata

@app.post("/api/metadata/image")
async def update_image_metadata(data: ImageMetadata):
    """Update image metadata"""
    metadata = json.loads(METADATA_FILE.read_text())
    
    if "images" not in metadata:
        metadata["images"] = {}
    
    metadata["images"][data.imagePath] = {
        **metadata["images"].get(data.imagePath, {}),
        **data.metadata,
        "updatedAt": datetime.now().isoformat()
    }
    
    METADATA_FILE.write_text(json.dumps(metadata, indent=2))
    return {"success": True}

# ============= VIDEO PROCESSING ENDPOINTS =============

@app.post("/api/video/extract-frames")
async def extract_video_frames():
    """Extract key frames from video - STUB"""
    # TODO: Implement with computer vision
    return {"error": "Not implemented yet", "message": "Video processing will be implemented later"}

@app.get("/api/video/jobs/{job_id}")
async def get_video_job_status(job_id: str):
    """Check video processing job status - STUB"""
    # TODO: Implement job status tracking
    return {"error": "Not implemented yet"}

# ============= AI ENDPOINTS (FUTURE - HuggingFace) =============

@app.post("/api/ai/embed-images")
async def embed_images():
    """Generate embeddings for images - STUB"""
    # TODO: Implement with HuggingFace CLIP or similar
    return {"error": "Not implemented yet", "message": "Image embeddings will use HuggingFace models"}

@app.post("/api/ai/search-similar")
async def search_similar():
    """Find similar images - STUB"""
    # TODO: Implement similarity search with embeddings
    return {"error": "Not implemented yet"}

@app.post("/api/ai/analyze-composition")
async def analyze_composition():
    """Analyze artwork composition - STUB"""
    # TODO: Implement with computer vision model
    return {"error": "Not implemented yet"}

@app.post("/api/ai/critique-generate")
async def generate_critique():
    """Generate AI critique - STUB"""
    # TODO: Implement with HuggingFace LLM
    return {"error": "Not implemented yet"}

# ============= HEALTH CHECK & ROOT =============

@app.get("/")
async def root():
    """Redirect to interactive API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Artist Development Hub Python API is running"}

# ============= GOOGLE PHOTOS INTEGRATION =============

def get_google_photos_credentials():
    """Get authenticated Google Photos credentials"""
    if not GOOGLE_PHOTOS_TOKEN_FILE.exists():
        return None

    creds = Credentials.from_authorized_user_file(str(GOOGLE_PHOTOS_TOKEN_FILE), GOOGLE_PHOTOS_SCOPES)
    return creds

def make_picker_api_request(endpoint, method='GET', params=None, json_data=None):
    """Make a request to Google Photos Picker API"""
    creds = get_google_photos_credentials()
    if not creds:
        return None

    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Content-Type': 'application/json'
    }

    url = f'https://photospicker.googleapis.com/v1/{endpoint}'

    if method == 'GET':
        response = requests.get(url, headers=headers, params=params)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=json_data)
    else:
        raise ValueError(f'Unsupported method: {method}')

    # Log detailed error information if request fails
    if not response.ok:
        logger.error(f"Google Photos Picker API Error - Status: {response.status_code}")
        logger.error(f"Response headers: {dict(response.headers)}")
        logger.error(f"Response body: {response.text}")

    response.raise_for_status()
    return response.json()

@app.get("/api/google-photos/auth-status")
async def get_google_photos_auth_status():
    """Check if Google Photos is authenticated"""
    has_credentials = GOOGLE_PHOTOS_CREDENTIALS_FILE.exists()
    has_token = GOOGLE_PHOTOS_TOKEN_FILE.exists()

    return {
        "configured": has_credentials,
        "authenticated": has_token,
        "message": "Ready to use" if has_token else ("OAuth credentials found, need to authenticate" if has_credentials else "Need to upload OAuth credentials")
    }

@app.post("/api/google-photos/upload-credentials")
async def upload_google_photos_credentials(file: UploadFile = File(...)):
    """Upload OAuth credentials JSON file"""
    try:
        content = await file.read()
        GOOGLE_PHOTOS_CREDENTIALS_FILE.write_bytes(content)
        return {"success": True, "message": "Credentials uploaded successfully"}
    except Exception as e:
        logger.error(f"Error uploading credentials: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/google-photos/auth-url")
async def get_google_photos_auth_url():
    """Get OAuth URL for user to authorize"""
    logger.info(f"Checking for credentials file at: {GOOGLE_PHOTOS_CREDENTIALS_FILE}")
    logger.info(f"File exists: {GOOGLE_PHOTOS_CREDENTIALS_FILE.exists()}")
    if not GOOGLE_PHOTOS_CREDENTIALS_FILE.exists():
        raise HTTPException(status_code=400, detail="OAuth credentials not configured")

    try:
        flow = Flow.from_client_secrets_file(
            str(GOOGLE_PHOTOS_CREDENTIALS_FILE),
            scopes=GOOGLE_PHOTOS_SCOPES,
            redirect_uri="http://localhost:3001/api/google-photos/oauth-callback"
        )

        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Error generating auth URL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/google-photos/oauth-callback")
async def google_photos_oauth_callback(code: str = Query(...), state: str = Query(None)):
    """Handle OAuth callback"""
    try:
        flow = Flow.from_client_secrets_file(
            str(GOOGLE_PHOTOS_CREDENTIALS_FILE),
            scopes=GOOGLE_PHOTOS_SCOPES,
            redirect_uri="http://localhost:3001/api/google-photos/oauth-callback",
            state=state
        )

        flow.fetch_token(code=code)
        creds = flow.credentials

        # Save the credentials
        GOOGLE_PHOTOS_TOKEN_FILE.write_text(creds.to_json())
        logger.info("Google Photos OAuth successful - credentials saved")

        # Redirect to frontend admin page with success parameter
        return RedirectResponse(url="http://localhost:3000/admin?auth=success", status_code=302)
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}", exc_info=True)
        # Redirect to frontend with error
        return RedirectResponse(url=f"http://localhost:3000/admin?auth=error&message={str(e)}", status_code=302)

@app.post("/api/google-photos/download-selected-photos")
async def download_selected_photos(body: dict):
    """Download photos selected from Google Photos"""
    creds = get_google_photos_credentials()
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated with Google")

    try:
        # Expecting media_item_ids from Google Photos Library API
        media_item_ids = body.get("media_item_ids", [])
        if not media_item_ids:
            raise HTTPException(status_code=400, detail="No media item IDs provided")

        downloaded_files = []

        for media_id in media_item_ids:
            try:
                # Get media item from Google Photos Library API
                media_item = make_google_photos_request(f'mediaItems/{media_id}')

                # Get the base URL for downloading
                base_url = media_item.get('baseUrl')
                filename = media_item.get('filename', f'photo_{media_id}.jpg')

                if base_url:
                    # Download with full resolution
                    download_url = f"{base_url}=d"
                    response = requests.get(download_url)

                    if response.status_code == 200:
                        # Save to uploads directory with timestamp
                        timestamped_filename = f"{int(datetime.now().timestamp())}_{filename}"
                        file_path = UPLOADS_DIR / timestamped_filename

                        with open(file_path, 'wb') as f:
                            f.write(response.content)

                        logger.info(f"Downloaded photo: {timestamped_filename}")
                        downloaded_files.append({
                            "id": media_id,
                            "name": filename,
                            "path": f"uploads/{timestamped_filename}",
                            "created": media_item.get('mediaMetadata', {}).get('creationTime')
                        })
                    else:
                        logger.error(f"Failed to download {filename}: HTTP {response.status_code}")

            except Exception as e:
                logger.error(f"Error downloading media item {media_id}: {e}")
                continue

        return {
            "status": "success",
            "downloaded_count": len(downloaded_files),
            "files": downloaded_files,
            "message": f"Successfully downloaded {len(downloaded_files)} photos from Google Photos"
        }

    except Exception as e:
        logger.error(f"Error in download_selected_photos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to download photos: {str(e)}")

@app.post("/api/google-photos/picker/create-session")
async def create_picker_session():
    """Create a Google Photos Picker session"""
    creds = get_google_photos_credentials()
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Create a picker session
        response = make_picker_api_request('sessions', method='POST', json_data={})

        logger.info(f"Picker session created: {response.get('id')}")
        return {
            "session_id": response.get('id'),
            "picker_uri": response.get('pickerUri'),
            "polling_config": response.get('pollingConfig', {})
        }
    except Exception as e:
        logger.error(f"Error creating picker session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create picker session: {str(e)}")

@app.get("/api/google-photos/picker/session/{session_id}")
async def get_picker_session(session_id: str):
    """Poll a picker session to check if user has finished selecting photos"""
    creds = get_google_photos_credentials()
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        response = make_picker_api_request(f'sessions/{session_id}', method='GET')

        return {
            "session_id": response.get('id'),
            "media_items_set": response.get('mediaItemsSet', False),
            "picker_uri": response.get('pickerUri')
        }
    except Exception as e:
        logger.error(f"Error polling picker session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to poll picker session: {str(e)}")

@app.get("/api/google-photos/picker/session/{session_id}/media-items")
async def list_picker_media_items(session_id: str):
    """Get media items selected by the user in a picker session"""
    creds = get_google_photos_credentials()
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        media_items = []
        page_token = None

        while True:
            params = {}
            if page_token:
                params['pageToken'] = page_token

            response = make_picker_api_request(f'sessions/{session_id}/mediaItems', method='GET', params=params)

            media_items.extend(response.get('mediaItems', []))
            page_token = response.get('nextPageToken')

            if not page_token:
                break

        logger.info(f"Retrieved {len(media_items)} media items from picker session {session_id}")
        return {
            "media_items": media_items,
            "count": len(media_items)
        }
    except Exception as e:
        logger.error(f"Error listing picker media items: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list media items: {str(e)}")

@app.get("/api/google-photos/albums/{album_id}/photos")
async def get_album_photos(album_id: str):
    """Get photos from a specific album for preview"""
    service = get_google_photos_service()
    if not service:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        photos = []
        next_page_token = None

        # Fetch first batch of photos for preview (limit to 100)
        while len(photos) < 100:
            body = {
                "albumId": album_id,
                "pageSize": 50
            }
            if next_page_token:
                body["pageToken"] = next_page_token

            results = service.mediaItems().search(body=body).execute()
            media_items = results.get('mediaItems', [])

            if not media_items:
                break

            photos.extend(media_items)
            next_page_token = results.get('nextPageToken')

            if not next_page_token or len(photos) >= 100:
                break

        return {"photos": photos[:100], "count": len(photos)}
    except Exception as e:
        logger.error(f"Error getting album photos: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/google-photos/sync-album")
async def sync_google_photos_album(data: dict):
    """Sync photos from a specific album to local storage"""
    album_id = data.get("album_id")
    album_title = data.get("album_title", "Unknown Album")

    if not album_id:
        raise HTTPException(status_code=400, detail="Album ID required")

    service = get_google_photos_service()
    if not service:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        # Create directory for this album
        album_dir = Path(IMAGE_PATHS["photos"]) / "google_photos" / album_title.replace("/", "_")
        album_dir.mkdir(parents=True, exist_ok=True)

        # Get all photos from the album
        photos_synced = 0
        next_page_token = None

        while True:
            body = {
                "albumId": album_id,
                "pageSize": 100
            }
            if next_page_token:
                body["pageToken"] = next_page_token

            results = service.mediaItems().search(body=body).execute()
            media_items = results.get('mediaItems', [])

            for item in media_items:
                # Download the photo
                base_url = item.get('baseUrl')
                filename = item.get('filename')

                if base_url and filename:
                    # Add download parameters for full quality
                    download_url = f"{base_url}=d"

                    response = requests.get(download_url)
                    if response.status_code == 200:
                        file_path = album_dir / filename
                        file_path.write_bytes(response.content)
                        photos_synced += 1

                        if photos_synced % 10 == 0:
                            logger.info(f"Synced {photos_synced} photos...")

            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break

        # Update synced albums list
        albums_data = json.loads(GOOGLE_ALBUMS_FILE.read_text())
        album_record = {
            "album_id": album_id,
            "title": album_title,
            "photo_count": photos_synced,
            "local_path": str(album_dir),
            "last_synced": datetime.now().isoformat()
        }

        # Remove existing record if present
        albums_data["synced_albums"] = [a for a in albums_data["synced_albums"] if a["album_id"] != album_id]
        albums_data["synced_albums"].append(album_record)
        albums_data["last_sync"] = datetime.now().isoformat()

        GOOGLE_ALBUMS_FILE.write_text(json.dumps(albums_data, indent=2))

        logger.info(f"Synced {photos_synced} photos from album '{album_title}'")

        # Rebuild image index
        build_image_index()

        return {
            "success": True,
            "photos_downloaded": photos_synced,
            "albumPath": str(album_dir)
        }
    except Exception as e:
        logger.error(f"Error syncing album: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/google-photos/synced-albums")
async def get_synced_albums():
    """Get list of synced albums"""
    albums_data = json.loads(GOOGLE_ALBUMS_FILE.read_text())
    return albums_data

@app.get("/admin")
async def redirect_to_admin():
    """Redirect admin requests to frontend"""
    return RedirectResponse(url="http://localhost:3000/admin?reauth=1", status_code=302)

# ============= FRONTEND SERVING (FOR PRODUCTION) =============
# This serves the React app and handles client-side routing
# Make sure to build the frontend first: cd frontend && npm run build

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os.path

# Check if frontend build exists
frontend_build_path = Path(__file__).parent / "frontend" / "build"
if frontend_build_path.exists():
    # Serve static files
    app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")

    # Serve index.html for all non-API routes (client-side routing)
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Don't serve index.html for API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")

        index_file = frontend_build_path / "index.html"
        if index_file.exists():
            return HTMLResponse(content=index_file.read_text(), status_code=200)
        raise HTTPException(status_code=404, detail="Frontend not built")
# ============= PAINT/PIGMENT MANAGEMENT ENDPOINTS =============

def lookup_color_by_name(color_name: str) -> Optional[Dict[str, Any]]:
    """
    Try to find RGB values for a color name using webcolors library.
    Returns dict with rgb values if found, None otherwise.
    """
    try:
        # Try CSS3 colors first
        rgb = webcolors.name_to_rgb(color_name.lower())
        return {"r": rgb.red, "g": rgb.green, "b": rgb.blue}
    except ValueError:
        # Try HTML4 colors
        try:
            rgb = webcolors.name_to_rgb(color_name.lower(), spec='html4')
            return {"r": rgb.red, "g": rgb.green, "b": rgb.blue}
        except ValueError:
            return None

def hex_to_rgb(hex_color: str) -> Optional[Dict[str, Any]]:
    """Convert hex color to RGB dict"""
    try:
        if not hex_color.startswith('#'):
            hex_color = '#' + hex_color
        rgb = webcolors.hex_to_rgb(hex_color)
        return {"r": rgb.red, "g": rgb.green, "b": rgb.blue}
    except ValueError:
        return None

@app.get("/api/paints")
async def get_paints():
    """Get all paints in collection"""
    paints = json.loads(PAINTS_FILE.read_text())
    return {"paints": paints}

@app.post("/api/paints")
async def add_paint(paint: dict):
    """Add a new paint to collection"""
    paints = json.loads(PAINTS_FILE.read_text())

    # Generate unique ID
    paint_id = f"paint_{datetime.now().timestamp()}".replace(".", "_")

    # Try to lookup RGB if not provided
    if not paint.get("rgb"):
        color_name = paint.get("name", "")
        rgb = lookup_color_by_name(color_name)
        if rgb:
            paint["rgb"] = rgb
            paint["rgb_source"] = "webcolors_lookup"

    # Add metadata
    paint["id"] = paint_id
    paint["created_at"] = datetime.now().isoformat()

    paints.append(paint)
    PAINTS_FILE.write_text(json.dumps(paints, indent=2))

    return {"success": True, "paint": paint}

@app.put("/api/paints/{paint_id}")
async def update_paint(paint_id: str, paint: dict):
    """Update an existing paint"""
    paints = json.loads(PAINTS_FILE.read_text())

    for i, p in enumerate(paints):
        if p["id"] == paint_id:
            # Preserve id and created_at
            paint["id"] = paint_id
            paint["created_at"] = p["created_at"]
            paint["updated_at"] = datetime.now().isoformat()

            # Try to lookup RGB if not provided
            if not paint.get("rgb"):
                color_name = paint.get("name", "")
                rgb = lookup_color_by_name(color_name)
                if rgb:
                    paint["rgb"] = rgb
                    paint["rgb_source"] = "webcolors_lookup"

            paints[i] = paint
            PAINTS_FILE.write_text(json.dumps(paints, indent=2))
            return {"success": True, "paint": paint}

    raise HTTPException(status_code=404, detail="Paint not found")

@app.delete("/api/paints/{paint_id}")
async def delete_paint(paint_id: str):
    """Delete a paint from collection"""
    paints = json.loads(PAINTS_FILE.read_text())

    paints = [p for p in paints if p["id"] != paint_id]
    PAINTS_FILE.write_text(json.dumps(paints, indent=2))

    return {"success": True}

@app.post("/api/paints/lookup-color")
async def lookup_color(request: dict):
    """Lookup RGB values for a color name or hex code"""
    color_input = request.get("color", "")

    # Try hex first
    if color_input.startswith('#') or len(color_input) == 6:
        rgb = hex_to_rgb(color_input)
        if rgb:
            return {"success": True, "rgb": rgb, "source": "hex"}

    # Try color name
    rgb = lookup_color_by_name(color_input)
    if rgb:
        return {"success": True, "rgb": rgb, "source": "color_name"}

    return {"success": False, "error": "Color not found"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Artist Development Hub API")
    logger.info(f"Image paths configured:")
    logger.info(f"  Reference: {IMAGE_PATHS['reference']}")
    logger.info(f"  Photos: {IMAGE_PATHS['photos']}")
    logger.info(f"  Artwork: {IMAGE_PATHS['artwork']}")

    if frontend_build_path.exists():
        logger.info(f"Frontend build found, serving React app")
    else:
        logger.info(f"Frontend build not found. Run 'cd frontend && npm run build' to create it.")
        logger.info(f"For development, run React dev server separately with 'cd frontend && npm start'")

    uvicorn.run(app, host="0.0.0.0", port=3001)