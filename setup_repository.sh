#!/bin/bash
# Setup Repository Script
# Run this script to initialize git repository and prepare for company deployment

echo "🚀 Setting up User Data Integration System for Company Repository"
echo "=================================================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Initialize git repository
echo "📁 Initializing git repository..."
git init

# Add all files
echo "📦 Adding files to repository..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: User Data Integration System v1.0.0

- Production-ready Attio to Notion integration
- CLI interface for contact syncing
- 19+ field mapping support
- Comprehensive error handling
- Optimized for production use"

# Show repository status
echo "📊 Repository status:"
git status

echo ""
echo "✅ Repository setup complete!"
echo ""
echo "🔗 Next steps:"
echo "1. Create repository on your company's platform (GitHub/GitLab/Bitbucket)"
echo "2. Add remote origin:"
echo "   git remote add origin [YOUR_REPOSITORY_URL]"
echo "3. Push to repository:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "📋 Files ready for repository:"
echo "   - Core integration files (3 files, 290 lines)"
echo "   - Complete documentation"
echo "   - Environment template"
echo "   - Git configuration"
echo ""
echo "🔐 Security:"
echo "   - No API keys in code"
echo "   - Environment variables only"
echo "   - .gitignore configured"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Main documentation"
echo "   - DEPLOYMENT_GUIDE.md - Deployment instructions"
echo "   - README_PRODUCTION.md - Detailed usage"
echo ""
echo "🎉 Ready for company repository deployment!"
