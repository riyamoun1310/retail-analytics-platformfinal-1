import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Package, 
  ShoppingCart, 
  Users, 
  Warehouse,
  BarChart3, 
  Brain
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Products', href: '/products', icon: Package },
  { name: 'Sales', href: '/sales', icon: ShoppingCart },
  { name: 'Customers', href: '/customers', icon: Users },
  { name: 'Inventory', href: '/inventory', icon: Warehouse },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'AI Reports', href: '/reports', icon: Brain },
]

const Sidebar: React.FC = () => {
  const location = useLocation()

  return (
    <div className="bg-white w-64 min-h-screen shadow-sm border-r border-gray-200">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="bg-primary-600 rounded-lg p-2">
            <BarChart3 className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">RetailAnalytics</h1>
            <p className="text-sm text-gray-500">AI-Powered Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          const Icon = item.icon
          
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`sidebar-item ${isActive ? 'active' : ''}`}
            >
              <Icon className="h-5 w-5 mr-3" />
              <span className="font-medium">{item.name}</span>
            </Link>
          )
        })}
      </nav>

      {/* Bottom Section */}
      <div className="absolute bottom-4 left-4 right-4">
        <div className="bg-gradient-to-r from-primary-50 to-blue-50 rounded-lg p-4 border border-primary-200">
          <div className="flex items-center space-x-2 mb-2">
            <Brain className="h-5 w-5 text-primary-600" />
            <span className="font-semibold text-primary-900">AI Insights</span>
          </div>
          <p className="text-sm text-primary-700 mb-3">
            Get intelligent recommendations based on your data
          </p>
          <Link 
            to="/reports" 
            className="btn-primary text-sm w-full text-center block"
          >
            Generate Report
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
