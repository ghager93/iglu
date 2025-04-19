import { useState } from 'react'
import './App.css'

const GMT_TIMEZONE = 'UTC'

function App() {
  const [glucoseLevel, setGlucoseLevel] = useState<string>('')
  const [readings, setReadings] = useState<Array<{level: number, timestamp: string}>>([])
  const [remoteReadings, setRemoteReadings] = useState<Array<{value: number, timestamp: number}>>([])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!glucoseLevel) return
    
    // In a real app, we would send this to the backend
    const newReading = {
      level: parseFloat(glucoseLevel),
      timestamp: new Date().toISOString()
    }
    
    setReadings([...readings, newReading])
    setGlucoseLevel('')
  }

  // Fetch remote readings from backend
  const handleFetchRemote = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/glucose-readings/remote')
      if (!res.ok) {
        const errBody = await res.text()
        console.error(`Remote fetch failed with status ${res.status}:`, errBody)
        throw new Error(`Network response was not ok: ${res.status}`)
      }
      const data: Array<{value: number, timestamp: number}> = await res.json()
      // sort readings newest first
      const sorted = data.sort((a, b) => b.timestamp - a.timestamp)
      setRemoteReadings(sorted)
    } catch (err) {
      console.error('Failed to fetch remote readings:', err)
      alert('Error fetching remote readings')
    }
  }

  return (
    <div className="container">
      <header>
        <h1>Diabetes Management App</h1>
        <p>Track and manage your glucose readings</p>
      </header>

      <form onSubmit={handleSubmit} className="glucose-form">
        <h2>Add New Reading</h2>
        <div className="form-group">
          <label htmlFor="glucoseLevel">Glucose Level (mg/dL):</label>
          <input
            type="number"
            id="glucoseLevel"
            value={glucoseLevel}
            onChange={(e) => setGlucoseLevel(e.target.value)}
            step="0.1"
            min="0"
            placeholder="Enter your glucose reading"
            required
          />
        </div>
        <button type="submit">Save Reading</button>
      </form>

      {/* Button to load remote readings */}
      <div style={{ marginBottom: '20px' }}>
        <button onClick={handleFetchRemote}>Load Remote Readings</button>
      </div>

      {/* Table of remote readings */}
      {remoteReadings.length > 0 && (
        <div className="readings-section">
          <h2>Remote Readings</h2>
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Value (mmoL)</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {remoteReadings.map((r, idx) => (
                  <tr key={idx}>
                    <td>{r.value}</td>
                    <td>{new Date(r.timestamp * 1000)
                      .toLocaleString('en-AU', { timeZone: GMT_TIMEZONE })
                    }</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="readings-section">
        <h2>Recent Readings</h2>
        {readings.length === 0 ? (
          <p>No readings recorded yet</p>
        ) : (
          <ul className="readings-list">
            {readings.map((reading, index) => (
              <li key={index}>
                <span className="reading-level">{reading.level} mg/dL</span>
                <span className="reading-time">
                  {new Date(reading.timestamp).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

export default App
