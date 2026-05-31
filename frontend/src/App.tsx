import React, { useEffect, useState } from 'react'
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
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Interactive form state
  const [startDate, setStartDate] = useState('2026-05-20T00:00')
  const [endDate, setEndDate] = useState('2026-05-30T00:00')
  const [stationName, setStationName] = useState('Meteo Station Gabriel de Castilla')
  const [timeAggregation, setTimeAggregation] = useState('Hourly')

  // Function executed on form submit
  async function fetchWeather(e?: React.FormEvent<HTMLFormElement>) {
    if (e) e.preventDefault() // Prevents full page reload

    try {
      setIsLoading(true)
      setError(null)

      // Ensure ISO format by appending seconds if the HTML input omits them
      const startIso = startDate.length === 16 ? `${startDate}:00` : startDate
      const endIso = endDate.length === 16 ? `${endDate}:00` : endDate
      
      const url = `${API_URL}antartida/datos/fechaini/${encodeURIComponent(
        startIso
      )}/fechafin/${encodeURIComponent(endIso)}/estacion/${encodeURIComponent(
        stationName
      )}?time_aggregation=${encodeURIComponent(timeAggregation)}`

      const response = await axios.get<WeatherMeasurement[]>(url)
      setData(response.data)

    } catch (err) {
      setError('No se pudo cargar la información meteorológica. Verifica la conexión o los parámetros.')
    } finally {
      setIsLoading(false)
    }
  }

  // Initial auto-load on page mount
  useEffect(() => {
    fetchWeather()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <main className="app">
      <header className="app__header">
        <h1>GS Inima Weather</h1>
        <p>Panel Interactivo de Observaciones en la Antártida (CET/CEST)</p>
      </header>

      {/* INTERACTIVE CONTROL PANEL */}
      <section className="app__controls">
        <form onSubmit={fetchWeather} className="controls-form">
          <div className="control-group">
            <label htmlFor="startDate">Fecha Inicio:</label>
            <input 
              type="datetime-local" 
              id="startDate" 
              value={startDate} 
              onChange={(e) => setStartDate(e.target.value)} 
              required
            />
          </div>

          <div className="control-group">
            <label htmlFor="endDate">Fecha Fin:</label>
            <input 
              type="datetime-local" 
              id="endDate" 
              value={endDate} 
              onChange={(e) => setEndDate(e.target.value)} 
              required
            />
          </div>

          <div className="control-group">
            <label htmlFor="station">Estación:</label>
            <select 
              id="station" 
              value={stationName} 
              onChange={(e) => setStationName(e.target.value)}
            >
              <option value="Meteo Station Gabriel de Castilla">Gabriel de Castilla</option>
              {/* You can add more stations here if your backend Enum supports them */}
            </select>
          </div>

          <div className="control-group">
            <label htmlFor="aggregation">Agregación:</label>
            <select 
              id="aggregation" 
              value={timeAggregation} 
              onChange={(e) => setTimeAggregation(e.target.value)}
            >
              <option value="Hourly">Por Hora (Hourly)</option>
              <option value="Daily">Diaria (Daily)</option>
              <option value="Monthly">Mensual (Monthly)</option>
            </select>
          </div>

          <button type="submit" disabled={isLoading} className="search-button">
            {isLoading ? 'Cargando...' : 'Buscar Datos'}
          </button>
        </form>
      </section>

      {/* RESULTS RENDERING */}
      {error && <p className="app__status app__status--error">{error}</p>}
      
      {!isLoading && !error && data.length === 0 && (
        <p className="app__status">No hay datos para esta selección.</p>
      )}

      {isLoading ? (
        <p className="app__status">Consultando a la base de datos...</p>
      ) : (
        <section className="app__list">
          {data.map((item) => (
            <article key={`${item.station_name}-${item.id}-${item.timestamp_utc}`} className="app__card">
              <h2>{item.station_name}</h2>
              <p className="date-text">📅 {formatDate(item.timestamp_utc)}</p>
              <dl>
                <div>
                  <dt>Temperatura</dt>
                  <dd>{item.temperature_c !== null ? item.temperature_c.toFixed(1) : 'N/A'} °C</dd>
                </div>
                <div>
                  <dt>Presión</dt>
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