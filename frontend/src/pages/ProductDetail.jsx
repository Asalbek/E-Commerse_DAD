import { useState, useEffect, useContext } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { AuthContext, CartContext, ToastContext } from '../App'

export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { API, token } = useContext(AuthContext)
  const { setCartCount } = useContext(CartContext)
  const { showToast } = useContext(ToastContext)
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [qty, setQty] = useState(1)
  const [liveStock, setLiveStock] = useState(null)

  useEffect(() => {
    fetch(`${API}/products/${id}`)
      .then(r => r.json())
      .then(data => { setProduct(data); setLiveStock(data.stock_quantity); setLoading(false) })
      .catch(() => setLoading(false))
  }, [id])

  // WebSocket for real-time stock updates (R7)
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${protocol}://${window.location.host}/ws/inventory/${id}`)

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.remaining !== undefined) setLiveStock(data.remaining)
      } catch (e) {}
    }

    return () => ws.close()
  }, [id])

  const addToCart = async () => {
    if (!token) { navigate('/login'); return }
    try {
      const res = await fetch(`${API}/cart/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ product_id: parseInt(id), quantity: qty }),
      })
      if (res.ok) {
        const data = await res.json()
        setCartCount(data.item_count)
        showToast('Added to cart!')
      } else {
        const err = await res.json()
        showToast(err.detail || 'Failed', 'error')
      }
    } catch (e) { showToast('Network error', 'error') }
  }

  const [reviews, setReviews] = useState([])
  const [newReview, setNewReview] = useState({ rating: 5, comment: '' })

  useEffect(() => {
    fetch(`${API}/products/${id}/reviews`)
      .then(r => r.json())
      .then(data => setReviews(data))
  }, [id])

  const submitReview = async (e) => {
    e.preventDefault()
    if (!token) { navigate('/login'); return }
    try {
      const res = await fetch(`${API}/products/${id}/reviews`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(newReview),
      })
      if (res.ok) {
        const saved = await res.json()
        setReviews([saved, ...reviews])
        setNewReview({ rating: 5, comment: '' })
        showToast('Review submitted!')
      }
    } catch (e) { showToast('Error', 'error') }
  }

  if (loading) return <div className="loading-page"><div className="spinner"></div></div>
  if (!product) return <div className="container page"><div className="empty-state"><h3>Product not found</h3></div></div>

  const stockLevel = (liveStock ?? product.stock_quantity) > 20 ? 'in-stock'
    : (liveStock ?? product.stock_quantity) > 0 ? 'low-stock' : 'out-of-stock'

  return (
    <div className="page">
      <div className="container">
        <button className="btn btn-ghost btn-sm mb-4" onClick={() => navigate(-1)}>← Back</button>
        <div className="two-col">
          <div>
            <img
              src={product.image_url || `https://picsum.photos/seed/${product.id}/600/600`}
              alt={product.name}
              style={{ width: '100%', borderRadius: 'var(--radius-lg)', aspectRatio: '1', objectFit: 'cover', background: 'var(--bg-hover)' }}
            />
          </div>
          <div>
            <span className="badge badge-accent" style={{ marginBottom: 12 }}>
              {product.category?.name}
            </span>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: 8, letterSpacing: '-0.025em' }}>
              {product.name}
            </h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem', lineHeight: 1.7, marginBottom: 24 }}>
              {product.description}
            </p>

            <div style={{ fontSize: '2rem', fontWeight: 700, marginBottom: 16 }}>
              ${product.price?.toFixed(2)}
            </div>

            <div className="stock-ticker" style={{ marginBottom: 24, display: 'inline-flex' }}>
              <span className={`stock-dot ${stockLevel}`}></span>
              <span>
                {stockLevel === 'in-stock' ? `${liveStock ?? product.stock_quantity} in stock`
                  : stockLevel === 'low-stock' ? `Only ${liveStock ?? product.stock_quantity} left!`
                  : 'Out of stock'}
              </span>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>• Live</span>
            </div>

            <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 24 }}>
              <div className="cart-item-qty">
                <button onClick={() => setQty(Math.max(1, qty - 1))}>−</button>
                <span>{qty}</span>
                <button onClick={() => setQty(qty + 1)}>+</button>
              </div>
              <button
                className="btn btn-primary btn-lg"
                style={{ flex: 1 }}
                onClick={addToCart}
                disabled={stockLevel === 'out-of-stock'}
                id="add-to-cart-btn"
              >
                Add to Cart
              </button>
            </div>

            <div className="divider"></div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
              <div>SKU: {product.sku}</div>
              <div style={{ marginTop: 4 }}>Category: {product.category?.name}</div>
            </div>
          </div>
        </div>

        {/* Reviews Section */}
        <div style={{ marginTop: 64 }}>
          <h2 style={{ marginBottom: 32, fontSize: '1.5rem', fontWeight: 700 }}>Customer Reviews</h2>
          
          <div className="two-col" style={{ alignItems: 'start', gap: 48 }}>
            <div className="card" style={{ padding: 24 }}>
              <h3 style={{ marginBottom: 16, fontSize: '1.125rem' }}>Write a Review</h3>
              <form onSubmit={submitReview}>
                <div style={{ marginBottom: 16 }}>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>Rating</label>
                  <select 
                    className="input" 
                    value={newReview.rating} 
                    onChange={e => setNewReview({...newReview, rating: parseInt(e.target.value)})}
                  >
                    {[5,4,3,2,1].map(r => <option key={r} value={r}>{r} Stars</option>)}
                  </select>
                </div>
                <div style={{ marginBottom: 24 }}>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8 }}>Comment</label>
                  <textarea 
                    className="input" 
                    rows="4" 
                    placeholder="What did you think of this product?"
                    value={newReview.comment}
                    onChange={e => setNewReview({...newReview, comment: e.target.value})}
                  ></textarea>
                </div>
                <button type="submit" className="btn btn-primary btn-block">Post Review</button>
              </form>
            </div>

            <div>
              {reviews.length === 0 ? (
                <div className="empty-state" style={{ padding: '32px 0' }}>
                  <p style={{ color: 'var(--text-muted)' }}>No reviews yet. Be the first to review!</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                  {reviews.map(review => (
                    <div key={review.id} style={{ paddingBottom: 24, borderBottom: '1px solid var(--border-color)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                        <span style={{ fontWeight: 600 }}>{review.user_name}</span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {new Date(review.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div style={{ color: '#fbbf24', marginBottom: 8 }}>
                        {'★'.repeat(review.rating)}{'☆'.repeat(5 - review.rating)}
                      </div>
                      <p style={{ fontSize: '0.9375rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                        {review.comment}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
