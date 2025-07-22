import { useState, useEffect } from 'react'
import './App.css'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const GMT_TIMEZONE = 'UTC'

const API_URL = 'http://localhost:8000/api'
const READING_LIMIT = 100


function App() {
  const [readings, setReadings] = useState<Array<{value: number, timestamp: number}>>([])
  const [from, setFrom] = useState<number>(Math.floor(Date.now()/1000-86400))
  const [to, setTo] = useState<number>(Math.floor(Date.now()/1000))
  const [granularity, setGranularity] = useState<string>('1m')
  const [isLive, setIsLive] = useState<boolean>(true)
  const [currTime, setCurrTime] = useState<number>(Date.now()/1000)

  const handleFetchReadings = async () => {
    try {
      console.log('Fetching readings')
      let res
      if (isLive) {
        res = await fetch(`${API_URL}/glucose-readings?order=desc&granularity=${granularity}&from=${from}`)
      } else {
        res = await fetch(`${API_URL}/glucose-readings?order=desc&granularity=${granularity}&from=${from}&to=${to}`)
      }
      if (!res.ok) {
        const errBody = await res.text()
        console.error(`Remote fetch failed with status ${res.status}:`, errBody)
        throw new Error(`Network response was not ok: ${res.status}`)
      }
      const dataRaw: Array<{value: number, timestamp: number | string}> = await res.json()
      const data = dataRaw.map(r => ({
        value: r.value,
        timestamp: typeof r.timestamp === 'string'
          ? Math.floor(new Date(r.timestamp).getTime() / 1000)
          : r.timestamp
      }))
      setReadings(data)
    } catch (err) {
      console.error('Failed to fetch readings:', err)
      alert('Error fetching readings')
    }
  }

  // Automatically load readings on component mount
  useEffect(() => {
    handleFetchReadings()
  }, [])

  // Real-time stream data
  // const [testData, setTestData] = useState<string[]>([])
  useEffect(() => {
    const eventSource = new EventSource('http://localhost:8000/api/glucose-readings/stream')
    eventSource.onmessage = (event) => {
      console.log('Received SSE:', event.data)
      // console.log('length of readings:', remoteReadings.length)
      // const newEntry: string = event.data
      // setTestData(prev => [...prev, newEntry])
      try {
        // Have to parse twice to get the correct format
        const parsed: Array<{value: number, timestamp: number}> = JSON.parse(JSON.parse(event.data))
        const newTimestamp = parsed[0].timestamp
        console.log('Parsed:', parsed)
        // if (newTimestamp > readings[0].timestamp + 30) {
        //   if (newTimestamp % 60 > 30) {
        //     parsed[0].timestamp = newTimestamp - (newTimestamp % 60) + 60
        //   } else {
        //     parsed[0].timestamp = newTimestamp - (newTimestamp % 60)
        //   }
        //   setReadings(prev => [parsed[0], ...prev])
        // }
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
  }, [])

  // Call for new readings every minute
  useEffect(() => {
    const interval = setInterval(async () => {
        try {
          console.log('Fetching new readings')
          const lastReadingTime = readings[0].timestamp
          const res = await fetch(`${API_URL}/glucose-readings?order=desc&granularity=1m&from=${lastReadingTime}`)
          if (!res.ok) {
            const errBody = await res.text()
            console.error(`Remote fetch failed with status ${res.status}:`, errBody)
            throw new Error(`Network response was not ok: ${res.status}`)
          }
          const dataRaw: Array<{value: number, timestamp: number | string}> = await res.json()
          const data = dataRaw.map(r => ({
            value: r.value,
            timestamp: typeof r.timestamp === 'string'
              ? Math.floor(new Date(r.timestamp).getTime() / 1000)
              : r.timestamp
          }))
          const dataNew = data.filter(r => r.timestamp > lastReadingTime)
          setReadings(prev => [...dataNew, ...prev])
        } catch (err) {
          console.error('Failed to fetch new readings:', err)
          alert('Error fetching new readings')
        }
    }, 60000)
    return () => clearInterval(interval)
  }, [readings])

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrTime(Math.floor(Date.now()/1000))
    }, 1000)
    return () => clearInterval(interval)
  }, [])


  return (
    <div className="container">
      <header>
        <h1>Diabetes Management App</h1>
        <p>Track and manage your glucose readings</p>
      </header>

      {/* Table of remote readings */}
      {readings.length > 0 && (
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
                {readings.map((r, idx) => (
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

          {/* Most recent reading */}
          <h2>Most Recent Reading</h2>
          <p>{readings[0].value} mmoL</p>
          <p>{new Date(readings[0].timestamp * 1000)
            .toLocaleString('en-AU', { timeZone: GMT_TIMEZONE })
          }</p>

          {/* Time since last reading */}
          <h2>Time Since Last Reading</h2>
          <p>{currTime - readings[0].timestamp + 600 * 60} seconds</p>
          <p>{currTime} {readings[0].timestamp - 600 * 60}</p>

          {/* Line chart */}
          <h2>Glucose Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={[...readings].reverse()}
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
