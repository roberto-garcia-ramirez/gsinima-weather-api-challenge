from fastapi.testclient import TestClient
from app.main import app

# Initialize the FastAPI test client
client = TestClient(app)

# Constant test parameters
START_DATE = "2026-05-20T00:00:00"
END_DATE = "2026-05-30T00:00:00"
VALID_STATION = "Meteo Station Gabriel de Castilla"
INVALID_STATION = "Base Secreta Inventada"

def test_get_weather_success():
    """Verify the endpoint responds correctly to a valid request."""
    url = f"/api/antartida/datos/fechaini/{START_DATE}/fechafin/{END_DATE}/estacion/{VALID_STATION}"
    response = client.get(url, params={"time_aggregation": "Hourly"})
    
    assert response.status_code == 200, f"Unexpected error: {response.text}"
    assert isinstance(response.json(), list), "The response must be a list of measurements"

def test_get_weather_data_structure():
    """Verify returned data contains the exact fields the frontend needs."""
    url = f"/api/antartida/datos/fechaini/{START_DATE}/fechafin/{END_DATE}/estacion/{VALID_STATION}"
    response = client.get(url, params={"time_aggregation": "Hourly"})
    data = response.json()
    
    if len(data) > 0:
        first_record = data[0]
        expected_keys = {
            "id", "station_name", "timestamp_utc", 
            "temperature_c", "pressure_hpa", "wind_speed_ms"
        }
        assert expected_keys.issubset(first_record.keys()), "Required JSON fields are missing"
        assert first_record["station_name"] == VALID_STATION

def test_get_weather_invalid_station():
    """Verify FastAPI correctly rejects station names not present in the Enum."""
    url = f"/api/antartida/datos/fechaini/{START_DATE}/fechafin/{END_DATE}/estacion/{INVALID_STATION}"
    response = client.get(url, params={"time_aggregation": "Hourly"})
    
    # Should return 422 Unprocessable Entity due to Pydantic/Enum validation failure
    assert response.status_code == 422