from plugins.base_plugin.base_plugin import BasePlugin
from PIL import Image
from io import BytesIO
import requests
import logging

logger = logging.getLogger(__name__)

# Default METAR map URLs - users can override with custom URLs
# Aviation Weather Center METAR map (conus - continental US)
DEFAULT_METAR_MAP_URL = "https://aviationweather.gov/data/obs/metar/map/conus.png"

def grab_image(image_url, dimensions, timeout_ms=40000):
    """Grab an image from a URL and resize it to the specified dimensions."""
    try:
        # Add a User-Agent header to avoid potential blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(image_url, timeout=timeout_ms / 1000, headers=headers)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img = img.resize(dimensions, Image.LANCZOS)
        return img
    except Exception as e:
        logger.error(f"Error grabbing METAR map image from {image_url}: {e}")
        return None

class MetarMap(BasePlugin):
    def generate_image(self, settings, device_config):
        # Use custom URL if provided, otherwise use default
        url = settings.get('url', '').strip()
        if not url:
            url = DEFAULT_METAR_MAP_URL
            logger.info("No URL provided, using default METAR map URL")

        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]

        logger.info(f"Grabbing METAR map image from: {url}")

        image = grab_image(url, dimensions, timeout_ms=40000)

        if not image:
            raise RuntimeError("Failed to load METAR map image, please check logs and verify the URL is accessible.")

        return image

