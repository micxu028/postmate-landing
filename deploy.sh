#!/bin/bash
echo "=== PostMate Landing Page Deploy ==="
echo ""

# Install wrangler if needed
if ! command -v wrangler &>/dev/null; then
    echo "Installing wrangler..."
    npm install -g wrangler
fi

# Login to Cloudflare
echo "Please login to Cloudflare:"
npx wrangler login

# Deploy
echo ""
echo "Deploying to Cloudflare Pages..."
npx wrangler pages deploy . --project-name postmate

echo ""
echo "Done! Then set the custom domain in Cloudflare Dashboard:"
echo "  postmate.net → Workers & Pages → postmate → Custom domains → Add postmate.net"
