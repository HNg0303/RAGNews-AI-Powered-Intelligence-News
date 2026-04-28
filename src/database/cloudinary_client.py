import cloudinary
import cloudinary.uploader

# Initialize Cloudinary - Save Images Data on here
def get_client(cloudinary_cloud_name: str, cloudinary_api_key: str, cloudinary_api_secret: str):
    cloudinary.config(
        cloud_name = cloudinary_cloud_name,
        api_key = cloudinary_api_key,
        api_secret = cloudinary_api_secret,
        secure = True
    )
    return cloudinary

def upload_to_cloudinary(cloudinary: cloudinary.Config, file_path, article_id):
    """Uploads a local image and returns its public URL."""
    try:
        response = cloudinary.uploader.upload(
            file_path,
            # Organizes images in a folder named after your project
            folder = f"RAGNews/{article_id}",
            use_filename = True,
            unique_filename = True
        )
        return response.get("secure_url") # Use secure_url for HTTPS
    except Exception as e:
        print(f"Cloudinary Upload Failed: {e}")
        return None
    
