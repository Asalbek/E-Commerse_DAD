import { useState, useEffect, useContext } from 'react'
import { AuthContext, ToastContext } from '../App'

export default function Profile() {
  const { API, token, user } = useContext(AuthContext)
  const { showToast } = useContext(ToastContext)
  const [profile, setProfile] = useState(null)
  const [addresses, setAddresses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) return
    
    // Fetch profile
    fetch(`${API}/profile`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => setProfile(data))
      
    // Fetch addresses
    fetch(`${API}/profile/addresses`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { setAddresses(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [token])

  if (!token) return <div className="container page"><h3>Please login to view profile</h3></div>
  if (loading) return <div className="loading-page"><div className="spinner"></div></div>

  return (
    <div className="page">
      <div className="container">
        <h1 style={{ marginBottom: 32 }}>Your Profile</h1>
        
        <div className="two-col" style={{ alignItems: 'start' }}>
          <div className="card" style={{ padding: 24 }}>
            <h3 style={{ marginBottom: 24 }}>Account Details</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label className="label">Full Name</label>
                <div className="input" style={{ background: 'var(--bg-hover)' }}>{user?.name}</div>
              </div>
              <div>
                <label className="label">Email Address</label>
                <div className="input" style={{ background: 'var(--bg-hover)' }}>{user?.email}</div>
              </div>
              <div>
                <label className="label">Account Type</label>
                <div className="badge badge-accent">{user?.role}</div>
              </div>
            </div>
          </div>

          <div className="card" style={{ padding: 24 }}>
            <h3 style={{ marginBottom: 24 }}>Shipping Addresses</h3>
            {addresses.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No addresses saved yet.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {addresses.map(addr => (
                  <div key={addr.id} style={{ padding: 16, border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
                    <div style={{ fontWeight: 600, marginBottom: 4 }}>{addr.title} {addr.is_default && <span className="badge badge-accent">Default</span>}</div>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      {addr.address_line1}, {addr.city} {addr.postal_code}
                    </div>
                  </div>
                ))}
              </div>
            )}
            <button className="btn btn-primary btn-sm mt-4" style={{ marginTop: 24 }}>+ Add New Address</button>
          </div>
        </div>
      </div>
    </div>
  )
}
