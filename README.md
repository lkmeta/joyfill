<div align="center">

<p align="center"> <img src="https://github.com/lkmeta/joyfill/blob/dev/app/static/joyfill.png" width="300px"></p>

<hr class="custom-line">

</div>

<div align="center">
  <p>
    <img src="https://img.shields.io/badge/NLP-BERT-1f425f.svg" alt="BERT">
    <img src="https://img.shields.io/badge/NLP-DistilBERT-1f425f.svg" alt="DistilBERT">
    <img src="https://img.shields.io/badge/FastAPI-1f425f.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/Python_3.10-1f425f.svg" alt="Python">
    <img src="https://img.shields.io/badge/Docker-1f425f.svg" alt="Docker">
  </p>
</div>


## Table of Contents

- [About](#about)
- [Features](#features)
- [Models Used](#models-used)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Monitoring](#monitoring)
- [Authentication](#authentication)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [License](#license)

## About

JoyFill is a python web application designed to enhance sentences by providing positive suggestions using advanced NLP models. The application includes features like user authentication, containerized deployment with Docker, and is scalable with Kubernetes.

## Features

- **Sentence Enhancement**: Enter a sentence with a `<blank>` placeholder, and JoyFill will provide positive suggestions to fill the blank using an NLP model.
- **User Authentication**: Secure access with username and password.
- **Scalability**: Docker support for containerized deployment.
- **Load Testing**: Automated load testing with Locust to ensure performance under heavy load.

## Models Used

- **[BERT](https://huggingface.co/bert-base-uncased)** (Bidirectional Encoder Representations from Transformers): Used for generating fill-in-the-blank suggestions.
- **[DistilBERT](https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english)**: Used for sentiment analysis to filter out negative suggestions.


## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.10+
- Docker (containerized deployment)

**Note:**
Kubernetes and Locust are used for local testing and are not required to run the application in a Docker environment.

## Installation

### Clone the Repository

```bash
git clone https://github.com/lkmeta/joyfill.git
cd joyfill
```

### Docker Setup
- Build the Docker image:

```bash
docker build -t joyfill-app .
```
- Run the Docker container:

```bash
docker run -d -p 5000:5000 joyfill-app
```

### Accessing the Application
After starting the application, you can access it at:

```bash
http://localhost:5000
```

## Monitoring

To monitor and view the logs of your running Docker container:

1. Use the following command to list all running Docker containers:

   ```bash
   docker ps
   ```

2. To view the live logs of a specific container, use:

    ```bash
    docker logs -f <container_id_or_name>
    ```
Replace `<container_id_or_name>` with the actual container ID or name obtained from the previous command.

## Authentication
The current authentication mechanism follows OAuth2 standards. However, for testing and this phase of development, you can use the following credentials:

- Username: `testuser`
- Password: `testpassword`



## Usage

1. After completing the installation, open your web browser and navigate to `http://localhost:5000` to access JoyFill.
2. Log in with the credentials: `testuser` (username) and `testpassword` (password).
3. Enter a sentence with `<blank>` where you want suggestions, or click "Add Blank."
4. Suggestions are generated as you type, but ensure `<blank>` is included in the input.
5. Click "Refresh" to manually update the suggestions.
6. Click a suggestion to replace the `<blank>` with the chosen word.
7. Click "Clear" to reset the sentence.

**Note:** Only 5 suggestions are shown at a time to keep the UI clean.


## API Documentation

JoyFill is built using FastAPI, which automatically generates interactive API documentation.  
Once the application is running, you can access the API documentation at:


```bash
http://localhost:5000/docs
```

## Testing

To perform load testing and benchmark the performance of the JoyFill application, Locust can be used.   
The `locustfile.py` is located inside the `tests` directory.

### Steps to Run Locust Tests

1. **Install Locust**: If you don't have Locust installed, you can install it using pip:
    ```bash
    pip install locust
    ```

2. **Navigate to the Tests Directory**: 
    ```bash
    cd tests
    ```

3. **Run Locust**: Start Locust by running:
    ```bash
    locust -f locustfile.py
    ```

4. **Open Locust Web Interface**: Open your web browser and go to `http://localhost:8089`.

5. **Start the Test**: Fill in the required fields (like the number of users) and set the Host to `http://localhost:5000` to begin testing the JoyFill application.


### Steps to Deploy on Kubernetes

1. **Ensure Docker Image is Available**: Make sure that the Docker image of the application is available either locally or pushed to a Docker registry.

2. **Apply Kubernetes Deployment**:
    ```bash
    kubectl apply -f k8s/deployment.yaml
    ```

3. **Apply Kubernetes Service**:
    ```bash
    kubectl apply -f k8s/service.yaml
    ```

4. **Verify Deployment**: Check the status of your deployment and services:
    ```bash
    kubectl get deployments
    kubectl get services
    ```

5. **Access the Application**:
    - Since the `service.yaml` file defines a `NodePort` service type, you can access the application via the node's IP address and the specified node port (30001 in this case).
    - If you are running Kubernetes locally (e.g., with Docker Desktop or Minikube), you can typically access the application using `http://localhost:30001`.

6. **Monitor with Kubernetes Dashboard or Lens**: You can use tools like Kubernetes Dashboard or Lens to monitor the deployment, pods, and logs.


## License
This project is licensed under the MIT License.
