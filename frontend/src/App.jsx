
import { useEffect, useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import './App.css'

// Sample security alerts
const sampleAlerts = [
  { id: 'ALT-001', type: 'DDoS', score: 0.92, status: 'pending' },
  { id: 'ALT-002', type: 'PortScan', score: 0.76, status: 'completed' },
  { id: 'ALT-003', type: 'Brute Force', score: 0.84, status: 'pending' },
]

// Sample AI investigation results
const sampleInvestigations = [
  {
    alert_id: 'ALT-002',
    verdict: 'suspicious',
    confidence_score: 0.78,
    explanation:
      'Multiple connection attempts suggest possible port scanning.',
  },
]

// Sample network traffic data
const networkData = [
  { time: '09:00', normal: 120, anomalies: 5 },
  { time: '10:00', normal: 180, anomalies: 12 },
  { time: '11:00', normal: 150, anomalies: 8 },
  { time: '12:00', normal: 220, anomalies: 25 },
  { time: '13:00', normal: 190, anomalies: 18 },
  { time: '14:00', normal: 250, anomalies: 35 },
  { time: '15:00', normal: 210, anomalies: 15 },
]

function App() {
  const [alerts, setAlerts] = useState(sampleAlerts)
  const [backendConnected, setBackendConnected] = useState(false)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/alerts?limit=50')
      .then(response => {
        if (!response.ok) throw new Error('Failed to load alerts')
        return response.json()
      })
      .then(data => {
        if (!Array.isArray(data)) throw new Error('Invalid alerts')
        setAlerts(data)
        setBackendConnected(true)
      })
      .catch(error => {
        console.error('CyberGuard API:', error)
        setBackendConnected(false)
      })
  }, [])
  const [selectedAlert, setSelectedAlert] = useState(null)
  const [trafficData, setTrafficData] = useState(networkData)
  const [summary, setSummary] = useState(null)
  const [extraDataLoaded, setExtraDataLoaded] = useState(false)
  const [extraDataError, setExtraDataError] = useState(false)

  useEffect(() => {
    const controller = new AbortController()

    async function loadExtraData() {
      try {
        const [summaryResponse, trafficResponse] = await Promise.all([
          fetch('http://127.0.0.1:8000/summary', {
            signal: controller.signal,
          }),
          fetch('http://127.0.0.1:8000/traffic?buckets=7', {
            signal: controller.signal,
          }),
        ])

        if (!summaryResponse.ok || !trafficResponse.ok) {
          throw new Error('Failed to load dashboard statistics')
        }

        const [summaryResult, trafficResult] = await Promise.all([
          summaryResponse.json(),
          trafficResponse.json(),
        ])

        if (
          typeof summaryResult.flagged !== 'number' ||
          typeof summaryResult.pending !== 'number' ||
          typeof summaryResult.completed !== 'number' ||
          !Array.isArray(trafficResult)
        ) {
          throw new Error('Unexpected dashboard data')
        }

        if (controller.signal.aborted) return

        setSummary(summaryResult)
        setTrafficData(trafficResult)
        setExtraDataLoaded(true)
      } catch (error) {
        if (controller.signal.aborted) return
        console.error('Dashboard data error:', error)
        setExtraDataError(true)
      }
    }

    loadExtraData()
    return () => controller.abort()
  }, [])

  const selectedInvestigation = selectedAlert
    ? sampleInvestigations.find(
        result => result.alert_id === selectedAlert.id
      )
    : null

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <h2>🛡️ CyberGuard</h2>
        <p>Network Security</p>

        <nav>
          <a href="#dashboard">Dashboard</a>
          <a href="#traffic">Network Traffic</a>
          <a href="#alerts">Security Alerts</a>
          <a href="#investigations">AI Investigations</a>
        </nav>
      </aside>

      {/* Main dashboard */}
      <main className="main" id="dashboard">
        <h1>Security Dashboard</h1>
        <p>Network Anomaly Detection & Threat Analysis</p>

        {/* Statistics */}
        <div className="stats">
          <div className="stat-card">
            <h3>Total Alerts</h3>
            <h2>{extraDataLoaded ? summary.flagged : alerts.length}</h2>
          </div>

          <div className="stat-card">
            <h3>Pending Investigation</h3>
            <h2>
              {extraDataLoaded ? summary.pending : alerts.filter(a => a.status === 'pending').length}
            </h2>
          </div>

          <div className="stat-card">
            <h3>Completed</h3>
            <h2>
              {extraDataLoaded ? summary.completed : alerts.filter(a => a.status === 'completed').length}
            </h2>
          </div>
        </div>

        {/* Network traffic chart */}
        <section id="traffic" className="traffic-section">
          <h2>Network Traffic Overview</h2>
          <p>
            {extraDataLoaded
              ? 'Normal vs. anomalous records (NSL-KDD dataset windows)'
              : 'Normal vs. anomalous records (sample data)'}
          </p>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trafficData}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#334155"
                />

                <XAxis dataKey="time" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />

                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    color: '#ffffff',
                  }}
                />

                <Legend />

                <Line
                  type="monotone"
                  dataKey="normal"
                  name="Normal Traffic"
                  stroke="#22c55e"
                  strokeWidth={3}
                />

                <Line
                  type="monotone"
                  dataKey="anomalies"
                  name="Anomalies"
                  stroke="#ef4444"
                  strokeWidth={3}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Security alerts */}
        <section id="alerts">
          <h2>Recent Security Alerts</h2>
          <p>Click an alert to view its details.</p>

          <table>
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Attack Type</th>
                <th>Anomaly Score</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {alerts.map(alert => (
                <tr
                  key={alert.id}
                  className="clickable-row"
                  onClick={() => setSelectedAlert(alert)}
                  onKeyDown={event => {
                    if (
                      event.key === 'Enter' ||
                      event.key === ' '
                    ) {
                      event.preventDefault()
                      setSelectedAlert(alert)
                    }
                  }}
                  tabIndex={0}
                  aria-selected={selectedAlert?.id === alert.id}
                >
                  <td>{alert.id}</td>
                  <td>{alert.type}</td>
                  <td>{alert.score.toFixed(2)}</td>
                  <td>
                    <span className={`status ${alert.status}`}>
                      {alert.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        {/* Selected alert details */}
        {selectedAlert && (
          <section className="alert-details">
            <div className="details-header">
              <h2>Selected Alert Details</h2>

              <button
                type="button"
                onClick={() => setSelectedAlert(null)}
              >
                Close
              </button>
            </div>

            <p>
              <strong>Alert ID:</strong> {selectedAlert.id}
            </p>

            <p>
              <strong>Attack Type:</strong> {selectedAlert.type}
            </p>

            <p>
              <strong>Anomaly Score:</strong>{' '}
              {selectedAlert.score.toFixed(2)}
            </p>

            <p>
              <strong>Status:</strong> {selectedAlert.status}
            </p>

            {selectedInvestigation ? (
              <div className="selected-investigation">
                <h3>AI Investigation</h3>

                <p>
                  <strong>Verdict:</strong>{' '}
                  {selectedInvestigation.verdict}
                </p>

                <p>
                  <strong>Confidence:</strong>{' '}
                  {(
                    selectedInvestigation.confidence_score * 100
                  ).toFixed(0)}%
                </p>

                <p>
                  <strong>Explanation:</strong>{' '}
                  {selectedInvestigation.explanation}
                </p>
              </div>
            ) : (
              <p>
                No completed investigation available for this alert.
              </p>
            )}
          </section>
        )}

        {/* AI investigation results */}
        <section
          id="investigations"
          className="investigations"
        >
          <h2>AI Investigation Results</h2>

          {sampleInvestigations.map(result => (
            <div
              className="investigation-card"
              key={result.alert_id}
            >
              <h3>Alert: {result.alert_id}</h3>

              <p>
                <strong>Verdict:</strong> {result.verdict}
              </p>

              <p>
                <strong>Confidence:</strong>{' '}
                {(result.confidence_score * 100).toFixed(0)}%
              </p>

              <p>
                <strong>AI Explanation:</strong>{' '}
                {result.explanation}
              </p>
            </div>
          ))}
        </section>

        {extraDataError && (
          <p>Statistics and traffic are showing sample data because the API request failed.</p>
        )}

        <p className="demo-note">
          {backendConnected
            ? 'Connected to CyberGuard AI backend — NSL-KDD detection results.'
            : 'Demo data — backend not connected yet.'}
        </p>
      </main>
    </div>
  )
}

export default App
