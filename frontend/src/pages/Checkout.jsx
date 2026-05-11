import { useState, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext, CartContext, ToastContext } from '../App'

export default function Checkout() {
  const { API, token } = useContext(AuthContext)
  const { setCartCount } = useContext(CartContext)
  const { showToast } = useContext(ToastContext)
  const navigate = useNavigate()
  const [address, setAddress] = useState('')
  const [notes, setNotes] = useState('')
  const [method, setMethod] = useState('card')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!address.trim()) { showToast('Please enter shipping address', 'error'); return }
    setSubmitting(true)

    try {
      const res = await fetch(`${API}/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ shipping_address: address, notes, payment_method: method }),
      })
      if (res.ok) {
        setCartCount(0)
        showToast('Order placed successfully! 🎉')
        navigate('/orders')
      } else {
        const err = await res.json()
        showToast(err.detail || 'Failed to place order', 'error')
      }
    } catch (e) { showToast('Network error', 'error') }
    setSubmitting(false)
  }

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 600 }}>
        <h1 className="page-title" style={{ marginBottom: 32 }}>Checkout</h1>
        <div className="card">
          <div className="card-body" style={{ padding: 32 }}>
            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <label>Shipping Address</label>
                <input className="input" placeholder="123 Main St, City, Country" value={address} onChange={e => setAddress(e.target.value)} required id="address-input" />
              </div>
              <div className="input-group">
                <label>Order Notes (optional)</label>
                <input className="input" placeholder="Special instructions..." value={notes} onChange={e => setNotes(e.target.value)} />
              </div>
              <div className="input-group">
                <label>Payment Method</label>
                <div style={{ display: 'flex', gap: 8 }}>
                  {['card', 'paypal', 'bank_transfer'].map(m => (
                    <button key={m} type="button" className={`chip ${method === m ? 'active' : ''}`} onClick={() => setMethod(m)}>
                      {m === 'card' ? '💳 Card' : m === 'paypal' ? '🅿️ PayPal' : '🏦 Bank'}
                    </button>
                  ))}
                </div>
              </div>
              <div className="divider"></div>
              <button type="submit" className="btn btn-primary btn-block btn-lg" disabled={submitting} id="place-order-btn">
                {submitting ? 'Placing Order...' : 'Place Order'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
