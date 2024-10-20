# API Server
Fast Api setver to get car angle and confidence for the images

## Dependencies

- Python 3.7+
- FastAPI
- Ultralytics

## Installation

1. Clone this repository
2. Install the required dependencies
3. Run server

```bash
cd Project_2
pip install -r requirements.txt

## move to root directory to run server
cd ..

## run the server
uvicorn Project_2.main:app --host 0.0.0.0 --port 4560 --reload
```
