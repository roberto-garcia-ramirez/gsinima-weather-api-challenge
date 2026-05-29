from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_async_session
from app.repositories.weather import WeatherRepository
from app.schemas.weather import WeatherMeasurementResponse, WeatherQueryRequest
from app.services.weather import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/", response_model=list[WeatherMeasurementResponse])
async def get_weather(
    request: WeatherQueryRequest = Depends(),
    session: AsyncSession = Depends(get_async_session),
    settings: Settings = Depends(get_settings),
) -> list[WeatherMeasurementResponse]:
    repository = WeatherRepository(session)
    service = WeatherService(repository, settings)
    return await service.get_aggregated_weather(request)
