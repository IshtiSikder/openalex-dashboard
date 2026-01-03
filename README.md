# OpenAlex Research Dashboard

A Streamlit-based interactive dashboard for exploring and visualizing research data from OpenAlex, an open catalog of scholarly papers, authors, institutions, and more.

## Overview

This project provides a web-based dashboard to query and analyze academic research data using the OpenAlex API. Built with Streamlit and designed for deployment on Google Cloud Run.

## Features

- Interactive data exploration from OpenAlex
- Visualizations using Plotly
- Real-time data fetching via PyAlex
- Cloud-native deployment ready
- Containerized with Docker

## Tech Stack

- **Frontend/Backend**: Streamlit
- **Data Source**: OpenAlex API (via PyAlex)
- **Visualization**: Plotly
- **Data Processing**: Pandas
- **Deployment**: Google Cloud Run
- **CI/CD**: GitHub Actions

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/openalex-dashboard.git
cd openalex-dashboard
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## Docker Deployment

### Build the Docker image:
```bash
docker build -t openalex-dashboard .
```

### Run the container locally:
```bash
docker run -p 8080:8080 openalex-dashboard
```

Access at `http://localhost:8080`

## Google Cloud Run Deployment

### Prerequisites

- Google Cloud account with billing enabled
- gcloud CLI installed and authenticated
- Project created with Cloud Run API enabled

### Deploy to Cloud Run

1. Set your project:
```bash
gcloud config set project YOUR_PROJECT_ID
```

2. Build and submit to Cloud Build:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/openalex-dashboard
```

3. Deploy to Cloud Run:
```bash
gcloud run deploy openalex-dashboard \
  --image gcr.io/YOUR_PROJECT_ID/openalex-dashboard \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## CI/CD with GitHub Actions

This project includes a GitHub Actions workflow for automated deployment to Cloud Run. Configure the following secrets in your GitHub repository:

- `GCP_PROJECT_ID`: Your Google Cloud project ID
- `GCP_SA_KEY`: Service account key JSON (base64 encoded)

## Project Structure

```
openalex-dashboard/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── .dockerignore          # Docker build exclusions
├── .gitignore            # Git exclusions
├── README.md             # Project documentation
├── .github/
│   └── workflows/
│       └── deploy.yml    # GitHub Actions CI/CD
└── tests/
    └── test_app.py       # Application tests
```

## Usage

(Coming soon - details on how to use the dashboard)

## Testing

Run tests with pytest:
```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Acknowledgments

- [OpenAlex](https://openalex.org/) for providing open access to scholarly data
- [Streamlit](https://streamlit.io/) for the amazing framework
- [PyAlex](https://github.com/J535D165/pyalex) for the Python wrapper

## Contact

For questions or feedback, please open an issue on GitHub.

---

**Status**: 🚧 Under Development
