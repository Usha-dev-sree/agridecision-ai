# Farm Service

The Farm Service manages agricultural entities including:
- Farm Plots and Spatial Boundaries (PostGIS)
- Soil Profiles (SoilGrids integrations)
- Crop Seasons and History
- IoT Devices (Moisture Sensors, Weather Stations)

## Technology Stack
- FastAPI
- SQLAlchemy + asyncpg
- GeoAlchemy2 + Shapely (Spatial processing)
- PostgreSQL + PostGIS extension
- Redis
- Kafka

## Environment Variables
See `src/config.py` for required environment variables.
