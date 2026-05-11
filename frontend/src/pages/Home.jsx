import { useState, useEffect, useContext } from 'react'
import { AuthContext, CartContext, ToastContext } from '../App'
import ProductCard from '../components/ProductCard'
import SearchBar from '../components/SearchBar'

export default function Home() {
  const { API } = useContext(AuthContext)
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [activeCategory, setActiveCategory] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchResults, setSearchResults] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchProducts()
    fetchCategories()
  }, [activeCategory])

  const fetchProducts = async () => {
    setLoading(true)
    try {
      let url = `${API}/products?page_size=20`
      if (activeCategory) url += `&category_id=${activeCategory}`
      const res = await fetch(url)
      const data = await res.json()
      setProducts(data.items || [])
    } catch (err) {
      console.error(err)
    }
    setLoading(false)
  }

  const fetchCategories = async () => {
    try {
      const res = await fetch(`${API}/products/categories`)
      const data = await res.json()
      setCategories(data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleSearch = (items, query) => {
    setSearchResults(items)
    setSearchQuery(query)
  }

  const clearSearch = () => {
    setSearchResults(null)
    setSearchQuery('')
  }

  const displayProducts = searchResults || products

  return (
    <div className="page">
      <div className="container">
        <div className="page-header flex-between">
          <div>
            <h1 className="page-title">
              {searchResults ? `Results for "${searchQuery}"` : 'Products'}
            </h1>
            <p className="page-subtitle">
              {searchResults
                ? `${searchResults.length} products found`
                : 'Discover our curated collection'}
            </p>
          </div>
          <SearchBar onSearch={handleSearch} />
        </div>

        {searchResults && (
          <button className="btn btn-ghost btn-sm mb-4" onClick={clearSearch}>
            ← Back to all products
          </button>
        )}

        {!searchResults && (
          <div className="filter-chips">
            <button
              className={`chip ${!activeCategory ? 'active' : ''}`}
              onClick={() => setActiveCategory(null)}
            >
              All
            </button>
            {categories.map(cat => (
              <button
                key={cat.id}
                className={`chip ${activeCategory === cat.id ? 'active' : ''}`}
                onClick={() => setActiveCategory(cat.id)}
              >
                {cat.name}
              </button>
            ))}
          </div>
        )}

        {loading ? (
          <div className="loading-page"><div className="spinner"></div></div>
        ) : displayProducts.length === 0 ? (
          <div className="empty-state">
            <h3>No products found</h3>
            <p>Try adjusting your search or filter criteria</p>
          </div>
        ) : (
          <div className="grid grid-4">
            {displayProducts.map(p => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
