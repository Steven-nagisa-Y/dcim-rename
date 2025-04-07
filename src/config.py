"""
Configuration file for file renaming patterns and rules
"""

# File extension patterns
IMAGE_EXTENSIONS = r'.+\.(jpg|jpeg|heic|png|heif)'
VIDEO_EXTENSIONS = r'.+\.(mp4|mov|3gp)'

# Target filename patterns
TARGET_IMAGE_PATTERN = r'IMG_\d{8}_\d{6}'  # IMG_YYYYMMDD_HHMMSS
TARGET_VIDEO_PATTERN = r'VID_\d{8}_\d{6}'  # VID_YYYYMMDD_HHMMSS

# Image filename patterns
IMAGE_PATTERNS = {
    'good_pattern': r'((IMG|Screenshot)_\d{8}_\d{6}(_HDR)?(_\w+\.\w+\..+)?\.(jpg|JPG|jpeg|JPEG|HEIC|heic|HEIF|heif|png|PNG))',
    'patterns': [
        {
            'pattern': r'\d{13}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)',
            'type': 'timestamp',
            'description': 'Unix timestamp pattern',
            'rename_type': 'timestamp'
        },
        {
            'pattern': r'(PANO|PXL)_\d{8}_\d{6}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)',
            'type': 'extra_prefix',
            'description': 'Pattern with extra prefix',
            'rename_type': 'remove_prefix'
        },
        {
            'pattern': r'IMG_\d{8}_\d{6}.+\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)',
            'type': 'extra_text',
            'description': 'Pattern with extra text',
            'rename_type': 'remove_extra'
        },
        {
            'pattern': r'IMG\d{14}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)',
            'type': 'missing_underline',
            'description': 'Pattern missing underline',
            'rename_type': 'add_underline'
        },
        {
            'pattern': r'(mmexport|microMsg\.|Image_|h_)\d{13}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)',
            'type': 'social_media',
            'description': 'Social media saved images',
            'rename_type': 'timestamp'
        },
        {
            'pattern': r'\d{8}_\d{6}(_HDR)?\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)',
            'type': 'missing_prefix',
            'description': 'Pattern missing IMG prefix',
            'rename_type': 'add_prefix'
        },
        {
            'pattern': r'\d{4}-\d{2}-\d{2}\s\d{2}\.\d{2}\.\d{2}\.(jpg|JPG|jpeg|JPEG|HEIC|heic|png|PNG)',
            'type': 'datetime',
            'description': 'Date time format',
            'rename_type': 'datetime'
        }
    ],
    'ext_map': {
        'JPEG': 'jpg',
        'JPG': 'jpg',
        'HEIC': 'heic',
        'HEIF': 'heic',
        'PNG': 'png'
    }
}

# Video filename patterns
VIDEO_PATTERNS = {
    'good_pattern': r'VID_\d{8}_\d{6}\.(mp4|mov|3gp)',
    'patterns': [
        {
            'pattern': r'\d{8}_\d{6}\.(mp4|mov|3gp)',
            'type': 'missing_prefix',
            'description': 'Pattern missing VID prefix',
            'rename_type': 'add_prefix'
        }
    ]
}
