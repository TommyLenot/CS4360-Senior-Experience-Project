
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

// Detection API (src/api/app.py); override with VITE_API_URL in frontend/.env
const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'
const ALERT_LIMIT = 50

async function getJson(path, signal) {
  const res = await fetch(`${API_URL}${path}`, { signal })
  if (!res.ok) {
    throw new Error(`${path} returned ${res.status}`)
  }
  return res.json()
}

function App() {
  const [models, setModels] = useState([])
  const [model, setModel] = useState('autoencoder')
  const [summary, setSummary] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [networkData, setNetworkData] = useState([])
  const [investigations, setInvestigations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedAlert, setSelectedAlert] = useState(null)

  // Model list for the picker
  useEffect(() => {
    const controller = new AbortController()
    getJson('/models', controller.signal)
      .then(setModels)
      .catch(err => {
        if (err.name !== 'AbortError') setError(err.message)
      })
    return () => controller.abort()
  }, [])

  // Dashboard data for the selected model
  useEffect(() => {
    const controller = new AbortController()
    const q = `model=${encodeURIComponent(model)}`

    Promise.all([
      getJson(`/summary?${q}`, controller.signal),
      getJson(`/alerts?${q}&limit=${ALERT_LIMIT}`, controller.signal),
      getJson(`/traffic?${q}`, controller.signal),
      getJson('/investigations', controller.signal),
    ])
      .then(([summaryData, alertData, trafficData, investigationData]) => {
        setSummary(summaryData)
        setAlerts(alertData)
        setNetworkData(trafficData)
        setInvestigations(investigationData)
        setLoading(false)
      })
      .catch(err => {
        if (err.name === 'AbortError') return
        setError(err.message)
        setLoading(false)
      })

    return () => controller.abort()
  }, [model])

  function changeModel(key) {
    setModel(key)
    setLoading(true)
    setError(null)
    setSelectedAlert(null)
  }

  const selectedInvestigation = selectedAlert
    ? investigations.find(
        result => result.alert_id === selectedAlert.id
      )
    : null

  const modelName =
    models.find(m => m.key === model)?.name ?? model

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

        {/* Model picker */}
        <div className="controls">
          <label htmlFor="model-select">Detection model</label>
          <select
            id="model-select"
            value={model}
            onChange={event => changeModel(event.target.value)}
            disabled={models.length === 0}
          >
            {models.length === 0 && (
              <option value={model}>{model}</option>
            )}
            {models.map(m => (
              <option key={m.key} value={m.key}>
                {m.name}
              </option>
            ))}
          </select>
        </div>

        {error && (
          <p className="error-banner" role="alert">
            Could not reach the detection API at {API_URL} ({error}).
            Start it from the project root with{' '}
            <code>uvicorn src.api.app:app --reload</code>.
          </p>
        )}

        {loading && !error && (
          <p className="loading-note">Loading {modelName} results…</p>
        )}

        {/* Statistics */}
        <div className="stats">
          <div className="stat-card">
            <h3>Total Alerts</h3>
            <h2>{summary ? summary.flagged.toLocaleString() : '–'}</h2>
          </div>

          <div className="stat-card">
            <h3>Pending Investigation</h3>
            <h2>{summary ? summary.pending.toLocaleString() : '–'}</h2>
          </div>

          <div className="stat-card">
            <h3>Completed</h3>
            <h2>{summary ? summary.completed.toLocaleString() : '–'}</h2>
          </div>
        </div>

        {summary && (
          <p className="model-metrics">
            {modelName} on {summary.rows.toLocaleString()} test records —
            precision {(summary.precision * 100).toFixed(1)}%, recall{' '}
            {(summary.recall * 100).toFixed(1)}%
          </p>
        )}

        {/* Network traffic chart */}
        <section id="traffic" className="traffic-section">
          <h2>Network Traffic Overview</h2>
          <p>
            Normal vs. flagged records. The NSL-KDD test set has no
            timestamps, so each window is an equal slice of the file.
          </p>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={networkData}>
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
          <p>
            Top {ALERT_LIMIT} most suspicious records. Score is how many
            times over the model threshold the record is. Click an alert
            to view its details.
          </p>

          <table>
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Attack Type</th>
                <th>True Label</th>
                <th>Anomaly Score</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {alerts.length === 0 && !loading && (
                <tr>
                  <td colSpan={5}>No alerts.</td>
                </tr>
              )}
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
                  <td>{alert.true_label}</td>
                  <td>{alert.score.toFixed(2)}×</td>
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
              <strong>True Label:</strong> {selectedAlert.true_label}
            </p>

            <p>
              <strong>Anomaly Score:</strong>{' '}
              {selectedAlert.score.toFixed(2)}× threshold
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

          {investigations.length === 0 && (
            <p className="empty-note">
              No investigations yet. Results will appear here once the
              AI investigation component is connected.
            </p>
          )}

          {investigations.map(result => (
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

        <p className="demo-note">
          Live data from the detection API ({API_URL}), replaying the
          NSL-KDD test set.
        </p>
      </main>
    </div>
  )
}

export default App
