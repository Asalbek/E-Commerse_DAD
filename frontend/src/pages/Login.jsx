import { useState, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext, ToastContext } from '../App'

export default function Login() {
  const { API, login } = useContext(AuthContext)
  const { showToast } = useContext(ToastContext)
  const navigate = useNavigate()
  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    const endpoint = isRegister ? 'register' : 'login'
    const body = isRegister ? { email, password, name } : { email, password }
    try {
      const res = await fetch(`${API}/auth/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (res.ok) {
        login(data.access_token, data.user)
        showToast(`Welcome, ${data.user.name}!`)
        navigate('/')
      } else {
        showToast(data.detail || 'Failed', 'error')
      }
    } catch (e) { showToast('Network error', 'error') }
    setLoading(false)
  }

  return (
    <div className="page">
      <div className="auth-container">
        <div className="auth-card">
          <h1>{isRegister ? 'Create Account' : 'Welcome Back'}</h1>
          <p className="subtitle">{isRegister ? 'Sign up to start shopping' : 'Sign in to your account'}</p>
          <form onSubmit={handleSubmit}>
            {isRegister && (
              <div className="input-group">
                <label>Full Name</label>
                <input className="input" placeholder="John Doe" value={name} onChange={e => setName(e.target.value)} required id="name-input" />
              </div>
            )}
            <div className="input-group">
              <label>Email</label>
              <input className="input" type="email" placeholder="you@example.com" value={email} onChange={e => setEmail(e.target.value)} required id="email-input" />
            </div>
            <div className="input-group">
              <label>Password</label>
              <input className="input" type="password" placeholder="••••••••" value={password} onChange={e => setPassword(e.target.value)} required id="password-input" />
            </div>
            <button type="submit" className="btn btn-primary btn-block btn-lg" disabled={loading} id="auth-submit-btn">
              {loading ? 'Please wait...' : isRegister ? 'Create Account' : 'Sign In'}
            </button>
          </form>
          <div className="auth-divider">or</div>
          <button className="btn btn-secondary btn-block" onClick={() => setIsRegister(!isRegister)}>
            {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Sign up"}
          </button>
          <div style={{ marginTop: 20, padding: 16, background: 'var(--bg-hover)', borderRadius: 'var(--radius-md)', fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
            <strong>Demo accounts:</strong><br/>
            Admin: admin@flashcart.com / admin123<br/>
            Customer: customer@flashcart.com / customer123
          </div>
        </div>
      </div>
    </div>
  )
}
