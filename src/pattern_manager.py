"""
Pattern manager for handling file renaming patterns and rules
"""
import re
import os
from time import strftime, strptime, localtime
import exifread
from typing import Optional, Dict, Any, Tuple

from config import (
    IMAGE_PATTERNS,
    VIDEO_PATTERNS,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    TARGET_IMAGE_PATTERN,
    TARGET_VIDEO_PATTERN
)

class PatternManager:
    def __init__(self):
        self.image_patterns = IMAGE_PATTERNS
        self.video_patterns = VIDEO_PATTERNS
        self.image_extensions = IMAGE_EXTENSIONS
        self.video_extensions = VIDEO_EXTENSIONS

    def is_image(self, filename: str) -> bool:
        """Check if file is an image based on extension"""
        return bool(re.match(self.image_extensions, filename, re.I))

    def is_video(self, filename: str) -> bool:
        """Check if file is a video based on extension"""
        return bool(re.match(self.video_extensions, filename, re.I))

    def is_good_image_name(self, filename: str) -> bool:
        """Check if image filename matches the target pattern"""
        return bool(re.match(self.image_patterns['good_pattern'], filename))

    def is_good_video_name(self, filename: str) -> bool:
        """Check if video filename matches the target pattern"""
        return bool(re.match(self.video_patterns['good_pattern'], filename))

    def get_image_pattern_match(self, filename: str) -> Optional[Dict[str, Any]]:
        """Find matching pattern for image filename"""
        for pattern in self.image_patterns['patterns']:
            if re.match(pattern['pattern'], filename, re.I):
                return pattern
        return None

    def get_video_pattern_match(self, filename: str) -> Optional[Dict[str, Any]]:
        """Find matching pattern for video filename"""
        for pattern in self.video_patterns['patterns']:
            if re.match(pattern['pattern'], filename, re.I):
                return pattern
        return None

    def get_file_datetime(self, filepath: str) -> Optional[str]:
        """Get datetime from file's EXIF data"""
        try:
            with open(filepath, 'rb') as f:
                tags = exifread.process_file(f)
                if tags and 'EXIF DateTimeOriginal' in tags:
                    return str(tags['EXIF DateTimeOriginal'])
        except (PermissionError, IOError, KeyError, AttributeError) as e:
            print(f"Error reading EXIF from {filepath}: {str(e)}")
        return None

    def _normalize_extension(self, ext: str) -> str:
        """Normalize file extension"""
        ext = ext.lower()
        if ext == 'jpeg':
            ext = 'jpg'
        return ext

    def _extract_name_and_ext(self, filename: str) -> Tuple[str, str]:
        """Extract name and extension from filename"""
        match = re.match(r'^(?P<name>[\S\s]+)\.(?P<ext>\S+)$', filename)
        if not match:
            raise ValueError(f"Invalid filename format: {filename}")
        name = match.groupdict()['name']
        ext = self._normalize_extension(match.groupdict()['ext'])
        return name, ext

    def generate_new_name(self, original_name: str, pattern_info: Dict[str, str],
                         file_path: str = None) -> Tuple[Optional[str], Optional[str]]:
        """Generate new filename based on pattern type and original name"""
        try:
            file_name, file_ext = self._extract_name_and_ext(original_name)

            if pattern_info['rename_type'] == 'timestamp':
                # Handle timestamp-based filenames
                time_stamp = int(file_name.replace('mmexport', '')
                                       .replace('microMsg.', '')
                                       .replace('Image_', ''))
                time_local = localtime(time_stamp/1000)
                prefix = 'VID_' if self.is_video(original_name) else 'IMG_'
                new_name = f"{prefix}{strftime('%Y%m%d_%H%M%S', time_local)}.{file_ext}"
            
            elif pattern_info['rename_type'] == 'remove_prefix':
                # Remove prefix from the filename
                new_name = original_name.replace('PANO', 'IMG').replace('PXL', 'IMG')

            elif pattern_info['rename_type'] == 'remove_extra':
                # Remove extra text after the standard pattern
                new_name = f"{file_name[:19]}.{file_ext}"

            elif pattern_info['rename_type'] == 'add_underline':
                # Add underline to the filename
                new_name = f"{file_name[:3]}_{file_name[3:11]}_{file_name[11:]}.{file_ext}"

            elif pattern_info['rename_type'] == 'add_prefix':
                # Add IMG_ or VID_ prefix
                prefix = 'VID_' if self.is_video(original_name) else 'IMG_'
                if file_name.startswith(('IMG_', 'VID_')):
                    new_name = original_name
                else:
                    new_name = f"{prefix}{file_name}.{file_ext}"

            elif pattern_info['rename_type'] == 'datetime':
                # Convert datetime format
                dt = strptime(file_name, "%Y-%m-%d %H.%M.%S")
                prefix = 'VID_' if self.is_video(original_name) else 'IMG_'
                new_name = f"{prefix}{strftime('%Y%m%d_%H%M%S', dt)}.{file_ext}"

            elif pattern_info['rename_type'] == 'exif':
                # Try EXIF data first, then fall back to creation time
                if file_path:
                    dt_str = self.get_file_datetime(file_path)
                    if dt_str:
                        dt = strptime(dt_str, "%Y:%m:%d %H:%M:%S")
                        prefix = 'VID_' if self.is_video(original_name) else 'IMG_'
                        new_name = f"{prefix}{strftime('%Y%m%d_%H%M%S', dt)}.{file_ext}"
                    else:
                        # Fall back to creation time
                        try:
                            ctime = os.path.getctime(file_path)
                            time_local = localtime(ctime)
                            prefix = 'VID_' if self.is_video(original_name) else 'IMG_'
                            new_name = f"{prefix}{strftime('%Y%m%d_%H%M%S', time_local)}.{file_ext}"
                        except OSError as e:
                            return None, f"Error getting creation time: {str(e)}"
                else:
                    return None, "No file path provided for EXIF/creation time reading"

            elif pattern_info['rename_type'] == 'creation_time':
                # Use file creation time
                if not file_path:
                    return None, "No file path provided for creation time"
                try:
                    ctime = os.path.getctime(file_path)
                    time_local = localtime(ctime)
                    prefix = 'VID_' if self.is_video(original_name) else 'IMG_'
                    new_name = f"{prefix}{strftime('%Y%m%d_%H%M%S', time_local)}.{file_ext}"
                except OSError as e:
                    return None, f"Error getting creation time: {str(e)}"

            else:
                return None, f"Unknown rename type: {pattern_info['rename_type']}"

            # Check if the generated name matches our target pattern
            if self.is_video(original_name):
                if not re.match(TARGET_VIDEO_PATTERN, new_name.split('.')[0]):
                    return None, f"Generated name {new_name} does not match target pattern"
            else:
                if not re.match(TARGET_IMAGE_PATTERN, new_name.split('.')[0]):
                    return None, f"Generated name {new_name} does not match target pattern"

            print(f" |-+ {new_name}  <-  {original_name}")
            return new_name, None

        except Exception as e:
            return None, f"Error renaming {original_name}: {str(e)}"
