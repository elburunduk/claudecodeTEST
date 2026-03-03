# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A single-file vanilla HTML/CSS/JS Tic Tac Toe game. No build tools, frameworks, or dependencies.

**File:** `tictactoe.html` — open directly in any browser to run.

## Workflow

After completing any work, commit and push changes to GitHub so no work is lost:

```bash
git add .
git commit -m "your message here"
git push
```

## Architecture

Everything lives in one file with three sections:

- **CSS** (`<style>`): Dark-themed UI using CSS Grid for the board, flexbox for layout. Color palette: `#1a1a2e` background, `#e94560` for X/red accents, `#a8dadc` for O/blue accents.
- **HTML** (`<body>`): Mode selector (2-player vs CPU), scoreboard, 3×3 board of `.cell` divs with `data-i` indices 0–8, restart button.
- **JS** (`<script>`): Game logic with no external dependencies.
  - `board[]` — 9-element array tracking `'X'`, `'O'`, or `''`
  - `minimax()` — unbeatable AI using minimax algorithm (Computer plays as O, maximizing; human plays as X, minimizing)
  - `handleClick()` — human move entry point; triggers `computerMove()` after 400ms delay in CPU mode
  - Score is tracked in `score = { X, O, D }` (session-only, no persistence)
