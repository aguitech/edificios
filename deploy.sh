#!/bin/bash
# deploy.sh — build + commit + push
# Uso: ./deploy.sh edificio2 "mensaje del commit"

set -e

EDIFICIO=${1:-edificio1}
MSG=${2:-"update render ${EDIFICIO}"}

echo "🏗️  Construyendo $EDIFICIO..."
cd "edificios/$EDIFICIO"
/Applications/Blender.app/Contents/MacOS/Blender --background --python build.py
cd ../..

echo "📦 Git add..."
git add .

echo "💬 Commit: $MSG"
git -c user.name="Hector Aguilar" -c user.email="hector@aguitech.com" commit -m "$MSG" || echo "(nothing to commit)"

echo "🚀 Push a origin/main..."
git push origin main

echo "✅ Listo! https://github.com/aguitech/edificios"
