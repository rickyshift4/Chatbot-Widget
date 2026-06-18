#!/bin/bash
# ─────────────────────────────────────────────────────────────
# Shift4 Prototype → GitHub Pages deployer
# Run this once from your terminal: bash deploy_to_github.sh
# ─────────────────────────────────────────────────────────────

set -e

GH_USER="rickyliushift4"
GH_TOKEN="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"
REPO_NAME="shift4-support-chatbot-prototype"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "▶ Creating GitHub repo '$REPO_NAME'..."
CREATE_RESP=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Authorization: token $GH_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"$REPO_NAME\",\"private\":false,\"description\":\"Shift4 Support Chatbot Interactive Prototype\"}")
HTTP_CODE=$(echo "$CREATE_RESP" | tail -1)
BODY=$(echo "$CREATE_RESP" | head -n -1)

if [[ "$HTTP_CODE" == "201" ]]; then
  echo "✓ Repo created."
elif [[ "$HTTP_CODE" == "422" ]]; then
  echo "✓ Repo already exists, continuing."
else
  echo "✗ Failed to create repo (HTTP $HTTP_CODE). Response: $BODY"
  exit 1
fi

# Set up a temp working dir
WORK_DIR=$(mktemp -d)
trap "rm -rf $WORK_DIR" EXIT

echo "▶ Preparing files..."
cp "$SCRIPT_DIR/widget_compact.html" "$WORK_DIR/index.html"

echo "▶ Initialising git and pushing..."
cd "$WORK_DIR"
git init -q
git config user.email "deploy@shift4.com"
git config user.name "Shift4 Deploy"
git checkout -b main
git add index.html
git commit -q -m "Deploy Shift4 support chatbot prototype"
git remote add origin "https://$GH_USER:$GH_TOKEN@github.com/$GH_USER/$REPO_NAME.git"
git push -u origin main --force -q
echo "✓ Pushed to GitHub."

echo "▶ Enabling GitHub Pages (main branch / root)..."
PAGES_RESP=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Authorization: token $GH_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$GH_USER/$REPO_NAME/pages" \
  -d '{"source":{"branch":"main","path":"/"}}')
PAGES_CODE=$(echo "$PAGES_RESP" | tail -1)

if [[ "$PAGES_CODE" == "201" || "$PAGES_CODE" == "409" ]]; then
  echo "✓ GitHub Pages enabled."
else
  echo "⚠ Pages response code: $PAGES_CODE (may already be enabled or pending activation)"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Done! Your prototype will be live in ~30–60 seconds:"
echo "  https://$GH_USER.github.io/$REPO_NAME/"
echo "  Repo: https://github.com/$GH_USER/$REPO_NAME"
echo "═══════════════════════════════════════════════════════"
