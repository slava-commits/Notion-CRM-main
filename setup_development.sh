#!/bin/bash

# Development Environment Setup Script
# Run this to set up your development environment

echo "🚀 Setting up User Data Integration Development Environment"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Create development branches
echo "📋 Creating development branches..."

# Create develop branch if it doesn't exist
git checkout -b develop 2>/dev/null || git checkout develop

# Create feature branches for common tasks
git checkout -b feature/enhancements 2>/dev/null || echo "Feature branch already exists"
git checkout -b feature/new-integrations 2>/dev/null || echo "New integrations branch already exists"

# Go back to main
git checkout main

echo "✅ Development branches created"

# Set up git hooks for code quality
echo "🔧 Setting up git hooks..."

mkdir -p .git/hooks

# Pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for code quality

echo "🔍 Running pre-commit checks..."

# Check for TODO comments in production code
if grep -r "TODO\|FIXME\|HACK" src/ --exclude-dir=__pycache__; then
    echo "⚠️  Warning: Found TODO/FIXME/HACK comments in production code"
fi

# Check for debug prints
if grep -r "print(" src/ --exclude-dir=__pycache__; then
    echo "⚠️  Warning: Found print statements in production code"
fi

# Run basic syntax check
python -m py_compile main.py
if [ $? -ne 0 ]; then
    echo "❌ Syntax error found. Commit aborted."
    exit 1
fi

echo "✅ Pre-commit checks passed"
EOF

chmod +x .git/hooks/pre-commit

echo "✅ Git hooks configured"

# Create development configuration
echo "⚙️  Setting up development configuration..."

# Create development environment file
if [ ! -f ".env.development" ]; then
    cp env.template .env.development
    echo "📝 Created .env.development - please add your development API keys"
fi

# Create development requirements
if [ ! -f "requirements-dev.txt" ]; then
    cat > requirements-dev.txt << 'EOF'
# Development dependencies
pytest>=7.0.0
pytest-asyncio>=0.21.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
pre-commit>=2.20.0
EOF
    echo "📦 Created requirements-dev.txt"
fi

echo "✅ Development configuration ready"

# Create development directory structure
echo "📁 Creating development directory structure..."

mkdir -p src/integrations
mkdir -p src/core
mkdir -p src/utils
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p docs/api
mkdir -p scripts/deployment

echo "✅ Directory structure created"

# Create initial development files
echo "📄 Creating development files..."

# Create development README
cat > DEVELOPMENT.md << 'EOF'
# Development Guide

## Quick Start
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up environment
cp .env.development .env
# Edit .env with your API keys

# Run tests
pytest

# Run code formatting
black src/
flake8 src/

# Start development server
python main.py
```

## Development Workflow
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes
3. Run tests: `pytest`
4. Format code: `black src/`
5. Commit: `git commit -m "feat: your feature"`
6. Push: `git push origin feature/your-feature`
7. Create Pull Request on GitHub

## Code Standards
- Follow PEP 8 style guide
- Add type hints
- Write tests for new features
- Update documentation
- Use meaningful commit messages
EOF

echo "✅ Development files created"

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your API keys to .env.development"
echo "2. Install development dependencies: pip install -r requirements-dev.txt"
echo "3. Start developing: git checkout -b feature/your-feature"
echo "4. Run tests: pytest"
echo ""
echo "Happy coding! 🚀"
