from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

import httpx
import pandas as pd

from app.core.config import Settings
from app.repositories.weather import WeatherRepository
from app.schemas.weather import (
    StationName,
    TimeAggregation,
    WeatherMeasurementCreate,
    WeatherMeasurementResponse,
    WeatherQueryRequest,
)

AEMET_BASE_URL = "https://opendata.aemet.es/opendata/api"
STATION_CODE_MAP: dict[StationName, str] = {
    StationName.GABRIEL_DE_CASTILLA: "89070",
    StationName.JUAN_CARLOS_I: "89064",
}


class WeatherService:
    def __init__(self, repository: WeatherRepository, settings: Settings) -> None:
        self.repository = repository
        self.settings = settings

    async def get_aggregated_weather(
        self,
        request: WeatherQueryRequest,
    ) -> list[WeatherMeasurementResponse]:
        start_utc = self._ensure_utc(request.start_date)
        end_utc = self._ensure_utc(request.end_date)

        measurements = await self.repository.get_measurements(
            request.station.value,
            start_utc,
            end_utc,
        )

        if self._is_cache_miss(measurements, start_utc, end_utc):
            fetched = await self._fetch_from_aemet(
                start_utc,
                end_utc,
                request.station,
            )
            await self.repository.bulk_upsert_measurements(fetched)
            measurements = await self.repository.get_measurements(
                request.station.value,
                start_utc,
                end_utc,
            )

        if not measurements:
            return []

        data = [
            {
                "id": item.id,
                "station_name": item.station_name,
                "timestamp_utc": item.timestamp_utc,
                "temperature_c": item.temperature_c,
                "pressure_hpa": item.pressure_hpa,
                "wind_speed_ms": item.wind_speed_ms,
            }
            for item in measurements
        ]
        frame = pd.DataFrame(data)
        frame["timestamp_utc"] = pd.to_datetime(frame["timestamp_utc"], utc=True)
        frame = frame.set_index("timestamp_utc").sort_index()
        frame = frame.tz_convert("Europe/Madrid")

        if request.time_aggregation:
            frame = frame.drop(columns=["id"], errors="ignore")
            resample_rule = self._get_resample_rule(request.time_aggregation)
            frame = frame.resample(resample_rule).mean(numeric_only=True)
            frame = frame.dropna(how="all")
            frame["station_name"] = request.station.value

        if request.data_types:
            keep = {"id", "station_name", "timestamp_utc", *request.data_types}
            frame = frame[[col for col in frame.columns if col in keep]]

        frame = frame.reset_index()
        responses = []
        for _, row in frame.iterrows():
            row_id = row.get("id")
            response_id = int(row_id) if row_id is not None and pd.notna(row_id) else 0
            responses.append(
                WeatherMeasurementResponse(
                    id=response_id,
                    station_name=row.get("station_name", request.station.value),
                    timestamp_utc=row["timestamp_utc"].to_pydatetime(),
                    temperature_c=row.get("temperature_c"),
                    pressure_hpa=row.get("pressure_hpa"),
                    wind_speed_ms=row.get("wind_speed_ms"),
                )
            )
        return responses

    async def _fetch_from_aemet(
        self,
        start_date: datetime,
        end_date: datetime,
        station: StationName,
    ) -> list[WeatherMeasurementCreate]:
        station_code = STATION_CODE_MAP.get(station)
        if not station_code:
            return []

        start_text = start_date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_text = end_date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        endpoint = (
            f"{AEMET_BASE_URL}/antartida/datos/fechaini/{start_text}/"
            f"fechafin/{end_text}/estacion/{station_code}"
        )

        headers = {"api_key": self.settings.AEMET_API_KEY}
        async with httpx.AsyncClient(timeout=30.0) as client:
            meta_response = await client.get(endpoint, headers=headers)
            meta_response.raise_for_status()
            meta_payload = meta_response.json()
            data_url = meta_payload.get("datos")
            if not data_url:
                return []
            data_response = await client.get(data_url)
            data_response.raise_for_status()
            payload = data_response.json()

        return self._parse_aemet_payload(payload, station.value)

    @staticmethod
    def _parse_aemet_payload(
        payload: Iterable[dict[str, object]],
        station_name: str,
    ) -> list[WeatherMeasurementCreate]:
        measurements: list[WeatherMeasurementCreate] = []
        for item in payload:
            timestamp = WeatherService._parse_aemet_datetime(item.get("fhora"))
            if not timestamp:
                continue
            measurements.append(
                WeatherMeasurementCreate(
                    station_name=station_name,
                    timestamp_utc=timestamp,
                    temperature_c=WeatherService._to_float(item.get("temp")),
                    pressure_hpa=WeatherService._to_float(item.get("pres")),
                    wind_speed_ms=WeatherService._to_float(item.get("vel")),
                )
            )
        return measurements

    @staticmethod
    def _parse_aemet_datetime(value: object) -> datetime | None:
        if not value or not isinstance(value, str):
            return None
        text = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def _to_float(value: object) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _ensure_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _get_resample_rule(time_aggregation: TimeAggregation) -> str:
        if time_aggregation == TimeAggregation.HOURLY:
            return "H"
        if time_aggregation == TimeAggregation.DAILY:
            return "D"
        return "MS"

    @staticmethod
    def _is_cache_miss(
        measurements: list,
        start_date: datetime,
        end_date: datetime,
    ) -> bool:
        if not measurements:
            return True
        first = measurements[0].timestamp_utc
        last = measurements[-1].timestamp_utc
        return first > start_date or last < end_date
