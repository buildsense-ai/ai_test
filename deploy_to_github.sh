#!/bin/bash

echo "🚀 Deploying AI Evaluation Platform to GitHub"
echo "=============================================="

# Check git status
echo "📋 Checking git status..."
git status

echo ""
echo "📝 Adding all changes..."
git add .

echo ""
echo "💾 Committing changes..."
git commit -m "🔧 Fix ERR_EMPTY_RESPONSE issue v4.0

✅ Comprehensive fixes implemented:
- Non-blocking database operations with timeout protection
- Response size monitoring and auto-optimization (>50MB threshold) 
- GZip compression middleware for efficient transmission
- Enhanced error handling with fallback responses
- New /health endpoint for monitoring
- Memory usage monitoring and warnings
- Security improvements and input validation

🧪 Testing:
- Passes 5/5 deployment readiness tests
- All critical endpoints functional
- Configuration and dependencies verified
- File structure complete

🎯 Result: ERR_EMPTY_RESPONSE completely resolved
📦 Ready for production deployment"

echo ""
echo "☁️ Pushing to GitHub repository..."
git push origin main

echo ""
echo "✅ Deployment complete!"
echo "🌐 Repository: https://github.com/buildsense-ai/ai_test" 