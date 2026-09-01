# Smart Kolhapur Guide

A React frontend and Flask backend for discovering Kolhapur destinations and finding nearby hotels.

## Features

- Search and filter Kolhapur destinations.
- Read destination history, timings, entry fees, and travel information.
- Rank hotels by distance, price, rating, and travel preference.
- Save destinations and hotels to favorites.
- Create academic demo bookings and view booking records.
- Open map directions for destinations and hotels.
- User signup, login, logout, and session persistence.

## Project Structure

```text
frontend/
  src/                 React application
  public/              Frontend public assets
  package.json         Node dependencies and scripts
  vite.config.js       Development proxy to Flask
backend/
  app.py               Flask application factory and server
  routes/              HTML and JSON routes
  services/            Data, recommendation, and notification logic
  *.json               Tourism, hotel, user, booking, and notification data
run.py                 Flask development launcher
requirements.txt       Python dependencies
```

## Requirements

- Python 3.10 or newer
- Node.js 18 or newer
- npm

## Installation

Create and activate a Python virtual environment from the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

Install frontend dependencies:

```powershell
cd frontend
npm install
cd ..
```

## Run Locally

Start Flask in the first terminal:

```powershell
py run.py
```

Start React in a second terminal:

```powershell
cd frontend
npm run dev
```

Open the React application at:

```text
http://localhost:5173
```

The Flask API runs at `http://127.0.0.1:5000`. Vite proxies `/api` and `/static` requests to Flask during development.

## Production Build

Build the React frontend:

```powershell
cd frontend
npm run build
```

The compiled frontend is generated in `frontend/dist`. It should be served by a web server or integrated into the Flask deployment configuration before production use.

## Main API Endpoints

```text
GET  /api/places
GET  /api/hotels
GET  /api/recommendations
GET  /api/auth/me
POST /api/auth/login
POST /api/auth/signup
POST /api/auth/logout
GET  /api/favorites
POST /api/favorites/toggle
GET  /api/bookings
POST /api/bookings/create
POST /api/bookings/cancel/<booking_id>
```

## Booking Note

Bookings are for academic demonstration only. No real payment is processed. The frontend labels the booking as a demo confirmation and the backend should not be used for real reservations without adding payment-provider verification, authorization checks, and production storage.

## Verification

Run the frontend production build:

```powershell
cd frontend
npm run build
```

Run a basic Flask API check:

```powershell
py -c "from backend.app import app; c=app.test_client(); print(c.get('/api/places').status_code, c.get('/api/hotels').status_code)"
```
