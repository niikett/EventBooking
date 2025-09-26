import cloudinary.uploader
from fastapi import UploadFile

def upload(file: UploadFile) -> str:
    try:
        result = cloudinary.uploader.upload(file.file, folder="event_banners")
        return result.get("secure_url")
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed: {e}")
