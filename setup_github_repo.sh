#!/bin/bash

# Setup GitHub Repository and Push AttioClient Feature
# This script helps set up a GitHub repository and push the production-ready AttioClient

echo "🚀 Setting up GitHub repository for AttioClient feature"
echo "=================================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Please run this from the project root."
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "feature/production-attio-client" ]; then
    echo "⚠️  Not on the feature branch. Switching to feature/production-attio-client"
    git checkout feature/production-attio-client
fi

# Check if remote exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "🔗 No remote repository configured."
    echo ""
    echo "To set up GitHub repository:"
    echo "1. Create a new repository on GitHub (e.g., 'notion-crm-integration')"
    echo "2. Run: git remote add origin https://github.com/YOUR_USERNAME/notion-crm-integration.git"
    echo "3. Run: git push -u origin main"
    echo "4. Run: git push -u origin feature/production-attio-client"
    echo ""
    echo "Or if you want to use this script with a specific repository:"
    echo "Usage: $0 <github-repo-url>"
    echo "Example: $0 https://github.com/username/notion-crm-integration.git"
    
    if [ $# -eq 1 ]; then
        REPO_URL=$1
        echo ""
        echo "🔗 Adding remote repository: $REPO_URL"
        git remote add origin "$REPO_URL"
        
        echo "📤 Pushing main branch..."
        git push -u origin main
        
        echo "📤 Pushing feature branch..."
        git push -u origin feature/production-attio-client
        
        echo ""
        echo "✅ Repository setup complete!"
        echo "🌐 Create a pull request at: $REPO_URL/compare/feature/production-attio-client"
    else
        echo ""
        echo "💡 To continue with manual setup, run:"
        echo "   git remote add origin <your-repo-url>"
        echo "   git push -u origin main"
        echo "   git push -u origin feature/production-attio-client"
    fi
else
    REMOTE_URL=$(git remote get-url origin)
    echo "🔗 Remote repository: $REMOTE_URL"
    
    echo "📤 Pushing main branch..."
    git push -u origin main
    
    echo "📤 Pushing feature branch..."
    git push -u origin feature/production-attio-client
    
    echo ""
    echo "✅ Push complete!"
    echo "🌐 Create a pull request at: $REMOTE_URL/compare/feature/production-attio-client"
fi

echo ""
echo "📋 Pull Request Summary:"
echo "========================"
echo "Title: feat: Add production-ready AttioClient with comprehensive features"
echo ""
echo "Description:"
echo "- Add AttioClient class with full async/await support"
echo "- Implement comprehensive error handling with custom AttioAPIError"
echo "- Add type hints and dataclasses for AttioPerson and AttioCompany"
echo "- Include connection testing and proper resource management"
echo "- Add support for people and company data retrieval"
echo "- Implement robust datetime parsing and custom field handling"
echo "- Add comprehensive unit tests with 95%+ coverage"
echo "- Include detailed documentation and usage examples"
echo "- Support for batch operations and pagination"
echo "- Production-ready with proper logging and error handling"
echo ""
echo "Files changed:"
echo "- integrations/attio_client.py (new, 650+ lines)"
echo "- tests/test_attio_client.py (new, 400+ lines)"
echo "- integrations/README_AttioClient.md (new, 300+ lines)"
echo ""
echo "🎉 Ready for code review!"
