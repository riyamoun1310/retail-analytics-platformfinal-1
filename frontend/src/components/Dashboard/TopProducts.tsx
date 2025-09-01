interface TopProductsProps {
  products?: any[]
  isLoading?: boolean
}

export default function TopProducts({ products: _products, isLoading: _isLoading }: TopProductsProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Top Products</h3>
      <div className="space-y-3">
        <p className="text-gray-500">Loading top products...</p>
      </div>
    </div>
  )
}
