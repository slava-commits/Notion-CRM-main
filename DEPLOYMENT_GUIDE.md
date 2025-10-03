# 🚀 Deployment Guide - Company Repository

## 📋 **Pre-Deployment Checklist**

### ✅ **Project Status**
- [x] Code optimized and production-ready
- [x] All unnecessary files removed
- [x] Core functionality tested and working
- [x] Documentation complete
- [x] Dependencies defined

### ✅ **Files Ready for Repository**
```
user-data-integration/
├── main.py                           # Main integration system
├── attio_to_notion_integration.py    # Core integration logic
├── sync_contacts.py                  # CLI interface
├── config.py                         # Configuration management
├── requirements.txt                  # Python dependencies
├── README_PRODUCTION.md              # Production usage guide
├── PRODUCTION_SUMMARY.md             # Project summary
├── data_mapping_report.md            # Field mapping analysis
├── DEPLOYMENT_GUIDE.md               # This file
├── integrations/                     # Integration modules
│   ├── notion_client_updated.py
│   ├── attio_integration_fixed.py
│   └── gmail_integration.py
├── tests/                           # Test files
│   └── run_tests.py
└── client_secret.json               # OAuth credentials (if needed)
```

---

## 🔧 **Repository Setup Steps**

### **1. Initialize Git Repository**
```bash
cd /Users/wwsharkgmail.com/user-data-integration/user-data-integration
git init
git add .
git commit -m "Initial commit: User Data Integration System v1.0.0"
```

### **2. Create .gitignore**
```bash
# Create .gitignore file
cat > .gitignore << 'EOF'
# Environment variables
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
temp/
tmp/

# Archive (if you want to exclude)
archive/
EOF
```

### **3. Create Repository on Company Platform**

#### **Option A: GitHub**
1. Go to your company's GitHub organization
2. Click "New repository"
3. Name: `user-data-integration`
4. Description: "User Data Integration System - Attio to Notion sync"
5. Set visibility (private for company)
6. Don't initialize with README (we have one)

#### **Option B: GitLab**
1. Go to your company's GitLab instance
2. Click "New project"
3. Choose "Create blank project"
4. Project name: `user-data-integration`
5. Set visibility level

#### **Option C: Bitbucket**
1. Go to your company's Bitbucket workspace
2. Click "Create repository"
3. Repository name: `user-data-integration`
4. Set access level

### **4. Connect Local Repository to Remote**
```bash
# Replace with your company's repository URL
git remote add origin https://github.com/your-company/user-data-integration.git
# OR
git remote add origin https://gitlab.com/your-company/user-data-integration.git
# OR
git remote add origin https://bitbucket.org/your-company/user-data-integration.git

# Push to repository
git branch -M main
git push -u origin main
```

---

## 📝 **Repository Documentation**

### **README.md (Main)**
```markdown
# User Data Integration System

A production-ready system for syncing contact data from Attio CRM to Notion Partners CRM database.

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables in `.env`
3. Sync contacts: `python3 sync_contacts.py email@example.com`

## Features

- ✅ Attio CRM integration
- ✅ Notion database sync
- ✅ 19+ field mapping
- ✅ CLI interface
- ✅ Batch processing

See [README_PRODUCTION.md](README_PRODUCTION.md) for detailed usage.

## Security

- API keys stored in environment variables
- No hardcoded credentials
- Secure OAuth implementation

## License

Company proprietary software.
```

### **Environment Setup (.env.example)**
```bash
# Create .env.example for team members
cat > .env.example << 'EOF'
# Notion Configuration
NOTION_TOKEN=your_notion_integration_token_here

# Attio Configuration
ATTIO_API_KEY=your_attio_api_key_here

# Gmail Configuration (optional)
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REFRESH_TOKEN=your_gmail_refresh_token

# System Configuration
TIMEZONE=Europe/London
LOG_LEVEL=INFO
EOF
```

---

## 🔐 **Security Considerations**

### **Sensitive Data**
- ✅ No API keys in code
- ✅ Environment variables only
- ✅ `.env` in `.gitignore`
- ✅ `client_secret.json` can be shared (OAuth config)

### **Access Control**
- Set repository to private
- Add team members with appropriate permissions
- Use branch protection rules
- Require code reviews for main branch

---

## 🚀 **Deployment Options**

### **Option 1: Direct Deployment**
```bash
# Clone on target server
git clone https://github.com/your-company/user-data-integration.git
cd user-data-integration

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values

# Run
python3 sync_contacts.py contact@example.com
```

### **Option 2: Docker Deployment**
```dockerfile
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
EOF
```

### **Option 3: CI/CD Pipeline**
```yaml
# .github/workflows/deploy.yml
name: Deploy Integration System

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python3 tests/run_tests.py
      - name: Deploy
        run: python3 main.py
```

---

## 📊 **Team Onboarding**

### **For New Team Members**
1. Clone repository: `git clone [repo-url]`
2. Install dependencies: `pip install -r requirements.txt`
3. Copy environment template: `cp .env.example .env`
4. Configure API keys in `.env`
5. Test with: `python3 sync_contacts.py test@example.com`

### **Documentation for Team**
- [README_PRODUCTION.md](README_PRODUCTION.md) - Detailed usage
- [PRODUCTION_SUMMARY.md](PRODUCTION_SUMMARY.md) - Project overview
- [data_mapping_report.md](data_mapping_report.md) - Field mappings

---

## 🔄 **Maintenance & Updates**

### **Regular Updates**
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Test changes
python3 tests/run_tests.py
```

### **Version Control**
- Use semantic versioning (v1.0.0, v1.1.0, etc.)
- Tag releases: `git tag v1.0.0`
- Document changes in CHANGELOG.md

---

## 📞 **Support & Contact**

- **Repository**: [Company Repository URL]
- **Documentation**: See README_PRODUCTION.md
- **Issues**: Use repository issue tracker
- **Team Lead**: [Your Name/Contact]

---

*Deployment Guide v1.0.0*  
*Last Updated: September 2025*
