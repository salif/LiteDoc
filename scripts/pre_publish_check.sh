#!/bin/bash
# pre_publish_check.sh
# Run this BEFORE uploading dist/index.html to GitHub Releases.
# It scans the output for backend URLs, API keys, or leaked secrets.

echo "=================================================="
echo "Pre-Publish Security Check"
echo "=================================================="

FILE="dist/index.html"

if [ ! -f "$FILE" ]; then
    echo "❌ Error: $FILE not found. Run python3 scripts/build.py first."
    exit 1
fi

echo "File to be published:"
ls -lh "$FILE"
echo ""

# Define sensitive patterns
PATTERNS=(
    "sk-[a-zA-Z0-9]{20,}"
    "api_key"
    "Bearer "
    "http://127.0.0.1"
    "http://localhost"
    "LiteDoc-AI-Addon"
    "ai-addon"
    "AI Addon"
    "ai-clean-btn"
    "ai-token-badge"
    "litedoc_ai_token"
)

LEAK_FOUND=0

for pattern in "${PATTERNS[@]}"; do
    if grep -E -q -i "$pattern" "$FILE"; then
        echo "❌ DANGER: Found sensitive pattern '$pattern' in $FILE!"
        LEAK_FOUND=1
    fi
done

if [ "$LEAK_FOUND" -eq 1 ]; then
    echo "=================================================="
    echo "🚨 LEAK DETECTED! DO NOT PUBLISH. 🚨"
    echo "=================================================="
    exit 1
else
    echo "✅ No obvious secrets or backend URLs detected."
    echo "Ready for manual upload to GitHub Releases."
    exit 0
fi
