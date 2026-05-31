from __future__ import annotations

import logging
import traceback

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_async_session
from app.repositories.weather import WeatherRepository
from app.schemas.weather import (
    StationName,
    TimeAggregation,
    WeatherMeasurementResponse,
    WeatherQueryRequest,
)
from app.services.weather import WeatherService

router = APIRouter(tags=["weather"])
logger = logging.getLogger(__name__)


@router.get(
    "/antartida/datos/fechaini/{start_date}/fechafin/{end_date}/estacion/{station}",
    response_model=list[WeatherMeasurementResponse],
)
async def get_weather(
    start_date: datetime,
    end_date: datetime,
    station: StationName,
    time_aggregation: TimeAggregation | None = None,
    session: AsyncSession = Depends(get_async_session),
    settings: Settings = Depends(get_settings),
) -> list[WeatherMeasurementResponse]:
    try:
        print("\n>>> [DIAGNÓSTICO] Iniciando procesamiento de la petición")
        request = WeatherQueryRequest(
            start_date=start_date,
            end_date=end_date,
            station=station,
            time_aggregation=time_aggregation,
        )
        print(">>> [DIAGNÓSTICO] Instancia WeatherQueryRequest creada")
        
        repository = WeatherRepository(session)
        service = WeatherService(repository, settings)
        
        print(">>> [DIAGNÓSTICO] Invocando WeatherService.get_aggregated_weather()")
        result = await service.get_aggregated_weather(request)
        print(">>> [DIAGNÓSTICO] Ejecución del servicio completada")
        
        return result
    except Exception as e:
        print(f"\n>>> [ERROR CRÍTICO DETECTADO]: {str(e)}")
        traceback.print_exc()
        raise