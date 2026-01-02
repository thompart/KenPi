from plugins.base_plugin.base_plugin import BasePlugin
from PIL import Image
import requests
import logging
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

# Default airports around KEDC (Austin Executive Airport)
DEFAULT_AIRPORTS = ['KEDC', 'KAUS', 'KT74', 'KGTU', 'KRYW', 'KHYI', 'KBMQ']

# NOAA Aviation Weather API endpoint
METAR_API_URL = "https://aviationweather.gov/api/data/metar"

class MetarMap(BasePlugin):
    def generate_settings_template(self):
        template_params = super().generate_settings_template()
        template_params['style_settings'] = True
        return template_params

    def fetch_metars(self, icao_codes):
        """Fetch METAR data from NOAA Aviation Weather API."""
        params = {
            'ids': ','.join(icao_codes),
            'format': 'json',
            'hours': 1,  # Last hour's reports
            'taf': 'false'
        }
        
        try:
            logger.info(f"Fetching METAR data for airports: {','.join(icao_codes)}")
            response = requests.get(METAR_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not isinstance(data, list):
                logger.warning(f"Unexpected API response format: {type(data)}")
                return []
            
            logger.info(f"Successfully fetched {len(data)} METAR reports")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch METAR data: {e}")
            raise RuntimeError(f"Failed to fetch METAR data from NOAA API: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing METAR data: {e}")
            raise RuntimeError(f"Error processing METAR data: {str(e)}")

    def parse_metar(self, metar_data):
        """Parse METAR data into a readable format."""
        station_id = metar_data.get('icaoId', metar_data.get('stationId', ''))
        raw_text = metar_data.get('rawOb', metar_data.get('rawText', ''))
        
        # Extract key information (handle different API response formats)
        temp = metar_data.get('temp', None)
        dewp = metar_data.get('dewp', None)
        wind_dir = metar_data.get('wdir', None)
        wind_speed = metar_data.get('wspd', None)
        visibility = metar_data.get('visib', None)
        altim = metar_data.get('altim', None)
        clouds = metar_data.get('skyc', [])
        flight_cat = metar_data.get('fltlvl', metar_data.get('flightCategory', ''))
        
        # Format temperature
        temp_str = "N/A"
        if temp is not None:
            try:
                temp_str = f"{int(temp)}°C"
            except (ValueError, TypeError):
                temp_str = "N/A"
        
        # Format wind
        wind_str = "N/A"
        if wind_dir is not None and wind_speed is not None:
            try:
                wind_str = f"{int(wind_dir):03d}@{int(wind_speed)}kt"
            except (ValueError, TypeError):
                wind_str = "N/A"
        
        # Format visibility
        vis_str = "N/A"
        if visibility is not None:
            try:
                vis_str = f"{float(visibility):.1f}SM" if float(visibility) < 10 else f"{int(visibility)}SM"
            except (ValueError, TypeError):
                vis_str = "N/A"
        
        # Format altimeter
        alt_str = "N/A"
        if altim is not None:
            try:
                alt_str = f"{float(altim):.2f}"
            except (ValueError, TypeError):
                alt_str = "N/A"
        
        # Format clouds
        cloud_str = ', '.join(clouds) if clouds and isinstance(clouds, list) else "CLR"
        
        # Format the data
        parsed = {
            'station': station_id,
            'raw': raw_text,
            'temp': temp_str,
            'wind': wind_str,
            'visibility': vis_str,
            'altimeter': alt_str,
            'clouds': cloud_str,
            'flight_cat': flight_cat if flight_cat else "N/A"
        }
        
        return parsed

    def generate_image(self, settings, device_config):
        # Get airport ICAO codes from settings, or use defaults
        airports_str = settings.get('airports', '').strip()
        if airports_str:
            # Parse comma-separated list
            icao_codes = [code.strip().upper() for code in airports_str.split(',') if code.strip()]
        else:
            # Use default airports around KEDC
            icao_codes = DEFAULT_AIRPORTS.copy()
        
        if not icao_codes:
            raise RuntimeError("No airports specified. Please provide ICAO codes (e.g., KEDC,KAUS).")
        
        # Fetch METAR data
        metar_data_list = self.fetch_metars(icao_codes)
        
        if not metar_data_list:
            raise RuntimeError("No METAR data received. The airports may not have current reports.")
        
        # Parse METAR data
        parsed_metars = []
        for metar_data in metar_data_list:
            try:
                parsed = self.parse_metar(metar_data)
                parsed_metars.append(parsed)
            except Exception as e:
                logger.warning(f"Error parsing METAR for {metar_data.get('icaoId', 'unknown')}: {e}")
        
        if not parsed_metars:
            raise RuntimeError("Failed to parse METAR data.")
        
        # Get display settings
        dimensions = device_config.get_resolution()
        if device_config.get_config("orientation") == "vertical":
            dimensions = dimensions[::-1]
        
        timezone = device_config.get_config("timezone", default="America/Chicago")
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        # Prepare template parameters
        template_params = {
            "title": settings.get('title', 'METAR Reports'),
            "metars": parsed_metars,
            "last_update": current_time.strftime("%H:%M"),
            "airport_count": len(parsed_metars),
            "plugin_settings": settings
        }
        
        # Render the image using HTML/CSS
        image = self.render_image(dimensions, "metar_map.html", "metar_map.css", template_params)
        
        if not image:
            raise RuntimeError("Failed to generate METAR display image.")
        
        return image

