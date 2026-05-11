import { useState, useEffect, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../App'

export default function Orders() {
  const { API, token } = useContext(AuthContext)
  const navigate = useNavigate()
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) { navigate('/login'); return }
    fetch(`${API}/orders`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { setOrders(data.items || []); setLoading(false) })
      .catch(() => setLoading(false))
  }, [token])

  const statusColors = {
    pending: 'badge-warning', paid: 'badge-accent', fulfilled: 'badge-accent',
    shipped: 'badge-success', delivered: 'badge-success', cancelled: 'badge-error',
  }

  if (loading) return <div className="loading-page"><div className="spinner"></div></div>

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 800 }}>
        <h1 className="page-title" style={{ marginBottom: 32 }}>My Orders</h1>

        {orders.length === 0 ? (
          <div className="empty-state">
            <h3>No orders yet</h3>
            <p>Your order history will appear here</p>
          </div>
        ) : (
          orders.map(order => (
            <div key={order.id} className="order-card" id={`order-${order.id}`}>
              <div className="order-header">
                <div>
                  <div className="order-id">Order #{order.id}</div>
                  <div className="order-date">{new Date(order.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className={`badge ${statusColors[order.status] || 'badge-accent'}`}>
                    {order.status}
                  </span>
                  <div className="order-total" style={{ marginTop: 4 }}>
                    ${order.total_amount?.toFixed(2)}
                  </div>
                </div>
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                {order.items?.map(item => (
                  <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span>{item.product_name} × {item.quantity}</span>
                    <span>${(item.unit_price * item.quantity).toFixed(2)}</span>
                  </div>
                ))}
              </div>
              {order.shipment?.tracking_number && (
                <div style={{ marginTop: 12, padding: '8px 12px', background: 'var(--bg-hover)', borderRadius: 'var(--radius-md)', fontSize: '0.8125rem' }}>
                  📦 Tracking: <strong>{order.shipment.tracking_number}</strong>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
