
import { useState } from 'react'
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
  const [alerts] = useState(sampleAlerts)
  const [selectedAlert, setSelectedAlert] = useState(null)

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
            <h2>{alerts.length}</h2>
          </div>

          <div className="stat-card">
            <h3>Pending Investigation</h3>
            <h2>
              {alerts.filter(a => a.status === 'pending').length}
            </h2>
          </div>

          <div className="stat-card">
            <h3>Completed</h3>
            <h2>
              {alerts.filter(a => a.status === 'completed').length}
            </h2>
          </div>
        </div>

        {/* Network traffic chart */}
        <section id="traffic" className="traffic-section">
          <h2>Network Traffic Overview</h2>
          <p>Normal vs. anomalous records (sample data)</p>

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

        <p className="demo-note">
          Demo data — backend not connected yet.
        </p>
      </main>
    </div>
  )
}

export default App
