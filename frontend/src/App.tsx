import { useEffect, useState } from 'react'
import axios from 'axios'
import './App.css'

type WeatherMeasurement = {
  id: number
  station_name: string
  timestamp_utc: string
  temperature_c: number | null
  pressure_hpa: number | null
  wind_speed_ms: number | null
}

const API_URL = 'http://127.0.0.1:8000/api/'

function formatDate(value: string) {
  return new Date(value).toLocaleString('es-ES', {
    timeZone: 'Europe/Madrid',
    hour12: false,
  })
}

function App() {
  const [data, setData] = useState<WeatherMeasurement[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    async function loadWeather() {
      try {
        setIsLoading(true)
        setError(null)

        const startDate = '2026-05-20T00:00:00'
        const endDate = '2026-05-30T00:00:00'
        const stationName = 'Meteo Station Gabriel de Castilla'
        const timeAggregation = 'Hourly'
        
        // Construcción estricta de la URL con Path Parameters
        const url = `${API_URL}antartida/datos/fechaini/${encodeURIComponent(
          startDate,
        )}/fechafin/${encodeURIComponent(endDate)}/estacion/${encodeURIComponent(
          stationName,
        )}?time_aggregation=${encodeURIComponent(timeAggregation)}`

        const response = await axios.get<WeatherMeasurement[]>(url, {
          signal: controller.signal,
        })

        setData(response.data)
      } catch (err) {
        if (axios.isCancel(err)) {
          return
        }
        setError('No se pudo cargar la informacion meteorologica.')
      } finally {
        setIsLoading(false)
      }
    }

    loadWeather()

    return () => controller.abort()
  }, [])

  return (
    <main className="app">
      <header className="app__header">
        <h1>GS Inima Weather</h1>
        <p>Observaciones recientes en la Antartida (CET/CEST).</p>
      </header>

      {isLoading ? (
        <p className="app__status">Loading...</p>
      ) : error ? (
        <p className="app__status app__status--error">{error}</p>
      ) : (
        <section className="app__list">
          {data.map((item) => (
            <article key={`${item.station_name}-${item.id}-${item.timestamp_utc}`} className="app__card">
              <h2>{item.station_name}</h2>
              <p>Fecha: {formatDate(item.timestamp_utc)}</p>
              <dl>
                <div>
                  <dt>Temperatura</dt>
                  <dd>{item.temperature_c !== null ? item.temperature_c.toFixed(1) : 'N/A'} °C</dd>
                </div>
                <div>
                  <dt>Presion</dt>
                  <dd>{item.pressure_hpa !== null ? item.pressure_hpa.toFixed(1) : 'N/A'} hPa</dd>
                </div>
                <div>
                  <dt>Viento</dt>
                  <dd>{item.wind_speed_ms !== null ? item.wind_speed_ms.toFixed(1) : 'N/A'} m/s</dd>
                </div>
              </dl>
            </article>
          ))}
        </section>
      )}
    </main>
  )
}

export default App