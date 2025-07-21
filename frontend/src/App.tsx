import { useState, useEffect } from 'react'
import './App.css'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const GMT_TIMEZONE = 'UTC'

function App() {
  const [remoteReadings, setRemoteReadings] = useState<Array<{value: number, timestamp: number}>>([])

  const handleFetchRemote = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/glucose-readings/remote')
      if (!res.ok) {
        const errBody = await res.text()
        console.error(`Remote fetch failed with status ${res.status}:`, errBody)
        throw new Error(`Network response was not ok: ${res.status}`)
      }
    } catch (err) {
      console.error('Failed to fetch remote readings:', err)
      alert('Error fetching remote readings')
    }
  }

  // Fetch readings from DB via backend API
  const handleFetchValues = async (from?: number) => {
    try {
      let res
      if (from) {
        res = await fetch(`http://localhost:8000/api/glucose-readings?limit=100&order=desc&granularity=1m&from=${from}`)
      } else {
        res = await fetch('http://localhost:8000/api/glucose-readings?limit=100&order=desc&granularity=1m')
      }
      console.log('Response:', res)
      if (!res.ok) {
        const errBody = await res.text()
        console.error(`Remote fetch failed with status ${res.status}:`, errBody)
        throw new Error(`Network response was not ok: ${res.status}`)
      }
      const dataRaw: Array<{value: number, timestamp: number | string}> = await res.json()
      // Convert ISO timestamp strings to numeric epoch seconds
      const data = dataRaw.map(r => ({
        value: r.value,
        timestamp: typeof r.timestamp === 'string'
          ? Math.floor(new Date(r.timestamp).getTime() / 1000)
          : r.timestamp
      }))
      console.log('Data:', data)
      setRemoteReadings(data)
    } catch (err) {
      console.error('Failed to fetch remote readings:', err)
      alert('Error fetching remote readings')
    }
  }

  // Automatically load readings on component mount
  useEffect(() => {
    handleFetchValues()
  }, [])

  // Real-time stream data
  // const [testData, setTestData] = useState<string[]>([])
  useEffect(() => {
    const eventSource = new EventSource('http://localhost:8000/api/glucose-readings/stream')
    eventSource.onmessage = (event) => {
      console.log('Received SSE:', event.data)
      console.log('length of readings:', remoteReadings.length)
      // const newEntry: string = event.data
      // setTestData(prev => [...prev, newEntry])
      try {
        // Have to parse twice to get the correct format
        const parsed: Array<{value: number, timestamp: number}> = JSON.parse(JSON.parse(event.data))
        const newTimestamp = parsed[0].timestamp
        console.log('Parsed:', parsed)
        if (newTimestamp > remoteReadings[0].timestamp + 30) {
          if (newTimestamp % 60 > 30) {
            parsed[0].timestamp = newTimestamp - (newTimestamp % 60) + 60
          } else {
            parsed[0].timestamp = newTimestamp - (newTimestamp % 60)
          }
          setRemoteReadings(prev => [parsed[0], ...prev])
        }
      } catch (err) {
        console.error('Failed to parse SSE data:', err)
      }
    }
    eventSource.onerror = (err) => {
      console.error('SSE connection error:', err)
      eventSource.close()
    }
    return () => {
      eventSource.close()
    }
  }, [remoteReadings])

  // Call for new readings every minute
  useEffect(() => {
    const interval = setInterval(() => {
      handleFetchValues(from=Date.now()/1000)
    }, 60000)
    return () => clearInterval(interval)
  }, [])

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

          {/* Line chart */}
          <h2>Glucose Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={[...remoteReadings].reverse()}
              margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                type="number"
                domain={["min", "max"]}
                tickFormatter={(ts: number) =>
                  new Date(ts * 1000).toLocaleTimeString('en-AU', { timeZone: GMT_TIMEZONE, hour: '2-digit', minute: '2-digit' })
                }
                interval="preserveStartEnd"
              />
              <YAxis domain={["auto", "auto"]} />
              <Tooltip
                labelFormatter={(ts: number) =>
                  new Date(ts * 1000).toLocaleString('en-AU', { timeZone: GMT_TIMEZONE, hour12: false })
                }
              />
              <Line type="monotone" dataKey="value" stroke="#8884d8" dot={false} />
            </LineChart>
          </ResponsiveContainer>
{/* 
          <h2>Test</h2>
          <ul>
            {testData.map( data => (
              <li key={data}>
                {data}
              </li>
            ))}
          </ul> */}
        </div>
      )}
    </div>
  )
}

export default App
