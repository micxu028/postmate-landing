#!/bin/bash
set -e
echo "=== PostMate Landing Page Deploy ==="

if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "Error: CLOUDFLARE_API_TOKEN not set"
    echo "Usage: CLOUDFLARE_API_TOKEN=your_token ./deploy.sh"
    exit 1
fi

export CLOUDFLARE_API_TOKEN
npx wrangler pages deploy . --project-name postmate --branch main

echo ""
echo "✅ Done! https://postmate.net"
