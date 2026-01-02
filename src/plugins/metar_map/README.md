# METAR Reports Plugin

This plugin displays METAR (Meteorological Aerodrome Report) data from airports on your e-ink display.

## Features

- Fetches real-time METAR data from the NOAA Aviation Weather API (free, no API key required)
- Displays weather information for multiple airports
- Automatically updates based on your playlist refresh interval
- Default airports around KEDC (Austin Executive Airport): KEDC, KAUS, KT74, KGTU, KRYW, KHYI, KBMQ

## Configuration

- **Title**: Optional title displayed at the top (default: "METAR Reports")
- **Airport ICAO Codes**: Comma-separated list of airport ICAO codes to display (e.g., `KEDC,KAUS,KT74`)
  - If left empty, defaults to airports around KEDC
  - Each airport must have a valid ICAO code (4 characters)

## Data Source

The plugin uses the NOAA Aviation Weather API:
- **Endpoint**: https://aviationweather.gov/api/data/metar
- **Format**: JSON
- **No API key required**
- **Rate limits**: 100 requests per minute (more than enough for typical refresh intervals)

## Display Information

For each airport, the plugin displays:
- Station ID (ICAO code)
- Temperature
- Wind direction and speed
- Visibility
- Altimeter setting
- Cloud conditions
- Raw METAR text

## Icon

The plugin currently uses a placeholder icon. You can replace `icon.png` with a custom icon that matches the style of other plugin icons (typically 64x64 or 128x128 pixels).

