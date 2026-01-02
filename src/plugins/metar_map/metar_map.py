from plugins.base_plugin.base_plugin import BasePlugin
from PIL import Image
from io import BytesIO
import requests
import logging

logger = logging.getLogger(__name__)

def grab_image(image_url, dimensions, timeout_ms=40000):
    """Grab an image from a URL and resize it to the specified dimensions."""
    try:
        # Add a User-Agent header to avoid potential blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        logger.debug(f"Attempting to fetch image from: {image_url}")
        response = requests.get(image_url, timeout=timeout_ms / 1000, headers=headers)
        response.raise_for_status()
        logger.debug(f"Successfully fetched image, status code: {response.status_code}")
        img = Image.open(BytesIO(response.content))
        logger.debug(f"Opened image, format: {img.format}, size: {img.size}")
        img = img.resize(dimensions, Image.LANCZOS)
        return img
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error grabbing METAR map image from {image_url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error grabbing METAR map image from {image_url}: {type(e).__name__}: {e}")
        return None

class MetarMap(BasePlugin):
    def generate_image(self, settings, device_config):
        # Get URL from settings - required
        url = settings.get('url', '').strip()
        if not url:
            raise RuntimeError("METAR Map URL is required. Please provide a URL to a METAR map image.")

        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]

        logger.info(f"Grabbing METAR map image from: {url}")

        image = grab_image(url, dimensions, timeout_ms=40000)

        if not image:
            error_msg = f"Failed to load METAR map image from: {url}. "
            error_msg += "Please verify the URL is accessible in a web browser. "
            error_msg += "You may need to use a different METAR map URL or check your network connection."
            raise RuntimeError(error_msg)

        return image

