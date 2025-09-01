import axios from 'axios'

// Handle different environments
const getApiBaseUrl = () => {
  // Production environment (Vercel)
  if (import.meta.env.PROD) {
    return import.meta.env.VITE_API_BASE_URL || window.location.origin
  }
  // Development environment
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
}

const API_BASE_URL = getApiBaseUrl()

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000, // Increased timeout for serverless functions
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API Types
export interface Product {
  id: number
  name: string
  category: string
  subcategory?: string
  brand?: string
  price: number
  cost?: number
  description?: string
  sku: string
  stock_quantity: number
  reorder_level: number
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface Customer {
  id: number
  first_name: string
  last_name: string
  email: string
  phone?: string
  address?: string
  city?: string
  state?: string
  zip_code?: string
  country: string
  date_of_birth?: string
  customer_segment?: string
  total_spent: number
  total_orders: number
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface Sale {
  id: number
  product_id: number
  customer_id: number
  quantity: number
  unit_price: number
  total_amount: number
  discount_amount: number
  tax_amount: number
  final_amount: number
  sale_date: string
  payment_method?: string
  store_location?: string
  sales_channel: string
  transaction_id: string
  created_at: string
  product: Product
  customer: Customer
}

export interface SalesAnalytics {
  total_sales: number
  total_orders: number
  average_order_value: number
  top_products: Array<{
    name: string
    category: string
    total_quantity: number
    total_revenue: number
  }>
  top_customers: Array<{
    name: string
    email: string
    total_spent: number
    total_orders: number
  }>
  sales_by_category: Array<{
    category: string
    total_revenue: number
    total_quantity: number
  }>
  sales_trend: Array<{
    date: string
    revenue: number
    orders: number
  }>
}

export interface PredictionResponse {
  product_id: number
  product_name: string
  predicted_quantity: number
  confidence_score: number
  prediction_date: string
  model_version: string
}

export interface ReportResponse {
  report_type: string
  summary: string
  detailed_analysis: string
  recommendations: string[]
  generated_at: string
}

// API Services
export const productService = {
  getProducts: (params?: { skip?: number; limit?: number; category?: string; is_active?: boolean }) =>
    api.get<Product[]>('/products', { params }),
  
  getProduct: (id: number) =>
    api.get<Product>(`/products/${id}`),
  
  createProduct: (data: Omit<Product, 'id' | 'created_at' | 'updated_at'>) =>
    api.post<Product>('/products', data),
  
  updateProduct: (id: number, data: Partial<Product>) =>
    api.put<Product>(`/products/${id}`, data),
  
  deleteProduct: (id: number) =>
    api.delete(`/products/${id}`),
  
  getLowStockProducts: () =>
    api.get('/products/low-stock/alert'),
}

export const customerService = {
  getCustomers: (params?: { skip?: number; limit?: number; customer_segment?: string; is_active?: boolean }) =>
    api.get<Customer[]>('/customers', { params }),
  
  getCustomer: (id: number) =>
    api.get<Customer>(`/customers/${id}`),
  
  createCustomer: (data: Omit<Customer, 'id' | 'total_spent' | 'total_orders' | 'created_at' | 'updated_at'>) =>
    api.post<Customer>('/customers', data),
  
  updateCustomer: (id: number, data: Partial<Customer>) =>
    api.put<Customer>(`/customers/${id}`, data),
  
  deleteCustomer: (id: number) =>
    api.delete(`/customers/${id}`),
  
  getCustomerStats: (id: number) =>
    api.get(`/customers/${id}/stats`),
}

export const salesService = {
  getSales: (params?: { 
    skip?: number
    limit?: number
    start_date?: string
    end_date?: string
    customer_id?: number
    product_id?: number
  }) =>
    api.get<Sale[]>('/sales', { params }),
  
  getSale: (id: number) =>
    api.get<Sale>(`/sales/${id}`),
  
  createSale: (data: {
    product_id: number
    customer_id: number
    quantity: number
    unit_price: number
    discount_amount?: number
    tax_amount?: number
    payment_method?: string
    store_location?: string
    sales_channel?: string
    transaction_id: string
  }) =>
    api.post<Sale>('/sales', data),
  
  getDailySummary: (date?: string) =>
    api.get('/sales/daily/summary', { params: { date } }),
  
  getWeeklySummary: (week_start?: string) =>
    api.get('/sales/weekly/summary', { params: { week_start } }),
  
  getMonthlySummary: (year?: number, month?: number) =>
    api.get('/sales/monthly/summary', { params: { year, month } }),
}

export const analyticsService = {
  getSalesOverview: (start_date?: string, end_date?: string) =>
    api.get<SalesAnalytics>('/analytics/sales-overview', { 
      params: { start_date, end_date } 
    }),
  
  getInventoryStatus: () =>
    api.get('/analytics/inventory-status'),
  
  getCustomerInsights: () =>
    api.get('/analytics/customer-insights'),
  
  getProductPerformance: (category?: string, days?: number) =>
    api.get('/analytics/product-performance', { 
      params: { category, days } 
    }),
}

export const mlService = {
  predictSales: (product_id: number, days_ahead?: number) =>
    api.post<PredictionResponse>('/ml/predict-sales', { 
      product_id, 
      days_ahead: days_ahead || 7 
    }),
  
  predictSalesBatch: (requests: Array<{ product_id: number; days_ahead?: number }>) =>
    api.post<PredictionResponse[]>('/ml/predict-sales/batch', requests),
  
  retrainModel: () =>
    api.post('/ml/retrain-model'),
  
  getModelInfo: () =>
    api.get('/ml/model-info'),
  
  getModelPerformance: () =>
    api.get('/ml/model-performance'),
  
  getFeatureImportance: () =>
    api.get('/ml/feature-importance'),
  
  optimizeInventory: (product_id: number) =>
    api.post(`/ml/optimize-inventory/${product_id}`),
}

export const reportService = {
  generateReport: (data: {
    report_type: 'sales_summary' | 'inventory_status' | 'customer_insights' | 'product_performance'
    start_date?: string
    end_date?: string
    filters?: any
  }) =>
    api.post<ReportResponse>('/reports/generate', data),
  
  getReportTypes: () =>
    api.get('/reports/types'),
  
  askQuestion: (question: string) =>
    api.post('/reports/ask', { question }),
}

export const healthService = {
  checkHealth: () =>
    api.get('/'),
  
  checkDBHealth: () =>
    api.get('/health'),
}

export default api
