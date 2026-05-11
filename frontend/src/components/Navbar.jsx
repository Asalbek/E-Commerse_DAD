import { useContext } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { AuthContext, CartContext } from '../App'

export default function Navbar() {
  const { user, logout } = useContext(AuthContext)
  const { cartCount } = useContext(CartContext)
  const location = useLocation()

  const isActive = (path) => location.pathname === path ? 'nav-link active' : 'nav-link'

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
          </svg>
          FlashCart
        </Link>

        <div className="navbar-links">
          <Link to="/" className={isActive('/')}>Products</Link>
          <Link to="/flash-sales" className={isActive('/flash-sales')}>
            ⚡ Flash Sales
          </Link>
          {user ? (
            <>
              <Link to="/cart" className={isActive('/cart')}>
                Cart
                {cartCount > 0 && <span className="nav-badge">{cartCount}</span>}
              </Link>
              <Link to="/orders" className={isActive('/orders')}>Orders</Link>
              <Link to="/profile" className={isActive('/profile')}>Profile</Link>
              {user.role === 'admin' && (
                <Link to="/admin" className={isActive('/admin')}>Admin</Link>
              )}
              <button onClick={logout} className="nav-link">Logout</button>
            </>
          ) : (
            <Link to="/login" className="btn btn-primary btn-sm">Sign In</Link>
          )}
        </div>
      </div>
    </nav>
  )
}
