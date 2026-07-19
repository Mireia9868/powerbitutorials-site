#!/bin/bash
# ============================================================
# new-tutorial.sh — One-command scaffold for a new tutorial
# Usage: ./scripts/new-tutorial.sh <slug> <category> [difficulty]
# Example: ./scripts/new-tutorial.sh "dax-switch-function" dax Beginner
# ============================================================

set -e

# --- Args ---
SLUG="$1"
CATEGORY="$2"
DIFFICULTY="${3:-Beginner}"

if [ -z "$SLUG" ] || [ -z "$CATEGORY" ]; then
  echo "Usage: ./scripts/new-tutorial.sh <slug> <category> [difficulty]"
  echo ""
  echo "Categories:  dax | power-query | data-modeling | visualization | time-intelligence"
  echo "Difficulty:  Beginner | Intermediate | Advanced (default: Beginner)"
  echo ""
  echo "Example:"
  echo "  ./scripts/new-tutorial.sh dax-switch-function dax Intermediate"
  exit 1
fi

# --- Validate category ---
VALID_CATEGORIES="dax power-query data-modeling visualization time-intelligence"
if ! echo "$VALID_CATEGORIES" | grep -qw "$CATEGORY"; then
  echo "Error: Invalid category '$CATEGORY'"
  echo "Valid options: dax, power-query, data-modeling, visualization, time-intelligence"
  exit 1
fi

# --- Validate difficulty ---
VALID_DIFF="Beginner Intermediate Advanced"
if ! echo "$VALID_DIFF" | grep -qw "$DIFFICULTY"; then
  echo "Error: Invalid difficulty '$DIFFICULTY'"
  echo "Valid options: Beginner, Intermediate, Advanced"
  exit 1
fi

# --- Paths ---
TUTORIALS_DIR="$(cd "$(dirname "$0")/.." && pwd)/src/content/tutorials"
FILENAME="${SLUG}.md"
FILEPATH="${TUTORIALS_DIR}/${FILENAME}"

# --- Check if file already exists ---
if [ -f "$FILEPATH" ]; then
  echo "Error: File already exists: $FILEPATH"
  exit 1
fi

# --- Generate title from slug ---
TITLE=$(echo "$SLUG" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')

# --- Today's date ---
PUB_DATE=$(date +%Y-%m-%d)

# --- Create file ---
mkdir -p "$TUTORIALS_DIR"

cat > "$FILEPATH" << EOF
---
title: "${TITLE}"
description: "TODO: Write a compelling 150-160 character meta description that includes the primary keyword and a value proposition."
pubDate: ${PUB_DATE}
category: "${CATEGORY}"
difficulty: "${DIFFICULTY}"
tags: ["TODO-tag1", "TODO-tag2"]
author: "Power BI Tutorials Team"
---

## Introduction

TODO: Write 2-3 sentences explaining what this tutorial covers and why it matters.

## Prerequisites

TODO: List what the reader should already know or have set up.

## Main Content

TODO: Write your tutorial content here. Aim for 1200-1800 words.

### Subsection 1

TODO: Content...

### Subsection 2

TODO: Content...

## Common Mistakes

TODO: 2-3 common pitfalls and how to avoid them.

## Summary

TODO: Brief recap of what was learned.

## Next Steps

- [Related Tutorial 1](/tutorials/TODO)
- [Related Tutorial 2](/tutorials/TODO)
EOF

echo ""
echo "========================================"
echo "  Tutorial scaffold created!"
echo "========================================"
echo ""
echo "  File:   ${FILEPATH}"
echo "  Title:  ${TITLE}"
echo "  Date:   ${PUB_DATE}"
echo "  Cat:    ${CATEGORY}"
echo "  Level:  ${DIFFICULTY}"
echo ""
echo "  Next steps:"
echo "    1. Edit the file — replace TODO sections with content"
echo "    2. Build:  npm run build"
echo "    3. Deploy: git add . && git commit -m 'new: ${SLUG}' && git push"
echo ""
