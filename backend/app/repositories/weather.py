from __future__ import annotations

from datetime import datetime
from typing import Iterable, Mapping

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.weather import WeatherMeasurement


class WeatherRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_measurements(
        self,
        station_name: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[WeatherMeasurement]:
        query = (
            select(WeatherMeasurement)
            .where(
                WeatherMeasurement.station_name == station_name,
                WeatherMeasurement.timestamp_utc.between(start_date, end_date),
            )
            .order_by(WeatherMeasurement.timestamp_utc.asc())
        )
        result = await self.session.scalars(query)
        return result.all()

    async def bulk_upsert_measurements(
        self,
        measurements: Iterable[WeatherMeasurement | Mapping[str, object]],
    ) -> None:
        values = [self._normalize_measurement(measurement) for measurement in measurements]
        if not values:
            return
        statement = insert(WeatherMeasurement).values(values).on_conflict_do_nothing()
        await self.session.execute(statement)
        await self.session.commit()

    @staticmethod
    def _normalize_measurement(
        measurement: WeatherMeasurement | Mapping[str, object],
    ) -> dict[str, object]:
        if isinstance(measurement, WeatherMeasurement):
            return {
                "station_name": measurement.station_name,
                "timestamp_utc": measurement.timestamp_utc,
                "temperature_c": measurement.temperature_c,
                "pressure_hpa": measurement.pressure_hpa,
                "wind_speed_ms": measurement.wind_speed_ms,
            }
        return dict(measurement)
