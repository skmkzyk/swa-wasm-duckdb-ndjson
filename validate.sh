#!/bin/bash

# Validation script for NDJSON Log Viewer

echo "🔍 Validating NDJSON Log Viewer Project..."
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is missing"
        ((ERRORS++))
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 directory exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 directory is missing"
        ((ERRORS++))
        return 1
    fi
}

# Check project structure
echo "📁 Checking project structure..."
check_file "README.md"
check_file "README-ja.md"
check_file "azure.yaml"
check_file "sample.ndjson"
check_file ".gitignore"
check_dir "infra"
check_dir "src"
check_dir "src/api"
check_dir ".github"
echo ""

# Check infrastructure files
echo "🏗️  Checking infrastructure files..."
check_file "infra/main.bicep"
check_file "infra/main.parameters.json"
check_file "infra/abbreviations.json"
check_file "infra/core/host/staticwebapp.bicep"
echo ""

# Check source files
echo "💻 Checking source files..."
check_file "src/index.html"
check_file "src/staticwebapp.config.json"
check_file "src/api/function_app.py"
check_file "src/api/requirements.txt"
check_file "src/api/host.json"
echo ""

# Check documentation
echo "📚 Checking documentation..."
check_file ".github/copilot-instructions.md"
echo ""

# Validate JSON files
echo "🔬 Validating JSON files..."
for jsonfile in $(find . -name "*.json" -not -path "./.git/*"); do
    if python3 -m json.tool "$jsonfile" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $jsonfile is valid JSON"
    else
        echo -e "${RED}✗${NC} $jsonfile is invalid JSON"
        ((ERRORS++))
    fi
done
echo ""

# Validate Python syntax
echo "🐍 Validating Python syntax..."
for pyfile in $(find src/api -name "*.py"); do
    if python3 -m py_compile "$pyfile" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $pyfile has valid Python syntax"
    else
        echo -e "${RED}✗${NC} $pyfile has Python syntax errors"
        ((ERRORS++))
    fi
done
echo ""

# Check HTML structure
echo "🌐 Checking HTML structure..."
if grep -q "DuckDB WASM" src/index.html; then
    echo -e "${GREEN}✓${NC} index.html contains DuckDB WASM reference"
else
    echo -e "${RED}✗${NC} index.html missing DuckDB WASM reference"
    ((ERRORS++))
fi

if grep -q "type=\"module\"" src/index.html; then
    echo -e "${GREEN}✓${NC} index.html uses ES6 modules"
else
    echo -e "${YELLOW}⚠${NC} index.html might not be using ES6 modules"
    ((WARNINGS++))
fi

if grep -q "@duckdb/duckdb-wasm" src/index.html; then
    echo -e "${GREEN}✓${NC} index.html imports DuckDB WASM from CDN"
else
    echo -e "${RED}✗${NC} index.html missing DuckDB WASM import"
    ((ERRORS++))
fi
echo ""

# Check sample data
echo "📊 Checking sample data..."
if [ -f "sample.ndjson" ]; then
    LINES=$(wc -l < sample.ndjson)
    if [ $LINES -gt 0 ]; then
        echo -e "${GREEN}✓${NC} sample.ndjson contains $LINES lines"
        
        # Validate first line is JSON
        FIRST_LINE=$(head -n 1 sample.ndjson)
        if echo "$FIRST_LINE" | python3 -m json.tool > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} sample.ndjson first line is valid JSON"
        else
            echo -e "${RED}✗${NC} sample.ndjson first line is not valid JSON"
            ((ERRORS++))
        fi
    else
        echo -e "${RED}✗${NC} sample.ndjson is empty"
        ((ERRORS++))
    fi
fi
echo ""

# Check Azure configuration
echo "☁️  Checking Azure configuration..."
if grep -q "language: py" azure.yaml; then
    echo -e "${GREEN}✓${NC} azure.yaml configured for Python"
else
    echo -e "${RED}✗${NC} azure.yaml not configured for Python"
    ((ERRORS++))
fi

if grep -q "staticwebapp" azure.yaml; then
    echo -e "${GREEN}✓${NC} azure.yaml configured for Static Web App"
else
    echo -e "${RED}✗${NC} azure.yaml missing Static Web App configuration"
    ((ERRORS++))
fi
echo ""

# Summary
echo "════════════════════════════════════════════════"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "🚀 Project is ready for deployment!"
    echo ""
    echo "Next steps:"
    echo "  1. Test locally: cd src && python3 -m http.server 8000"
    echo "  2. Open browser: http://localhost:8000"
    echo "  3. Upload sample.ndjson to test"
    echo "  4. Deploy to Azure: azd up"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validation completed with $WARNINGS warning(s)${NC}"
    echo ""
    echo "Project should work, but review warnings above."
    exit 0
else
    echo -e "${RED}✗ Validation failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo ""
    echo "Please fix the errors above before deploying."
    exit 1
fi
