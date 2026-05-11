import { useState, useEffect, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext, ToastContext } from '../App'

export default function Admin() {
  const { API, token, user } = useContext(AuthContext)
  const { showToast } = useContext(ToastContext)
  const navigate = useNavigate()
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token || user?.role !== 'admin') { navigate('/login'); return }
    fetch(`${API}/admin/analytics/sales`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { setAnalytics(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [token, user])

  if (loading) return <div className="loading-page"><div className="spinner"></div></div>

  return (
    <div className="page">
      <div className="container">
        <h1 className="page-title">Admin Dashboard</h1>
        <p className="page-subtitle" style={{ marginBottom: 32 }}>Sales analytics and management</p>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total Orders</div>
            <div className="stat-value">{analytics?.total_orders || 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Revenue</div>
            <div className="stat-value">${(analytics?.total_revenue || 0).toFixed(2)}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Pending Orders</div>
            <div className="stat-value">{analytics?.orders_by_status?.pending || 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Shipped Orders</div>
            <div className="stat-value">{analytics?.orders_by_status?.shipped || 0}</div>
          </div>
        </div>

        {analytics?.top_products?.length > 0 && (
          <div className="card" style={{ marginTop: 24 }}>
            <div className="card-body">
              <h3 style={{ fontWeight: 700, marginBottom: 16 }}>Top Selling Products</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border)', textAlign: 'left' }}>
                    <th style={{ padding: '8px 0', color: 'var(--text-secondary)', fontWeight: 600 }}>Product</th>
                    <th style={{ padding: '8px 0', color: 'var(--text-secondary)', fontWeight: 600 }}>Units Sold</th>
                    <th style={{ padding: '8px 0', color: 'var(--text-secondary)', fontWeight: 600 }}>Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  {analytics.top_products.map((p, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '12px 0', fontWeight: 500 }}>{p.name}</td>
                      <td style={{ padding: '12px 0' }}>{p.total_sold}</td>
                      <td style={{ padding: '12px 0', fontWeight: 600 }}>${p.revenue?.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div style={{ marginTop: 24 }}>
          <a href="/docs" target="_blank" className="btn btn-secondary">
            📄 API Documentation (Swagger)
          </a>
        </div>
      </div>
    </div>
  )
}
