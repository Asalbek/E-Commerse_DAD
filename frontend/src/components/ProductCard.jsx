import { Link } from 'react-router-dom'

export default function ProductCard({ product }) {
  const stockLevel = product.stock_quantity > 20 ? 'in-stock'
    : product.stock_quantity > 0 ? 'low-stock' : 'out-of-stock'

  const stockText = product.stock_quantity > 20 ? 'In Stock'
    : product.stock_quantity > 0 ? `Only ${product.stock_quantity} left` : 'Out of Stock'

  return (
    <Link to={`/product/${product.id}`} className="card product-card" id={`product-${product.id}`}>
      <div className="product-image-wrap">
        <img
          src={product.image_url || `https://picsum.photos/seed/${product.id}/400/400`}
          alt={product.name}
          className="product-image"
          loading="lazy"
        />
        <span className={`badge badge-stock ${stockLevel === 'in-stock' ? 'badge-success' : stockLevel === 'low-stock' ? 'badge-warning' : 'badge-error'}`}>
          {stockText}
        </span>
      </div>
      <div className="card-body">
        <div className="product-category">{product.category?.name || ''}</div>
        <div className="product-name">{product.name}</div>
        <div className="product-price">${product.price?.toFixed(2)}</div>
      </div>
    </Link>
  )
}
