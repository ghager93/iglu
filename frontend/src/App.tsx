import { useState } from 'react'
import './App.css'

const GMT_TIMEZONE = 'UTC'

function App() {
  const [remoteReadings, setRemoteReadings] = useState<Array<{value: number, timestamp: number}>>([])

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
    </div>
  )
}

export default App
