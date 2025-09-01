import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  TrendingUp, 
  DollarSign, 
  ShoppingCart, 
  Users, 
  Package,
  AlertTriangle,
  Brain,
  Target
} from 'lucide-react'
import { analyticsService, salesService } from '../services/api'
import MetricCard from '../components/Dashboard/MetricCard'
import SalesChart from '../components/Dashboard/SalesChart'
import TopProducts from '../components/Dashboard/TopProducts'
import RecentSales from '../components/Dashboard/RecentSales'
import InventoryAlerts from '../components/Dashboard/InventoryAlerts'
import PredictionInsights from '../components/Dashboard/PredictionInsights'

const Dashboard: React.FC = () => {
  // Fetch dashboard data
  const { data: salesOverview, isLoading: salesLoading } = useQuery({
    queryKey: ['sales-overview'],
    queryFn: () => analyticsService.getSalesOverview().then(res => res.data),
  })

  const { data: inventoryStatus, isLoading: inventoryLoading } = useQuery({
    queryKey: ['inventory-status'],
    queryFn: () => analyticsService.getInventoryStatus().then(res => res.data),
  })

  const { data: customerInsights, isLoading: customerLoading } = useQuery({
    queryKey: ['customer-insights'],
    queryFn: () => analyticsService.getCustomerInsights().then(res => res.data),
  })

  const { data: recentSales, isLoading: recentSalesLoading } = useQuery({
    queryKey: ['recent-sales'],
    queryFn: () => salesService.getSales({ limit: 10 }).then(res => res.data),
  })

  const isLoading = salesLoading || inventoryLoading || customerLoading

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome back! Here's what's happening with your retail business.
          </p>
        </div>
        <div className="flex space-x-3">
          <button className="btn-outline">
            <TrendingUp className="h-4 w-4 mr-2" />
            Export Data
          </button>
          <button className="btn-primary">
            <Brain className="h-4 w-4 mr-2" />
            Generate AI Report
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Revenue"
          value={`$${salesOverview?.total_sales?.toLocaleString() || '0'}`}
          icon={DollarSign}
          trend="up"
          change="+12.5% vs last month"
        />
        <MetricCard
          title="Total Orders"
          value={salesOverview?.total_orders?.toLocaleString() || '0'}
          icon={ShoppingCart}
          trend="up"
          change="+8.2% vs last month"
        />
        <MetricCard
          title="Active Customers"
          value={customerInsights?.total_customers?.toLocaleString() || '0'}
          icon={Users}
          trend="up"
          change="+5.7% vs last month"
        />
        <MetricCard
          title="Products in Stock"
          value={inventoryStatus?.total_products?.toLocaleString() || '0'}
          icon={Package}
          trend="down"
          change="-2.1% vs last month"
        />
      </div>

      {/* Charts and Insights Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Trend Chart */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Sales Trend</h3>
            <select className="text-sm border border-gray-300 rounded-lg px-3 py-1">
              <option>Last 30 days</option>
              <option>Last 7 days</option>
              <option>Last 90 days</option>
            </select>
          </div>
          <SalesChart data={salesOverview?.sales_trend || []} isLoading={isLoading} />
        </div>

        {/* Top Products */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Top Products</h3>
            <button className="text-primary-600 text-sm hover:text-primary-700">
              View all
            </button>
          </div>
          <TopProducts products={salesOverview?.top_products || []} isLoading={isLoading} />
        </div>
      </div>

      {/* Additional Insights Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Sales */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Recent Sales</h3>
            <button className="text-primary-600 text-sm hover:text-primary-700">
              View all
            </button>
          </div>
          <RecentSales sales={recentSales || []} isLoading={recentSalesLoading} />
        </div>

        {/* Inventory Alerts */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Inventory Alerts</h3>
            <div className="flex items-center text-orange-600">
              <AlertTriangle className="h-4 w-4 mr-1" />
              <span className="text-sm font-medium">
                {inventoryStatus?.low_stock_products || 0} items
              </span>
            </div>
          </div>
          <InventoryAlerts 
            lowStockCount={inventoryStatus?.low_stock_products || 0}
            outOfStockCount={inventoryStatus?.out_of_stock_products || 0}
            isLoading={inventoryLoading}
          />
        </div>

        {/* AI Predictions */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">AI Predictions</h3>
            <div className="flex items-center text-purple-600">
              <Brain className="h-4 w-4 mr-1" />
              <span className="text-sm font-medium">Smart Insights</span>
            </div>
          </div>
          <PredictionInsights />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-400 hover:bg-primary-50 transition-colors">
            <div className="text-center">
              <Package className="h-8 w-8 mx-auto text-gray-400 mb-2" />
              <p className="text-sm font-medium text-gray-600">Add Product</p>
            </div>
          </button>
          <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-400 hover:bg-primary-50 transition-colors">
            <div className="text-center">
              <Users className="h-8 w-8 mx-auto text-gray-400 mb-2" />
              <p className="text-sm font-medium text-gray-600">Add Customer</p>
            </div>
          </button>
          <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-400 hover:bg-primary-50 transition-colors">
            <div className="text-center">
              <ShoppingCart className="h-8 w-8 mx-auto text-gray-400 mb-2" />
              <p className="text-sm font-medium text-gray-600">Record Sale</p>
            </div>
          </button>
          <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-400 hover:bg-primary-50 transition-colors">
            <div className="text-center">
              <Target className="h-8 w-8 mx-auto text-gray-400 mb-2" />
              <p className="text-sm font-medium text-gray-600">View Analytics</p>
            </div>
          </button>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
