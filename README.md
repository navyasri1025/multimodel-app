# MultiModel AI Comparison App

A Streamlit application that compares responses from multiple AI models using a single prompt. It allows users to evaluate model outputs, response times, and token usage through a simple interface.

## Features

- Compare multiple AI models simultaneously
- Single prompt for all selected models
- Response latency tracking
- Token usage display
- Clean and interactive Streamlit UI
- Secure API key management using `.env`

## Tech Stack

- Python
- Streamlit
- OpenRouter API
- Requests

## Project Structure

```
multimodel-app/
├── .streamlit/
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── spec.md
└── .gitignore
```

## Installation

```bash
git clone https://github.com/navyasri1025/multimodel-app.git
cd multimodel-app
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
```

Run the application:

```bash
streamlit run app.py
```

The app will be available at:

```
http://localhost:8501
```

## License

MIT License
