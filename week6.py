import numpy as np, matplotlib.pyplot as plt, pandas as pd
import requests
import os
from urllib.parse import urlparse
from pathlib import Path


def create_directory(directory_name):
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(directory_name, exist_ok=True)
        print(f"Directory '{directory_name}' is ready.")
        return True
    except OSError as e:
        print(f"Error creating directory: {e}")
        return False


def get_valid_filename(url, content_type):
    """Generate a valid filename from URL or content type"""
    # Extract filename from URL path
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    # If no filename in URL or it's invalid, create one
    if not filename or '.' not in filename or len(filename) > 100:
        # Get extension from content type or use generic
        if content_type and '/' in content_type:
            extension = content_type.split('/')[-1]
            # Clean extension (remove parameters)
            extension = extension.split(';')[0].strip()
        else:
            extension = 'bin'

        # Create filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.{extension}"

    # Clean filename (remove any query parameters that might be in the filename)
    filename = filename.split('?')[0]

    # Ensure the filename is safe for filesystem
    import re
    filename = re.sub(r'[^\w\-_.]', '_', filename)

    return filename


def download_image(url, download_dir):
    """Download image from URL and save to specified directory"""
    try:
        print(f"Connecting to: {url}")

        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Send GET request with timeout and headers
        response = requests.get(url, headers=headers, stream=True, timeout=15)
        response.raise_for_status()  # Raise exception for bad status codes

        # Get content type
        content_type = response.headers.get('content-type', '').lower()

        # Check if content is likely an image
        if not content_type.startswith('image/'):
            print(f"Warning: Content-Type is '{content_type}' - may not be an image")
            proceed = input("Do you want to continue downloading? (y/n): ").lower()
            if proceed != 'y':
                print("Download cancelled by user.")
                return None

        # Generate appropriate filename
        filename = get_valid_filename(url, content_type)
        filepath = os.path.join(download_dir, filename)

        # Check if file already exists and handle naming conflict
        counter = 1
        original_filepath = filepath
        while os.path.exists(filepath):
            name, ext = os.path.splitext(original_filepath)
            filepath = f"{name}_{counter}{ext}"
            counter += 1

        # Download and save the image
        print(f"Downloading to: {filepath}")
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='\r')

        print(f"\nDownload completed successfully!")
        print(f"Saved as: {os.path.basename(filepath)}")
        print(f"File size: {os.path.getsize(filepath):,} bytes")

        return filepath

    except requests.exceptions.Timeout:
        print("Error: Connection timed out. The server took too long to respond.")
    except requests.exceptions.ConnectionError:
        print("Error: Connection failed. Check your internet connection or the URL.")
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error occurred - {e}")
    except requests.exceptions.TooManyRedirects:
        print("Error: Too many redirects. The URL might be broken.")
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to download image - {e}")
    except IOError as e:
        print(f"Error: Failed to save file - {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return None


def main():
    """Main function"""
    print("=" * 50)
    print("           IMAGE DOWNLOADER")
    print("=" * 50)
    print("This script downloads images from URLs and saves them to 'Fetched_Images' directory")
    print()

    # Create download directory
    download_dir = "Fetched_Images"
    if not create_directory(download_dir):
        print("Cannot proceed without download directory.")
        return

    # Get URL from user
    while True:
        print("\n" + "-" * 30)
        url = input("Enter the image URL (or 'quit' to exit): ").strip()

        if url.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if not url:
            print("Please enter a valid URL.")
            continue

        # Download the image
        downloaded_file = download_image(url, download_dir)

        if downloaded_file:
            print("✓ Download successful!")
        else:
            print("✗ Download failed.")

        # Ask if user wants to continue
        continue_download = input("\nDownload another image? (y/n): ").lower()
        if continue_download != 'y':
            print("Goodbye!")
            break


if __name__ == "__main__":
    # Check if requests library is installed
    try:
        import requests

        main()
    except ImportError:
        print("Error: The 'requests' library is required.")
        print("Please install it using: pip install requests")