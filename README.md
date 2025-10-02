# The Orbital Debris Tracker

A near real-time simulator that visualizes tracked space debris around Earth. This project uses public TLE data from Space-Track.org, propagates orbital trajectories, and renders them in a 3D browser environment using CesiumJS.

## Features

- **Backend API:** Fetches, caches, and processes orbital data using Python and FastAPI.
- **Orbital Propagation:** Uses the SGP4 model via the `skyfield` library to calculate debris positions.
- **Scheduled Data Updates:** Automatically fetches the latest debris catalog every 4 hours.
- **3D Visualization:** Renders the Earth and debris objects in real-time using CesiumJS.
- **Interactive UI:** Displays debris information (velocity, altitude) in a tooltip on hover.

## Tech Stack

- **Backend:** Python, FastAPI, Skyfield, APScheduler, Requests
- **Frontend:** HTML5, CSS3, JavaScript, CesiumJS
- **Data Source:** Space-Track.org API

## Setup and Installation

### Prerequisites

- Python 3.8+
- A free account on [Space-Track.org](https://www.space-track.org)

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd orbital-debris-tracker/backend
    ```
2.  **Create a Python virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create and configure your environment file:**
    -   Copy the contents of the provided `.env` template below into a new file named `.env`.
    -   Add your Space-Track.org username and password.

### Frontend Setup

The frontend is a simple static site and requires no build steps. You just need a local web server to serve the files to avoid CORS issues.

## How to Run the Application

1.  **Run the Backend Scheduler (First time & periodically):**
    -   Open a terminal in the `backend` directory.
    -   This script will fetch the initial data from Space-Track and save it to `cache/debris_data.json`. It's designed to be run periodically (e.g., via a cron job). For now, run it once manually to get the data.
    ```bash
    python scheduler.py
    ```

2.  **Start the Backend API Server:**
    -   In the same terminal (after the scheduler has run at least once):
    ```bash
    uvicorn main:app --reload
    ```
    -   The API will be available at `http://127.0.0.1:8000`.

3.  **Serve the Frontend:**
    -   Open a *new* terminal in the `frontend` directory.
    -   The easiest way to serve the files is with Python's built-in HTTP server.
    ```bash
    python -m http.server 8080
    ```
4.  **View the Application:**
    -   Open your web browser and navigate to `http://localhost:8080`.
