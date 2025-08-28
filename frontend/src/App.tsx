import { EventSource } from 'eventsource'
import { useState, useEffect } from 'react'
import './App.css'
import { GlucoseChart } from './components/GlucoseChart'

const GMT_TIMEZONE = 'UTC'

const API_URL = 'http://localhost:8000/api'
const READING_LIMIT = 100

const API_KEY = import.meta.env.VITE_API_KEY

// Separate component for timer display to prevent chart re-renders
const TimeDisplay = ({ lastReading }: { lastReading: {value: number, timestamp: number} }) => {
  const [currTime, setCurrTime] = useState<number>(Math.floor(Date.now()/1000))

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrTime(Math.floor(Date.now()/1000))
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  if (!lastReading) return null

  return (
    <>
      {/* Time since last reading */}
      <h2>Time Since Last Reading</h2>
      <p>{currTime - lastReading.timestamp + 600 * 60} seconds</p>
    </>
  )
}

const ReadingDisplay = ({ reading }: { reading: {value: number, timestamp: number} }) => {
  const [currTime, setCurrTime] = useState<number>(Math.floor(Date.now()/1000))

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrTime(Math.floor(Date.now()/1000))
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  if (!reading) return null

  const timeSinceReading = currTime - reading.timestamp + 600 * 60
  let timeSinceReadingStr = "Now"
  if (timeSinceReading < 10) {
    timeSinceReadingStr = "Just now"
  } else if (timeSinceReading < 60) {
    timeSinceReadingStr = `< 1 minute ago`
  } else if (timeSinceReading < 120) {
    timeSinceReadingStr = `1 minute ago`
  } else if (timeSinceReading < 3600) {
    timeSinceReadingStr = `${Math.floor(timeSinceReading / 60)} minutes ago`
  } else if (timeSinceReading < 1800) {
    timeSinceReadingStr = `1 hour ago`
  } else if (timeSinceReading < 86400) {
    timeSinceReadingStr = `${Math.floor(timeSinceReading / 3600)} hours ago`
  } else if (timeSinceReading < 172800) {
    timeSinceReadingStr = `1 day ago`
  } else {
    timeSinceReadingStr = `${Math.floor(timeSinceReading / 86400)} days ago`
  }

  return (
    <>
      <p>{reading.value} mmoL</p>
      <p>{new Date(reading.timestamp * 1000)
        .toLocaleString('en-AU', { timeZone: GMT_TIMEZONE })
      }</p>
      <p>{timeSinceReadingStr}</p>
    </>
  )
}

function App() {
  const [readings, setReadings] = useState<Array<{value: number, timestamp: number}>>([])
  const [from, setFrom] = useState<number>(Math.floor(Date.now()/1000-86400))
  const [to, setTo] = useState<number>(Math.floor(Date.now()/1000))
  const [granularity, setGranularity] = useState<string>('1m')
  const [isLive, setIsLive] = useState<boolean>(true)
  const [lastReadingTime, setLastReadingTime] = useState<number>(0)
  const [mostRecentReading, setMostRecentReading] = useState<{value: number, timestamp: number} | null>(readings.length > 0 ? readings[0] : null)

  const handleFetchReadings = async () => {
    try {
      console.log('Fetching readings')
      let res
      if (isLive) {
        res = await fetch(`${API_URL}/glucose-readings?order=desc&granularity=${granularity}&from=${from}`, {
          headers: {
            'X-API-KEY': API_KEY
          }
        })
      } else {
        res = await fetch(`${API_URL}/glucose-readings?order=desc&granularity=${granularity}&from=${from}&to=${to}`, {
          headers: {
            'X-API-KEY': API_KEY
          }
        })
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
      setLastReadingTime(data[0].timestamp)
      setReadings(data)
      console.log('Readings:', data)
    } catch (err) {
      console.error('Failed to fetch readings:', err)
      alert('Error fetching readings')
    }
  }

  // Automatically load readings on component mount
  useEffect(() => {
    handleFetchReadings()
    setMostRecentReading(readings[0])
  }, [])

  // Real-time stream data
  // const [testData, setTestData] = useState<string[]>([])
  useEffect(() => {
    const eventSource = new EventSource('http://localhost:8000/api/glucose-readings/stream', {
      fetch: (input, init) => 
        fetch(input, {
          ...init,
          headers: {
            ...init.headers,
            'X-API-KEY': API_KEY
          }
        })
    })
    eventSource.onmessage = (event) => {
      console.log('Received SSE:', event.data)
      console.log('Data type:', typeof event.data)
      try {
        const parsed = JSON.parse(event.data)
        setMostRecentReading(parsed[0])
        console.log('Parsed:', parsed)
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
          if (dataNew.length > 0) {
            setLastReadingTime(dataNew[0].timestamp)
            setReadings(prev => [...dataNew, ...prev])
          }
          console.log('New readings:', dataNew)
        } catch (err) {
          console.error('Failed to fetch new readings:', err)
          alert('Error fetching new readings')
        }
    }, 60000)
    return () => clearInterval(interval)
  }, [readings])




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

          <h2>Live Reading</h2>
          {mostRecentReading && (
            <ReadingDisplay reading={mostRecentReading} />
          )}

          {/* Time since last reading */}
          {mostRecentReading && (
            <TimeDisplay lastReading={mostRecentReading} />
          )}

          {/* Line chart */}
          <h2>Glucose Trend</h2>
          <GlucoseChart readings={readings} />
        </div>
      )}
    </div>
  )
}

export default App
