# ☁️ Serverless RAG Document Parser on AWS

A containerized Retrieval Augmented Generation (RAG) application deployed on AWS App Runner.

# 📖 Project Overview

This project is a serverless RAG application that allows users to upload PDF documents and interact with them using natural language. It leverages Streamlit for the frontend, LangChain for the orchestration, and Hugging Face for the LLM inference.

The application is fully containerized using Docker and deployed to AWS App Runner, demonstrating a modern, cloud-native workflow.

# ✨ Features

📄 PDF Ingestion: Upload and process PDF documents instantly.

💬 Context-Aware Chat: Ask questions about the specific content of your uploaded document.

🧠 Free Tier AI: Uses the Mistral-7B-Instruct model via Hugging Face's free inference API.

⚡ Serverless Deployment: auto-scaling architecture using AWS App Runner.

🐳 Dockerized: Consistent environment across development and production.

# 🏗 Architecture

Frontend: Streamlit (Python)

Container Runtime: Docker

Vector Store: FAISS (In-memory vector search)

Embeddings: all-MiniLM-L6-v2 (Runs locally on CPU)

LLM: Mistral-7B (External API via Hugging Face)

Cloud Hosting: AWS App Runner pulling from Amazon ECR

# 🛠 Tech Stack

Language: Python 3.9

Frameworks: Streamlit, LangChain

AI/ML: Hugging Face Hub, FAISS, Sentence Transformers

DevOps: Docker, AWS ECR, AWS App Runner

# 🚀 Getting Started

## Prerequisites

Docker Desktop installed

Python 3.9+

An AWS Account (for deployment)

A free Hugging Face Account

## Local Installation

### 1. Clone the repository:

        git clone [https://github.com/s2donald/rag-document-assistant.git](https://github.com/s2donald/rag-document-assistant.git)
        
        cd rag-document-assistant


### 2. Install dependencies:

    pip install -r requirements.txt


### 3. Run the app:

    streamlit run app.py


# ☁️ Deployment Guide (AWS)

This project is designed to be deployed using AWS App Runner for a fully managed container experience.

### Step 1: Create an ECR Repository

Create a place to store your Docker image in AWS.

    aws ecr create-repository --repository-name rag-document-assistant --region us-east-1


### Step 2: Build & Push Image

    Login to ECR and push your Docker image.

    # Login (Replace 123456789012 with your AWS Account ID)
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

    # Build
    docker build -t rag-document-assistant .

    # Tag & Push
    docker tag rag-document-assistant:latest [123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-document-assistant:latest](https://123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-document-assistant:latest)
    docker push [123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-document-assistant:latest](https://123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-document-assistant:latest)


### Step 3: Configure App Runner

1. Go to the AWS Console -> App Runner.

2. Create a new service.

3. Select Container Registry -> Amazon ECR.

4. Select your image (rag-document-assistant).

5. In configuration settings, set the port to 8501.

6. Deploy!

# 🔑 Configuration

Once the app is running (locally or on AWS), you will need to input your Hugging Face Access Token in the sidebar.

1. Go to Hugging Face Settings -> Access Tokens.

2. Create a "Read" token.

3. Paste it into the app to start parsing.