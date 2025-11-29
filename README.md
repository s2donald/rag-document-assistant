# ☁️ Serverless RAG Document Parser on AWS

A containerized Retrieval Augmented Generation (RAG) application deployed on AWS App Runner.

# 📖 Project Overview

This project is a serverless **RAG application** that allows users to upload PDF documents and interact with them using natural language. It leverages **Streamlit** for the frontend, **LangChain** for the orchestration, and **Hugging Face** (via the Featherless.ai provider) for the LLM inference.

The application is fully containerized using **Docker** and deployed to **AWS Fargate** (Serverless ECS), ensuring high availability and secure networking without managing EC2 instances.

# ✨ Features

* 📄 **PDF Ingestion**: Upload and process PDF documents instantly.

* 💬 **Context-Aware Chat**: Ask questions about the specific content of your uploaded document.

* 🧠 **Free Tier AI**: Uses the `Zephyr-7b-Beta` model via Hugging Face's free inference API.

* ⚡ **Serverless Deployment**: auto-scaling architecture using AWS App Runner.

* 🐳 **Dockerized**: Consistent environment across development and production.

# 🏗 Architecture

1. **Frontend**: Streamlit (Python)

2. **Container Runtime**: Docker

3. **Vector Store**: FAISS (In-memory vector search)

4. **Embeddings**: `all-MiniLM-L6-v2` (Runs locally on CPU)

5. **LLM**: `zephyr-7b-beta` (External API via Featherless AI)

6. **Cloud Hosting**: AWS Elastic Container Service (ECS) on Fargate

# 🧠 Why FAISS? (Vector Store)

I specifically chose **FAISS (Facebook AI Similarity Search)** for this project's retrieval layer.

* **What it does**: FAISS is a library that allows developers to quickly search for embeddings (vectors) of multimedia documents that are similar to each other.

* **How it works**: When a user uploads a PDF, the application converts the text into high-dimensional vectors. FAISS creates an efficient index of these vectors in RAM. When a question is asked, FAISS calculates the mathematical "distance" (similarity) between the question's vector and the document chunks to retrieve the most relevant answers in milliseconds.

* **Why I went with it**:

    * **In-Memory Speed**: FAISS runs entirely in RAM, making retrieval incredibly fast.

    * **Session-Based**: Since this app is designed for ephemeral sessions (upload a doc, chat, close tab), we do not need a persistent database like Pinecone or PostgreSQL.

    * **No Infrastructure**: It eliminates the need to provision and manage an external database server, keeping the architecture "serverless" and self-contained within the Docker container.

# 🛠 Tech Stack

Language: Python 3.9

Frameworks: Streamlit, LangChain

AI/ML: Hugging Face Hub, FAISS, Sentence Transformers

DevOps: Docker, AWS ECR, AWS ECS Fargate

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


### Step 2: Build & Push Image to Amazon ECR

    Login to ECR and push your Docker image.

    # Login (Replace 123456789012 with your AWS Account ID)
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

    # Build
    docker build --platform=linux/amd64 -t rag-document-assistant .

    # Tag & Push
    docker tag rag-document-assistant:latest [123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-document-assistant:latest](https://123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-document-assistant:latest)
    docker push [123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-document-assistant:latest](https://123456789012.dkr.ecr.us-east-1.amazonaws.com/rag-document-assistant:latest)


### Step 3: Configure AWS ECS Cluster

1. Navigate to **Amazon ECS > Clusters** 

2. Click **Create Cluster**.

3. Name: `rag-document-cluster`.

4. Infrastructure Select `Fargate Only`.

5. Click **Create**.

# Step 4: Create Task Definition

1. Go to Task Definitions > Create new Task Definition.

2. **Name**: `rag-task-def`.

3. **Launch** Type: AWS Fargate.

4. **OS/Architecture**: Linux / X86_64.

5. **CPU/Memory**: `.5 vCPU` / `1 GB` (or higher if needed).

6. **Container Details**:

    * **Name**: `rag-container`

    * **Image URI**: Select your ECR Image URI from Step 1.

    * **Container Port**: `8501` (Protocol TCP).

7. Click **Create**.

# Step 5: Run the Service

1. Go inside your `rag-cluster`.

2. Click **Create** under "Services".

3. **Compute Options**: Launch Type > Fargate.

4. **Task Definition**: Select `rag-task-def` (Latest revision).

5. **Service Name**: `rag-service`.

6. **Desired Tasks**: 1.

7. **Networking**:

    * **VPC**: Select default VPC.

    * **Subnets**: Select all available.

    * **Security Group**: Create a new group that allows **Custom TCP** on Port **8501** from source `0.0.0.0/0` (Anywhere).

    * **Public IP**: **TURN ON** (Required to access the app).

8. Click **Create Service**.

# Step 6: Access the App

1. Wait for the Task Status to change to `Running`.

2. Click on the **Task ID**.

3. Find the **Public IP** address under the Network section.

4. Open your browser to: `http://<PUBLIC-IP>:8501`

# 🔑 Configuration

Once the app is running (locally or on AWS), you will need to input your Hugging Face Access Token in the sidebar.

1. Go to Hugging Face Settings -> Access Tokens.

2. Create a "Read" token.

3. Paste it into the app to start parsing.