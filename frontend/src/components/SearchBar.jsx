import { useState, useContext } from 'react'
import { AuthContext } from '../App'

export default function SearchBar({ onSearch }) {
  const [query, setQuery] = useState('')
  const { API } = useContext(AuthContext)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    try {
      const res = await fetch(`${API}/search?q=${encodeURIComponent(query)}`)
      const data = await res.json()
      onSearch(data.items || [], query)
    } catch (err) {
      console.error('Search failed:', err)
    }
  }

  return (
    <form className="search-bar" onSubmit={handleSearch} id="search-form">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8"/>
        <path d="m21 21-4.3-4.3"/>
      </svg>
      <input
        type="text"
        className="input"
        placeholder="Search products..."
        value={query}
        onChange={e => setQuery(e.target.value)}
        id="search-input"
      />
    </form>
  )
}
