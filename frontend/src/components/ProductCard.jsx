import { Link } from 'react-router-dom'

// Maps product name keywords → relevant image search terms
function getImageUrl(product) {
  if (
    product.image_url &&
    !product.image_url.includes('example.com') &&
    !product.image_url.includes('placeholder') &&
    !product.image_url.includes('picsum')
  ) {
    return product.image_url
  }

  const name = product.name.toLowerCase()
  const category = (product.category?.name || '').toLowerCase()

  // Electronics
  if (name.includes('iphone') || name.includes('apple'))
    return `https://loremflickr.com/400/400/iphone,apple,smartphone?lock=${product.id}`
  if (name.includes('samsung') || name.includes('galaxy'))
    return `https://loremflickr.com/400/400/samsung,galaxy,smartphone?lock=${product.id}`
  if (name.includes('ipad'))
    return `https://loremflickr.com/400/400/ipad,tablet,apple?lock=${product.id}`
  if (name.includes('macbook') || name.includes('laptop'))
    return `https://loremflickr.com/400/400/laptop,macbook,computer?lock=${product.id}`
  if (name.includes('airpod') || name.includes('headphone') || name.includes('earphone'))
    return `https://loremflickr.com/400/400/headphones,earbuds,audio?lock=${product.id}`
  if (name.includes('watch') || name.includes('smartwatch'))
    return `https://loremflickr.com/400/400/smartwatch,applewatch,wearable?lock=${product.id}`
  if (name.includes('tv') || name.includes('television'))
    return `https://loremflickr.com/400/400/television,tv,screen?lock=${product.id}`
  if (name.includes('camera'))
    return `https://loremflickr.com/400/400/camera,photography,lens?lock=${product.id}`
  if (name.includes('keyboard'))
    return `https://loremflickr.com/400/400/keyboard,mechanical,typing?lock=${product.id}`
  if (name.includes('mouse') || name.includes('gaming'))
    return `https://loremflickr.com/400/400/gaming,mouse,computer?lock=${product.id}`
  if (name.includes('speaker') || name.includes('bluetooth'))
    return `https://loremflickr.com/400/400/speaker,bluetooth,audio?lock=${product.id}`
  if (name.includes('phone') || name.includes('mobile') || name.includes('smartphone'))
    return `https://loremflickr.com/400/400/smartphone,mobile,phone?lock=${product.id}`

  // Clothing
  if (name.includes('t-shirt') || name.includes('tshirt') || name.includes('cotton shirt'))
    return `https://loremflickr.com/400/400/tshirt,clothing,fashion?lock=${product.id}`
  if (name.includes('jeans') || name.includes('denim'))
    return `https://loremflickr.com/400/400/jeans,denim,fashion?lock=${product.id}`
  if (name.includes('dress'))
    return `https://loremflickr.com/400/400/dress,fashion,clothing?lock=${product.id}`
  if (name.includes('jacket') || name.includes('hoodie') || name.includes('coat'))
    return `https://loremflickr.com/400/400/jacket,hoodie,fashion?lock=${product.id}`
  if (name.includes('shoe') || name.includes('sneaker') || name.includes('boot') || name.includes('nike') || name.includes('adidas'))
    return `https://loremflickr.com/400/400/sneakers,shoes,footwear?lock=${product.id}`

  // Food & Beverages
  if (name.includes('coffee') || name.includes('espresso'))
    return `https://loremflickr.com/400/400/coffee,espresso,cafe?lock=${product.id}`
  if (name.includes('tea'))
    return `https://loremflickr.com/400/400/tea,herbal,drink?lock=${product.id}`
  if (name.includes('chocolate'))
    return `https://loremflickr.com/400/400/chocolate,sweet,dessert?lock=${product.id}`
  if (name.includes('protein') || name.includes('supplement') || name.includes('vitamin'))
    return `https://loremflickr.com/400/400/protein,supplement,fitness?lock=${product.id}`

  // Books
  if (name.includes('book') || category.includes('book'))
    return `https://loremflickr.com/400/400/book,reading,library?lock=${product.id}`

  // Sports
  if (name.includes('yoga') || name.includes('mat'))
    return `https://loremflickr.com/400/400/yoga,mat,fitness?lock=${product.id}`
  if (name.includes('bike') || name.includes('bicycle') || name.includes('cycling'))
    return `https://loremflickr.com/400/400/bicycle,cycling,sport?lock=${product.id}`
  if (name.includes('football') || name.includes('soccer'))
    return `https://loremflickr.com/400/400/football,soccer,sport?lock=${product.id}`
  if (name.includes('basketball'))
    return `https://loremflickr.com/400/400/basketball,sport,ball?lock=${product.id}`

  // Home & Garden
  if (name.includes('sofa') || name.includes('couch') || name.includes('chair'))
    return `https://loremflickr.com/400/400/sofa,furniture,interior?lock=${product.id}`
  if (name.includes('lamp') || name.includes('light'))
    return `https://loremflickr.com/400/400/lamp,light,interior?lock=${product.id}`
  if (name.includes('plant') || name.includes('flower') || name.includes('garden'))
    return `https://loremflickr.com/400/400/plant,flower,garden?lock=${product.id}`

  // Beauty
  if (name.includes('perfume') || name.includes('cologne') || name.includes('fragrance'))
    return `https://loremflickr.com/400/400/perfume,fragrance,luxury?lock=${product.id}`
  if (name.includes('lipstick') || name.includes('makeup') || name.includes('cosmetic'))
    return `https://loremflickr.com/400/400/makeup,cosmetics,beauty?lock=${product.id}`

  // Automotive
  if (category.includes('automotive') || name.includes('car') || name.includes('tire') || name.includes('wheel'))
    return `https://loremflickr.com/400/400/car,automotive,vehicle?lock=${product.id}`

  // Category fallbacks
  if (category.includes('electronics'))
    return `https://loremflickr.com/400/400/electronics,technology,gadget?lock=${product.id}`
  if (category.includes('clothing'))
    return `https://loremflickr.com/400/400/fashion,clothing,style?lock=${product.id}`
  if (category.includes('sports'))
    return `https://loremflickr.com/400/400/sports,fitness,gym?lock=${product.id}`
  if (category.includes('beauty'))
    return `https://loremflickr.com/400/400/beauty,skincare,cosmetics?lock=${product.id}`
  if (category.includes('food'))
    return `https://loremflickr.com/400/400/food,gourmet,delicious?lock=${product.id}`
  if (category.includes('home'))
    return `https://loremflickr.com/400/400/home,interior,decor?lock=${product.id}`
  if (category.includes('office'))
    return `https://loremflickr.com/400/400/office,workspace,desk?lock=${product.id}`

  // Last fallback — use product name directly
  const keyword = encodeURIComponent(name.split(' ').slice(0, 2).join(','))
  return `https://loremflickr.com/400/400/${keyword}?lock=${product.id}`
}

export default function ProductCard({ product }) {
  const stockLevel = product.stock_quantity > 20 ? 'in-stock'
    : product.stock_quantity > 0 ? 'low-stock' : 'out-of-stock'
  const stockText = product.stock_quantity > 20 ? 'In Stock'
    : product.stock_quantity > 0 ? `Only ${product.stock_quantity} left` : 'Out of Stock'

  return (
    <Link to={`/product/${product.id}`} className="card product-card" id={`product-${product.id}`}>
      <div className="product-image-wrap">
        <img
          src={getImageUrl(product)}
          alt={product.name}
          className="product-image"
          loading="lazy"
        />
        <span className={`badge badge-stock ${
          stockLevel === 'in-stock' ? 'badge-success' :
          stockLevel === 'low-stock' ? 'badge-warning' : 'badge-error'
        }`}>
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
