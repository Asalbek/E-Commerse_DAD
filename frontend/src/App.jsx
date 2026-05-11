import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useState, useEffect, createContext } from 'react'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import ProductDetail from './pages/ProductDetail'
import Cart from './pages/Cart'
import Checkout from './pages/Checkout'
import Orders from './pages/Orders'
import FlashSale from './pages/FlashSale'
import Login from './pages/Login'
import Admin from './pages/Admin'
import Profile from './pages/Profile'

export const AuthContext = createContext(null)
export const CartContext = createContext(null)
export const ToastContext = createContext(null)

const API = '/api/v1'

function App() {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [cartCount, setCartCount] = useState(0)
  const [toast, setToast] = useState(null)

  useEffect(() => {
    if (token) {
      fetch(`${API}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.ok ? r.json() : Promise.reject())
        .then(u => setUser(u))
        .catch(() => { setToken(null); localStorage.removeItem('token') })
    }
  }, [token])

  useEffect(() => {
    if (token) {
      fetch(`${API}/cart`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.ok ? r.json() : null)
        .then(data => { if (data) setCartCount(data.item_count) })
        .catch(() => {})
    }
  }, [token])

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }

  const login = (tkn, usr) => {
    setToken(tkn); setUser(usr)
    localStorage.setItem('token', tkn)
  }

  const logout = () => {
    setToken(null); setUser(null); setCartCount(0)
    localStorage.removeItem('token')
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, API }}>
      <CartContext.Provider value={{ cartCount, setCartCount }}>
        <ToastContext.Provider value={{ showToast }}>
          <BrowserRouter>
            <Navbar />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/product/:id" element={<ProductDetail />} />
              <Route path="/cart" element={<Cart />} />
              <Route path="/checkout" element={<Checkout />} />
              <Route path="/orders" element={<Orders />} />
              <Route path="/flash-sales" element={<FlashSale />} />
              <Route path="/login" element={<Login />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="/profile" element={<Profile />} />
            </Routes>
            {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}
          </BrowserRouter>
        </ToastContext.Provider>
      </CartContext.Provider>
    </AuthContext.Provider>
  )
}

export default App
