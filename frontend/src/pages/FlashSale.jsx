import { useState, useEffect, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext, ToastContext } from '../App'

export default function FlashSale() {
  const { API, token } = useContext(AuthContext)
  const { showToast } = useContext(ToastContext)
  const navigate = useNavigate()
  const [sales, setSales] = useState([])
  const [loading, setLoading] = useState(true)
  const [timers, setTimers] = useState({})

  useEffect(() => {
    fetch(`${API}/flash-sales/active`)
      .then(r => r.json())
      .then(data => { setSales(data || []); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  // Countdown timers
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now()
      const updated = {}
      sales.forEach(sale => {
        const end = new Date(sale.end_time).getTime()
        const diff = Math.max(0, end - now)
        const h = Math.floor(diff / 3600000)
        const m = Math.floor((diff % 3600000) / 60000)
        const s = Math.floor((diff % 60000) / 1000)
        updated[sale.id] = { h, m, s, expired: diff === 0 }
      })
      setTimers(updated)
    }, 1000)
    return () => clearInterval(interval)
  }, [sales])

  // WebSocket for live stock updates
  useEffect(() => {
    const sockets = sales.map(sale => {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const ws = new WebSocket(`${protocol}://${window.location.host}/ws/inventory/${sale.product_id}`)
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          if (data.remaining !== undefined) {
            setSales(prev => prev.map(s =>
              s.id === sale.id ? { ...s, remaining: data.remaining } : s
            ))
          }
        } catch (e) {}
      }
      return ws
    })
    return () => sockets.forEach(ws => ws.close())
  }, [sales.length])

  const purchase = async (saleId) => {
    if (!token) { navigate('/login'); return }
    try {
      const res = await fetch(`${API}/flash-sales/${saleId}/purchase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ quantity: 1 }),
      })
      const data = await res.json()
      if (res.ok) {
        showToast('Flash sale purchase successful! ⚡')
        setSales(prev => prev.map(s => s.id === saleId ? { ...s, remaining: data.remaining_stock } : s))
      } else {
        showToast(data.detail || 'Purchase failed', 'error')
      }
    } catch (e) { showToast('Network error', 'error') }
  }

  if (loading) return <div className="loading-page"><div className="spinner"></div></div>

  return (
    <div className="page">
      <div className="container">
        <div className="flash-banner">
          <h2>⚡ Flash Sales</h2>
          <p>Limited time offers with real-time stock tracking. Grab them before they're gone!</p>
          {sales.length > 0 && timers[sales[0]?.id] && (
            <div className="flash-timer">
              <div className="flash-timer-block">
                <span className="number">{String(timers[sales[0].id].h).padStart(2, '0')}</span>
                <span className="label">Hours</span>
              </div>
              <div className="flash-timer-block">
                <span className="number">{String(timers[sales[0].id].m).padStart(2, '0')}</span>
                <span className="label">Minutes</span>
              </div>
              <div className="flash-timer-block">
                <span className="number">{String(timers[sales[0].id].s).padStart(2, '0')}</span>
                <span className="label">Seconds</span>
              </div>
            </div>
          )}
        </div>

        {sales.length === 0 ? (
          <div className="empty-state">
            <h3>No active flash sales</h3>
            <p>Check back later for amazing deals!</p>
          </div>
        ) : (
          <div className="grid grid-3">
            {sales.map(sale => {
              const percent = sale.stock_limit > 0 ? Math.round(((sale.stock_limit - (sale.remaining ?? 0)) / sale.stock_limit) * 100) : 100
              return (
                <div key={sale.id} className="card" id={`flash-sale-${sale.id}`}>
                  <div className="product-image-wrap">
                    <img src={sale.product_image || `https://picsum.photos/seed/${sale.product_id}/400`} alt={sale.product_name} className="product-image" />
                    <span className="badge badge-sale">⚡ FLASH</span>
                  </div>
                  <div className="card-body">
                    <div className="product-name">{sale.product_name}</div>
                    <div style={{ margin: '8px 0' }}>
                      <span style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--error)' }}>${sale.sale_price?.toFixed(2)}</span>
                      <span className="product-original-price">${sale.original_price?.toFixed(2)}</span>
                    </div>
                    <div style={{ marginBottom: 12 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8125rem', marginBottom: 4 }}>
                        <span style={{ color: 'var(--text-secondary)' }}>{percent}% sold</span>
                        <span style={{ fontWeight: 600 }}>{sale.remaining ?? 0} left</span>
                      </div>
                      <div style={{ height: 6, background: 'var(--bg-hover)', borderRadius: 99, overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${percent}%`, background: percent > 80 ? 'var(--error)' : 'var(--accent)', borderRadius: 99, transition: 'width 0.5s ease' }}></div>
                      </div>
                    </div>
                    <button className="btn btn-primary btn-block" onClick={() => purchase(sale.id)} disabled={(sale.remaining ?? 0) <= 0}>
                      {(sale.remaining ?? 0) <= 0 ? 'Sold Out' : 'Buy Now ⚡'}
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
