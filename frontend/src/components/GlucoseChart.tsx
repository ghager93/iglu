import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { memo } from "react";

const GMT_TIMEZONE = 'UTC'

export const GlucoseChart = memo(({ readings }: { readings: Array<{ value: number, timestamp: number }> }) => (
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
))