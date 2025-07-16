# GENZOIC ASSIGNMENT

## Built with:

- **React**
- **JavaScript**
- **Python**
- **Vite**

## Overview

This repository contains Market-Pulse, a FastAPI+React microservice. One thing which I added to make it unique is In-Memory TTL cache (10 min) to avoid redundant API calls. What it does is if a user has already searched for a particular ticker, it will save the data in-memory for 10 mins so when another user searches for the same ticker it will just not use one more API call hence saving API call cost. Used CORS for frontend and Backend Integration.

## What it Does?

1. **Accepts a Stock Ticker** (from the React frontend)

2. **Fetches:**

   - Last 5 trading days price return to compute a momentum score (Alpha Vantage)
   - Last 5 news headlines

3. **Send the data to LLM (Gemini)**

   - It decides whether the data is bullish/bearish/neutral
   - Generate a short, structured explanation using momentum and news context

4. **Return a JSON response**
   - It is managed by displaying using React-JSON library

## Frontend:

- Simple Chat-like UI
- Displays LLM result
- Expandable structured JSON viewer for full response

## Project Structure

```
/backend       # FastAPI service
/frontend      # React app (Vite or CRA)
README.md      # Project overview, setup, API spec
```

## Getting Started

### Prerequisites

- Node.js
- Python 3.x
- pip

### Installation

Build Genzoic-Assignment from the source and Install dependencies:

#### 1. Git Clone repository:

```bash
git clone https://github.com/Uzair-Tajmat/Genzzoic-Assignment
```

#### 2. Navigate to project Directory

```bash
cd Genzoic-Assignment
```

#### 3. Install the Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Starting Frontend

```bash
cd frontend
npm i
npm run dev
```

#### 5. Starting Backend

Open another terminal when you are in root directory:

```bash
cd backend
uvicorn main:app --reload
```

## Future Scope:

1. Add unit tests for momentum scoring and LLM prompt generation
2. Optimize LLM prompt for even cleaner, markdown-free JSON outputs
3. Polish Frontend with Recharts for momentum sparkline graphs
