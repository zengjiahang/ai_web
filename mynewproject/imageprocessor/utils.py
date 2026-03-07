"""
Utility functions
"""
import hashlib
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def generate_unique_filename(original_filename):
    """
    Generate unique filename
    
    Args:
        original_filename: Original filename
        
    Returns:
        str: New unique filename
    """
    # Get file extension
    ext = original_filename.split('.')[-1] if '.' in original_filename else ''
    
    # Generate unique identifier
    unique_id = str(uuid.uuid4())
    
    # Create hash value
    hash_object = hashlib.md5(unique_id.encode())
    hash_hex = hash_object.hexdigest()
    
    # Combine new filename
    new_filename = f"{hash_hex[:8]}.{ext}" if ext else hash_hex[:8]
    
    return new_filename


def validate_image_file(file):
    """
    Validate image file
    
    Args:
        file: File object
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check file size (10MB limit)
    if file.size > 10 * 1024 * 1024:
        return False, "Image file size cannot exceed 10MB"
    
    # Check file type
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    ext = file.name.lower().split('.')[-1] if '.' in file.name else ''
    
    if f'.{ext}' not in valid_extensions:
        return False, "Unsupported image format. Please upload JPG, PNG, GIF, BMP, or WebP format images"
    
    return True, None


def format_file_size(size_in_bytes):
    """
    Format file size
    
    Args:
        size_in_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} TB"


def truncate_text(text, max_length=100):
    """
    Truncate text
    
    Args:
        text: Original text
        max_length: Maximum length
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'