from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, field_serializer

MADRID_TZ = ZoneInfo("Europe/Madrid")


class StationName(str, Enum):
    GABRIEL_DE_CASTILLA = "Meteo Station Gabriel de Castilla"
    JUAN_CARLOS_I = "Meteo Station Juan Carlos I"


class TimeAggregation(str, Enum):
    HOURLY = "Hourly"
    DAILY = "Daily"
    MONTHLY = "Monthly"


class WeatherMeasurementBase(BaseModel):
    station_name: str
    timestamp_utc: datetime
    temperature_c: float | None = None
    pressure_hpa: float | None = None
    wind_speed_ms: float | None = None


class WeatherMeasurementCreate(WeatherMeasurementBase):
    pass


class WeatherMeasurementResponse(WeatherMeasurementBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("timestamp_utc")
    def serialize_timestamp_utc(self, value: datetime) -> str:
        return value.astimezone(MADRID_TZ).isoformat()


class WeatherQueryRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    station: StationName
    time_aggregation: Optional[TimeAggregation] = None
    data_types: Optional[list[str]] = None
    model_config = ConfigDict(from_attributes=True)
