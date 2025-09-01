interface SalesChartProps {
  data?: any[]
  isLoading?: boolean
}

export default function SalesChart({ data: _data, isLoading: _isLoading }: SalesChartProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Sales Trends</h3>
      <div className="h-64 flex items-center justify-center text-gray-500">
        Sales chart coming soon...
      </div>
    </div>
  )
}
