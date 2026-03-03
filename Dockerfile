# -- Stage 1: Build the React Frontend --
FROM node:18-alpine AS build-frontend
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# -- Stage 2: Set up the Python Backend --
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for FAISS
RUN apt-get update && apt-get install -y 
    libgomp1 
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
# Copy built frontend from Stage 1
COPY --from=build-frontend /frontend/dist ./frontend/dist
# Copy pre-built index
COPY backend/faiss_index ./backend/faiss_index

# Set PYTHONPATH to the current directory
ENV PYTHONPATH=/app/backend

# Run the server
CMD ["python", "backend/app/main.py"]
