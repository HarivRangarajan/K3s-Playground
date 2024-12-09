FROM python:3.9-slim

WORKDIR /app

# Install required packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code and model
COPY model.py .
COPY scaling_agent.py .
COPY linear_model.pkl /app/model/

CMD ["python", "scaling_agent.py"] 