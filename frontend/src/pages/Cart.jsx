import { useState, useEffect, useContext } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { AuthContext, CartContext, ToastContext } from '../App'

export default function Cart() {
  const { API, token } = useContext(AuthContext)
  const { setCartCount } = useContext(CartContext)
  const { showToast } = useContext(ToastContext)
  const navigate = useNavigate()
  const [cart, setCart] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) { navigate('/login'); return }
    fetchCart()
  }, [token])

  const fetchCart = async () => {
    const res = await fetch(`${API}/cart`, { headers: { Authorization: `Bearer ${token}` } })
    const data = await res.json()
    setCart(data)
    setCartCount(data.item_count)
    setLoading(false)
  }

  const updateQty = async (itemId, qty) => {
    const res = await fetch(`${API}/cart/items/${itemId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ quantity: qty }),
    })
    if (res.ok) fetchCart()
  }

  const removeItem = async (itemId) => {
    const res = await fetch(`${API}/cart/items/${itemId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) { fetchCart(); showToast('Item removed') }
  }

  if (loading) return <div className="loading-page"><div className="spinner"></div></div>

  return (
    <div className="page">
      <div className="container">
        <h1 className="page-title" style={{ marginBottom: 32 }}>Shopping Cart</h1>

        {!cart || cart.items.length === 0 ? (
          <div className="empty-state">
            <h3>Your cart is empty</h3>
            <p>Add some products to get started</p>
            <Link to="/" className="btn btn-primary">Browse Products</Link>
          </div>
        ) : (
          <div className="two-col">
            <div>
              {cart.items.map(item => (
                <div key={item.id} className="cart-item" id={`cart-item-${item.id}`}>
                  <img src={item.product_image || `https://picsum.photos/seed/${item.product_id}/200`} alt="" className="cart-item-image" />
                  <div className="cart-item-info">
                    <div className="cart-item-name">{item.product_name}</div>
                    <div className="cart-item-price">${item.product_price?.toFixed(2)} each</div>
                  </div>
                  <div className="cart-item-qty">
                    <button onClick={() => updateQty(item.id, item.quantity - 1)}>−</button>
                    <span>{item.quantity}</span>
                    <button onClick={() => updateQty(item.id, item.quantity + 1)}>+</button>
                  </div>
                  <div style={{ fontWeight: 700, minWidth: 80, textAlign: 'right' }}>
                    ${item.subtotal?.toFixed(2)}
                  </div>
                  <button className="btn btn-ghost" onClick={() => removeItem(item.id)} style={{ color: 'var(--error)' }}>✕</button>
                </div>
              ))}
            </div>
            <div className="cart-summary">
              <h3 style={{ fontWeight: 700, marginBottom: 16 }}>Order Summary</h3>
              <div className="cart-summary-row">
                <span>Subtotal ({cart.item_count} items)</span>
                <span>${cart.total.toFixed(2)}</span>
              </div>
              <div className="cart-summary-row">
                <span>Shipping</span>
                <span style={{ color: 'var(--success)' }}>Free</span>
              </div>
              <div className="cart-summary-row total">
                <span>Total</span>
                <span>${cart.total.toFixed(2)}</span>
              </div>
              <button className="btn btn-primary btn-block btn-lg mt-4" onClick={() => navigate('/checkout')} id="checkout-btn">
                Proceed to Checkout
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
