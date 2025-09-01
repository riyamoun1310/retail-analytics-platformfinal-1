#!/bin/bash
# Quick test script for deployment

echo "🚀 Testing Retail Analytics Platform Setup..."
echo ""

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: Run this from the project root directory"
    exit 1
fi

echo "✅ Project structure looks good"

# Check if frontend directory exists
if [ -d "frontend" ]; then
    echo "✅ Frontend directory exists"
else
    echo "❌ Frontend directory missing"
    exit 1
fi

# Check if api directory exists
if [ -d "api" ]; then
    echo "✅ API directory exists"
else
    echo "❌ API directory missing"
    exit 1
fi

# Check if required files exist
echo ""
echo "📁 Checking required files..."

files=("vercel.json" "api/index.py" "api/requirements.txt" "frontend/package.json")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
    fi
done

echo ""
echo "🎯 Ready for deployment!"
echo ""
echo "Next steps:"
echo "1. git add ."
echo "2. git commit -m 'Ready for deployment'"
echo "3. git push origin main"
echo "4. Deploy on Vercel"
echo ""
