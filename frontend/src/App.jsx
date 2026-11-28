
import { useEffect, useState } from 'react'
import { describeAlert, FAMILY_INFO } from './attackInfo'
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

const scoreFormat = new Intl.NumberFormat('en-US', {
  notation: 'compact',
  maximumFractionDigits: 1,
})

function formatScore(score) {
  return `${scoreFormat.format(score)}×`
}

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
  const [focus, setFocus] = useState('top')
  const [datasets, setDatasets] = useState([])
  const [dataset, setDataset] = useState('nslkdd')
  const [summary, setSummary] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [networkData, setNetworkData] = useState([])
  const [investigations, setInvestigations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedAlert, setSelectedAlert] = useState(null)

  // Load the list of datasets once
  useEffect(() => {
    const controller = new AbortController()

    getJson('/datasets', controller.signal)
      .then(setDatasets)
      .catch(err => {
        if (err.name !== 'AbortError') {
          setError(err.message)
        }
      })

    return () => controller.abort()
  }, [])

  // Load available detection models for the selected dataset
  useEffect(() => {
    const controller = new AbortController()

    getJson(`/models?dataset=${dataset}`, controller.signal)
      .then(setModels)
      .catch(err => {
        if (err.name !== 'AbortError') {
          setError(err.message)
        }
      })

    return () => controller.abort()
  }, [dataset])

  // Load dashboard data for the selected model
  useEffect(() => {
    const controller = new AbortController()
    const q = `model=${encodeURIComponent(model)}&focus=${focus}&dataset=${dataset}`

    Promise.all([
      getJson(`/summary?${q}`, controller.signal),
      getJson(`/alerts?${q}&limit=${ALERT_LIMIT}`, controller.signal),
      getJson(`/traffic?${q}`, controller.signal),
      getJson(`/investigations?${q}&limit=${ALERT_LIMIT}`, controller.signal),
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
  }, [model, focus, dataset])

  // Escape closes the alert pop-up
  useEffect(() => {
    function onKey(event) {
      if (event.key === 'Escape') setSelectedAlert(null)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  function changeDataset(key) {
    const next = datasets.find(d => d.key === key)
    setDataset(key)
    setModel(next?.default_model ?? 'autoencoder')
    setModels([])
    setLoading(true)
    setError(null)
    setSelectedAlert(null)
  }

  function changeModel(key) {
    setModel(key)
    setLoading(true)
    setError(null)
    setSelectedAlert(null)
  }

  function changeFocus(value) {
    setFocus(value)
    setLoading(true)
    setError(null)
    setSelectedAlert(null)
  }

  function hoverText(alertId) {
    const result = investigations.find(r => r.alert_id === alertId)
    if (!result) return undefined
    const parts = result.explanation.split(' | ')
    const reason = parts.length > 2 ? parts.slice(2).join(' → ') : parts[0]
    return `${result.verdict} (${Math.round(result.confidence_score * 100)}%): ${reason}`
  }

  const selectedInvestigation = selectedAlert
    ? investigations.find(
        result => result.alert_id === selectedAlert.id
      )
    : null

  const modelName =
    models.find(m => m.key === model)?.name ?? model

  const datasetName =
    datasets.find(d => d.key === dataset)?.name ?? dataset

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

        {/* Detection model selector */}
        <div className="controls">
          <label htmlFor="dataset-select">Dataset</label>

          <select
            id="dataset-select"
            value={dataset}
            onChange={event => changeDataset(event.target.value)}
            disabled={datasets.length === 0}
          >
            {datasets.length === 0 && (
              <option value={dataset}>{dataset}</option>
            )}

            {datasets.map(d => (
              <option
                key={d.key}
                value={d.key}
                disabled={!d.ready}
                title={d.ready ? undefined : d.reason}
              >
                {d.name}{d.ready ? '' : ' (not set up yet)'}
              </option>
            ))}
          </select>

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

          <label htmlFor="focus-select">Alert list</label>

          <select
            id="focus-select"
            value={focus}
            onChange={event => changeFocus(event.target.value)}
          >
            <option value="top">Highest scores</option>
            <option value="uncertain">Uncertain (agent investigated)</option>
          </select>
        </div>

        {/* API error message */}
        {error && (
          <p className="error-banner" role="alert">
            Could not reach the detection API at {API_URL} ({error}).
            Start it from the project root with{' '}
            <code>uvicorn src.api.app:app --reload</code>.
          </p>
        )}

        {/* Loading indicator */}
        {loading && !error && (
          <p className="loading-note">
            Loading {modelName} results…
          </p>
        )}

        {/* Statistics */}
        <div className="stats">
          <div className="stat-card">
            <h3>Total Alerts (flagged by model)</h3>
            <h2>
              {summary ? summary.flagged.toLocaleString() : '–'}
            </h2>
          </div>

          <div className="stat-card">
            <h3>Investigated by Agent</h3>
            <h2>
              {summary ? summary.investigated.toLocaleString() : '–'}
            </h2>
          </div>

          <div className="stat-card">
            <h3>Confident (no investigation needed)</h3>
            <h2>
              {summary ? summary.confident.toLocaleString() : '–'}
            </h2>
          </div>
        </div>

        {/* Detection model performance */}
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
            {focus === 'uncertain'
              ? `The ${ALERT_LIMIT} highest-scoring alerts the detectors were unsure about, each investigated by the agent.`
              : `The ${ALERT_LIMIT} alerts with the highest scores.`}{' '}
            Score shows how many times over the alert threshold a record
            is. Click an alert to view its details.
          </p>

          <table>
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Attack Family</th>
                <th>Attack Name (dataset label)</th>
                <th>Score (× threshold)</th>
                <th>Agent</th>
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
                  title={hoverText(alert.id)}
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
                  <td>{formatScore(alert.score)}</td>
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
          <div
            className="modal-overlay"
            onClick={() => setSelectedAlert(null)}
          >
          <section
            className="alert-details"
            role="dialog"
            aria-modal="true"
            aria-label="Selected alert details"
            onClick={event => event.stopPropagation()}
          >
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
              <strong>Attack Family:</strong> {selectedAlert.type}
            </p>

            <p>
              <strong>Attack Name (dataset label):</strong> {selectedAlert.true_label}
            </p>

            <p>
              <strong>Score:</strong>{' '}
              {formatScore(selectedAlert.score)} the alert threshold ({selectedAlert.score.toFixed(2)}×)
            </p>

            <p>
              <strong>Agent:</strong> {selectedAlert.status}
            </p>

            {selectedInvestigation ? (
              <div className="selected-investigation">
                <h3>AI Investigation</h3>

                <p>
                  <strong>Verdict:</strong>{' '}
                  {selectedInvestigation.verdict}
                </p>

                <p>
                  <strong>Confidence in verdict:</strong>{' '}
                  {(
                    selectedInvestigation.confidence_score * 100
                  ).toFixed(0)}%
                </p>

                <p>
                  <strong>Why the agent decided this:</strong>{' '}
                  {selectedInvestigation.explanation}
                </p>

                <p>
                  <strong>About this attack:</strong>{' '}
                  {describeAlert(selectedAlert.true_label)}
                </p>

                {FAMILY_INFO[selectedAlert.type] && (
                  <p>
                    <strong>Attack family:</strong>{' '}
                    {FAMILY_INFO[selectedAlert.type]}
                  </p>
                )}
              </div>
            ) : (
              <p>
                No completed investigation available for this alert.
              </p>
            )}
          </section>
          </div>
        )}

        {/* AI investigation results */}
        <section
          id="investigations"
          className="investigations"
        >
          <h2>AI Investigation Results</h2>

          {investigations.length === 0 && (
            <p className="empty-note">
              No investigations for the alerts shown.
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
                <strong>Confidence in verdict:</strong>{' '}
                {(result.confidence_score * 100).toFixed(0)}%
              </p>

              <p>
                <strong>Why the agent decided this:</strong>{' '}
                {result.explanation}
              </p>
            </div>
          ))}
        </section>

        <p className="demo-note">
          Replay of the NSL-KDD test file, served by the detection API
          ({API_URL}). This is recorded data, not live network traffic.
        </p>
      </main>
    </div>
  )
}

export default App
