interface InventoryAlertsProps {
  lowStockCount?: number
  outOfStockCount?: number
  isLoading?: boolean
}

export default function InventoryAlerts({ lowStockCount: _lowStockCount, outOfStockCount: _outOfStockCount, isLoading: _isLoading }: InventoryAlertsProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Inventory Alerts</h3>
      <div className="space-y-3">
        <p className="text-gray-500">No alerts at this time</p>
      </div>
    </div>
  )
}
