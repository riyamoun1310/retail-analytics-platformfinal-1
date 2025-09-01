interface RecentSalesProps {
  sales?: any[]
  isLoading?: boolean
}

export default function RecentSales({ sales: _sales, isLoading: _isLoading }: RecentSalesProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Sales</h3>
      <div className="space-y-3">
        <p className="text-gray-500">Loading recent sales...</p>
      </div>
    </div>
  )
}
