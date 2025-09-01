import httpx
from typing import Dict, Any, List
from datetime import datetime
import json
import os
from app.core.config import settings

class GenAIService:
    def __init__(self):
        # Initialize Tavily API key
        self.api_key = settings.TAVILY_API_KEY if hasattr(settings, 'TAVILY_API_KEY') else os.getenv('TAVILY_API_KEY')
        self.api_url = "https://api.tavily.com/v1/generate"
    
    async def generate_report(self, report_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a natural language report from data"""
        
        # Create context-specific prompts
        prompts = {
            "sales_summary": self._create_sales_summary_prompt(data),
            "inventory_status": self._create_inventory_prompt(data),
            "customer_insights": self._create_customer_insights_prompt(data),
            "product_performance": self._create_product_performance_prompt(data)
        }
        
        prompt = prompts.get(report_type, self._create_generic_prompt(data))
        
        try:
            # Generate report using Tavily
            if self.api_key:
                response = await self._generate_with_tavily(prompt)
            else:
                # Fallback to template-based generation
                response = self._generate_template_report(report_type, data)
            return self._parse_report_response(response)
        except Exception as e:
            # Fallback to template-based generation on error
            return self._generate_template_report(report_type, data)
    
    async def answer_question(self, question: str, context: Dict[str, Any]) -> str:
        """Answer a business question using the provided context"""
        
        prompt = f"""
        You are a retail analytics assistant. Based on the following business data, answer the user's question in a clear and actionable way.
        
        Business Context:
        {json.dumps(context, indent=2, default=str)}
        
        User Question: {question}
        
        Please provide a concise and helpful answer based on the data provided.
        """
        
        try:
            if self.api_key:
                response = await self._generate_with_tavily(prompt)
                return response
            else:
                return self._answer_question_template(question, context)
        except Exception as e:
            return f"I apologize, but I'm unable to process your question at the moment. Error: {str(e)}"
    
    async def _generate_with_tavily(self, prompt: str) -> str:
        """Generate response using Tavily API"""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"prompt": prompt, "max_tokens": 1500, "temperature": 0.7}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(self.api_url, headers=headers, json=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                # Tavily API expected to return {'result': '...'}
                return data.get("result", "")
            except Exception as e:
                raise Exception(f"Tavily API error: {str(e)}")
    
    def _create_sales_summary_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for sales summary report"""
        return f"""
        Generate a comprehensive sales summary report based on the following data:
        
        Period: {data.get('period', 'N/A')}
        Total Revenue: ${data.get('total_revenue', 0):,.2f}
        Total Orders: {data.get('total_orders', 0):,}
        Average Order Value: ${data.get('avg_order_value', 0):.2f}
        
        Top Products:
        {self._format_top_products(data.get('top_products', []))}
        
        Category Performance:
        {self._format_category_sales(data.get('category_sales', []))}
        
        Please provide:
        1. A brief executive summary (2-3 sentences)
        2. Detailed analysis of key metrics and trends
        3. 3-5 actionable recommendations for improvement
        
        Format the response as JSON with keys: "summary", "detailed_analysis", "recommendations" (as a list)
        """
    
    def _create_inventory_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for inventory status report"""
        return f"""
        Generate an inventory status report based on the following data:
        
        Total Products: {data.get('total_products', 0):,}
        Total Stock Units: {data.get('total_stock_units', 0):,}
        Inventory Value: ${data.get('inventory_value', 0):,.2f}
        
        Low Stock Products ({len(data.get('low_stock_products', []))} items):
        {self._format_low_stock_products(data.get('low_stock_products', []))}
        
        Stock by Category:
        {self._format_stock_by_category(data.get('stock_by_category', []))}
        
        Please provide:
        1. A brief executive summary of inventory health
        2. Detailed analysis of stock levels and potential issues
        3. 3-5 actionable recommendations for inventory optimization
        
        Format the response as JSON with keys: "summary", "detailed_analysis", "recommendations" (as a list)
        """
    
    def _create_customer_insights_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for customer insights report"""
        return f"""
        Generate a customer insights report based on the following data:
        
        Total Customers: {data.get('total_customers', 0):,}
        New Customers: {data.get('new_customers', 0):,}
        
        Customer Segments:
        {self._format_customer_segments(data.get('customer_segments', []))}
        
        Top Customers:
        {self._format_top_customers(data.get('top_customers', []))}
        
        Please provide:
        1. A brief executive summary of customer base health
        2. Detailed analysis of customer behavior and segmentation
        3. 3-5 actionable recommendations for customer retention and growth
        
        Format the response as JSON with keys: "summary", "detailed_analysis", "recommendations" (as a list)
        """
    
    def _create_product_performance_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for product performance report"""
        return f"""
        Generate a product performance report based on the following data:
        
        Analysis Period: {data.get('period', 'N/A')}
        
        Top Performing Products:
        {self._format_product_performance(data.get('top_performers', []))}
        
        Please provide:
        1. A brief executive summary of product performance
        2. Detailed analysis of top performers and trends
        3. 3-5 actionable recommendations for product strategy
        
        Format the response as JSON with keys: "summary", "detailed_analysis", "recommendations" (as a list)
        """
    
    def _create_generic_prompt(self, data: Dict[str, Any]) -> str:
        """Create generic prompt for unknown report types"""
        return f"""
        Generate a business intelligence report based on the following data:
        
        {json.dumps(data, indent=2, default=str)}
        
        Please provide:
        1. A brief executive summary
        2. Detailed analysis of the data
        3. 3-5 actionable recommendations
        
        Format the response as JSON with keys: "summary", "detailed_analysis", "recommendations" (as a list)
        """
    
    def _parse_report_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response and extract structured data"""
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # If not JSON, parse manually
            lines = response.split('\n')
            summary = ""
            detailed_analysis = ""
            recommendations = []
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if "summary" in line.lower() or "executive" in line.lower():
                    current_section = "summary"
                elif "analysis" in line.lower() or "detailed" in line.lower():
                    current_section = "analysis"
                elif "recommendation" in line.lower():
                    current_section = "recommendations"
                elif line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•')):
                    if current_section == "recommendations":
                        recommendations.append(line)
                else:
                    if current_section == "summary":
                        summary += line + " "
                    elif current_section == "analysis":
                        detailed_analysis += line + " "
            
            return {
                "summary": summary.strip() or "Analysis completed successfully.",
                "detailed_analysis": detailed_analysis.strip() or "Detailed metrics have been processed.",
                "recommendations": recommendations if recommendations else ["Continue monitoring key metrics", "Review performance regularly", "Consider optimization opportunities"]
            }
        
        except Exception as e:
            return {
                "summary": "Report generated successfully with available data.",
                "detailed_analysis": f"Analysis completed based on provided metrics. Raw response: {response[:200]}...",
                "recommendations": ["Review data quality", "Monitor key performance indicators", "Consider implementing automated reporting"]
            }
    
    def _generate_template_report(self, report_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report using templates when AI is not available"""
        
        templates = {
            "sales_summary": {
                "summary": f"Sales analysis shows ${data.get('total_revenue', 0):,.2f} in revenue from {data.get('total_orders', 0):,} orders with an average order value of ${data.get('avg_order_value', 0):.2f}.",
                "detailed_analysis": f"The sales performance for the period {data.get('period', 'analyzed')} indicates moderate business activity. Total revenue reached ${data.get('total_revenue', 0):,.2f} across {data.get('total_orders', 0):,} transactions. The average order value of ${data.get('avg_order_value', 0):.2f} suggests customer purchasing behavior is within expected ranges.",
                "recommendations": [
                    "Focus on increasing average order value through upselling",
                    "Analyze top-performing products for expansion opportunities",
                    "Review underperforming categories for improvement",
                    "Implement targeted marketing campaigns for growth"
                ]
            },
            "inventory_status": {
                "summary": f"Inventory analysis reveals {data.get('total_products', 0):,} products with a total value of ${data.get('inventory_value', 0):,.2f}. {len(data.get('low_stock_products', []))} items require attention.",
                "detailed_analysis": f"Current inventory consists of {data.get('total_products', 0):,} active products totaling {data.get('total_stock_units', 0):,} units. The inventory value of ${data.get('inventory_value', 0):,.2f} represents the current investment in stock. There are {len(data.get('low_stock_products', []))} products below reorder levels that need immediate attention.",
                "recommendations": [
                    "Reorder low-stock items immediately",
                    "Review reorder levels for optimization",
                    "Implement automated inventory alerts",
                    "Analyze slow-moving inventory for clearance"
                ]
            },
            "customer_insights": {
                "summary": f"Customer base consists of {data.get('total_customers', 0):,} active customers with {data.get('new_customers', 0):,} new acquisitions in the analyzed period.",
                "detailed_analysis": f"The customer portfolio shows {data.get('total_customers', 0):,} active customers, indicating a stable customer base. Recent acquisition of {data.get('new_customers', 0):,} new customers demonstrates ongoing growth potential. Customer segmentation reveals varying spending patterns across different groups.",
                "recommendations": [
                    "Develop customer retention programs",
                    "Create targeted campaigns for high-value segments",
                    "Improve customer acquisition strategies",
                    "Implement loyalty programs for repeat customers"
                ]
            },
            "product_performance": {
                "summary": f"Product performance analysis shows clear winners and opportunities for optimization across the product portfolio.",
                "detailed_analysis": f"Product performance during {data.get('period', 'the analyzed period')} reveals distinct patterns in sales velocity and revenue generation. Top performers demonstrate strong market demand and should be prioritized for inventory and marketing focus.",
                "recommendations": [
                    "Increase inventory for top-performing products",
                    "Analyze successful product characteristics",
                    "Consider discontinuing poor performers",
                    "Develop marketing campaigns for promising products"
                ]
            }
        }
        
        return templates.get(report_type, templates["sales_summary"])
    
    def _answer_question_template(self, question: str, context: Dict[str, Any]) -> str:
        """Provide template-based answers when AI is not available"""
        
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["sales", "revenue", "orders"]):
            sales_data = context.get("recent_sales", {})
            return f"Based on recent sales data, total revenue is ${sales_data.get('total_revenue', 0):,.2f} from {sales_data.get('total_orders', 0):,} orders. The average order value is ${sales_data.get('avg_order_value', 0):.2f}."
        
        elif any(word in question_lower for word in ["inventory", "stock", "products"]):
            inventory_data = context.get("inventory", {})
            return f"Current inventory includes {inventory_data.get('total_products', 0):,} products with {inventory_data.get('total_stock_units', 0):,} total units valued at ${inventory_data.get('inventory_value', 0):,.2f}."
        
        elif any(word in question_lower for word in ["customers", "customer", "clients"]):
            customer_data = context.get("customers", {})
            return f"The customer base consists of {customer_data.get('total_customers', 0):,} active customers with {customer_data.get('new_customers', 0):,} new acquisitions recently."
        
        else:
            return "I can help you with questions about sales, inventory, customers, and product performance. Please provide more specific details about what you'd like to know."
    
    # Helper methods for formatting data
    def _format_top_products(self, products: List[Dict]) -> str:
        return "\n".join([f"- {p['name']}: {p['quantity_sold']} units, ${p['revenue']:,.2f}" for p in products[:5]])
    
    def _format_category_sales(self, categories: List[Dict]) -> str:
        return "\n".join([f"- {c['category']}: ${c['revenue']:,.2f}" for c in categories])
    
    def _format_low_stock_products(self, products: List[Dict]) -> str:
        return "\n".join([f"- {p['name']}: {p['current_stock']} units (reorder at {p['reorder_level']})" for p in products[:10]])
    
    def _format_stock_by_category(self, categories: List[Dict]) -> str:
        return "\n".join([f"- {c['category']}: {c['total_stock']:,} units" for c in categories])
    
    def _format_customer_segments(self, segments: List[Dict]) -> str:
        return "\n".join([f"- {s['segment']}: {s['count']} customers, avg spent ${s['avg_spent']:,.2f}" for s in segments])
    
    def _format_top_customers(self, customers: List[Dict]) -> str:
        return "\n".join([f"- {c['name']}: ${c['total_spent']:,.2f} ({c['total_orders']} orders)" for c in customers[:5]])
    
    def _format_product_performance(self, products: List[Dict]) -> str:
        return "\n".join([f"- {p['name']} ({p['category']}): {p['units_sold']} units, ${p['revenue']:,.2f}" for p in products[:10]])
