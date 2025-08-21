# Web Content Analyzer

This project is a sophisticated web application that scrapes and analyzes the content of any website. It uses a `requests`-based engine to extract text, metadata, and structural information, then leverages the Google Gemini API to perform a multi-faceted AI analysis, providing insights on sentiment, SEO, readability, and more.

## ✨ Features

- **Intelligent Content Extraction**: Goes beyond simple text scraping to extract metadata, document structure, and key phrases.
- **Multi-Faceted AI Analysis**: Performs comprehensive analysis including:
  - Content Summarization & Key Points
  - Sentiment & Tone Analysis (with reasoning)
  - Topic Identification
  - SEO Recommendations & Keyword Extraction
  - Readability & Accessibility Scoring
- **Batch Processing**: Analyze multiple URLs in a single run.
- **Rich Report Exporting**: Download analysis reports in JSON, transposed CSV, and professional PDF formats.
- **Analysis History**: A stateful UI that saves and displays past analysis reports.
- **Dockerized**: Fully containerized with Docker for easy, one-command setup and deployment.

## 🏛️ How the Code Works

The application is built with a decoupled frontend and backend.

#### Backend (`FastAPI`)
- **`main.py`**: The entry point for the FastAPI server.
- **`api/routes.py`**: Defines the API endpoints (`/analyze`, `/export/pdf`) and orchestrates the calls to the various services.
- **`services/scraping_service.py`**: Uses the `requests` library to fetch a webpage's HTML. It includes features like user-agent rotation and retry logic.
- **`processors/content_extractor.py`**: The core data extraction engine. It uses `BeautifulSoup` to parse HTML and performs advanced analysis to identify the main content, extract metadata, find key phrases, and determine the document's structure.
- **`services/analysis_service.py`**: The AI core. It constructs a detailed prompt with the extracted text and sends it to the Google Gemini API, parsing the structured JSON response.
- **`services/report_service.py`**: Generates professional PDF reports using the `fpdf2` library, including an embedded sentiment chart created with `matplotlib`.
- **`models/data_models.py`**: Contains all Pydantic models that define the structure and validation rules for API requests and responses.

#### Frontend (`Streamlit`)
- **`app.py`**: A multi-page application created using `st.tabs`. It manages user input, calls the backend API, and displays results.
  - **`st.session_state`**: Used to manage and persist the analysis history across user interactions.
  - **Batch Processing**: The UI accepts multiple URLs and loops through them, displaying a progress bar for the entire batch.
  - **Report Display**: Each report is displayed in a dashboard-like format using `st.metric`, columns, and charts.
  - **Export Logic**: Contains helper functions to convert the JSON data to a transposed CSV for download.

## 🛠️ How to Run the App

### Prerequisites
- Docker Desktop installed and running.
- A Google Gemini API key.

### Method 1: Docker (Recommended)
This is the easiest way to run the entire application.

1.  **Clone the Repository**:
    ```sh
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```
2.  **Create Environment File**: In the `backend/` directory, create a file named `.env` and add your API key:
    ```
    # backend/.env
    GOOGLE_API_KEY="your_secret_gemini_api_key_here"
    ```
3.  **Run with Docker Compose**: From the project's **root directory**, run:
    ```sh
    docker-compose up --build
    ```
4.  **Access the App**: Open your web browser and go to `http://localhost:8501`.

### Method 2: Local Development (Without Docker)
Run the backend and frontend in separate terminals.

1.  **Terminal 1: Run the Backend**
    ```sh
    cd path/to/backend
    pip install -r requirements.txt
    py -m uvicorn main:app --reload
    ```
2.  **Terminal 2: Run the Frontend**
    ```sh
    cd path/to/frontend
    pip install -r requirements.txt
    # Make sure the BACKEND_URL in app.py is set to http://127.0.0.1:8000
    streamlit run app.py
    ```
