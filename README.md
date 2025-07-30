# whisper-prod

> 🗣️ Self-hosted Whisper Speech-to-Text MVP  
> Scalable, containerized, and production-ready transcription service.

---

## 🧠 Project Overview

This project is a technical MVP that self-hosts the open-source Whisper model to provide an internal, cost-effective, and scalable speech-to-text API for the Sales Performance team.  
It was designed to transcribe audio from 100 sales agents, with headroom to scale to 1000 users.

---

## ✅ Objectives

- Replace a costly third-party transcription service with an in-house solution.
- Provide a production-grade API for transcription tasks.
- Ensure the stack is containerized, monitored, and deployable on AWS via Terraform.
- Demonstrate a scalable inference backend based on open models.

---

## 🚧 Challenges Addressed

| Challenge              | Solution                                                                 |
|------------------------|--------------------------------------------------------------------------|
| **Scalability**        | Kubernetes-native deployment; async batch processing                     |
| **Inference latency**  | Optimized Python code with dynamic batching and concurrency              |
| **Portability**        | Containerized with Docker, reproducible builds                           |
| **Infra automation**   | Infrastructure-as-code with Terraform (AWS-ready)                        |
| **Monitoring**         | Prometheus & Grafana integration with custom metrics                     |
| **Integration**        | Clear REST API contract for internal software engineers                  |

---

## 🏗️ Architecture Overview

### 🔁 High-Level Design

```text
User Audio File
      ↓
LoadBalancer (Kubernetes)
      ↓
FastAPI Whisper Server (/v1/audio/transcriptions[_batch])
      ↓
Whisper Inference Engine (CPU-based or GPU-based)
      ↓
Text Output
````

### 🔧 Components

* **Inference Service**

  * FastAPI backend
  * `openai/whisper` model (tiny by default, configurable)
  * Endpoints:

    * `/v1/audio/transcriptions` (single file)
    * `/v1/audio/transcriptions_batch` (multiple files)

* **Containerization**

  * Lightweight multi-stage Docker build
  * Python 3.11-slim + Uvicorn server

* **Infrastructure (AWS-ready)**

  * Terraform provisioning of:

    * EKS Cluster ?
    * MetalLB ?
  * Helm-based app deployment

* **Monitoring**

  * Prometheus exporter integrated in FastAPI  - TODO
  * Grafana dashboards - TODO
  * Custom metrics: request latency, memory usage, errors - TODO

---

## 🧪 Scalable Inference Logic

### Key Features

* **Dynamic Batching**: Multiple audio files can be processed together to increase CPU/GPU throughput.
* **Async I/O**: Python's `asyncio` to prevent blocking calls during file upload and transcription.
* **Resource Constraints**: Kubernetes CPU/memory limits & health probes enabled.

### Code Snapshot

```python
@app.post("/v1/audio/transcriptions")
async def transcribe(file: UploadFile):
    audio = await file.read()
    audio_tensor = audio_to_tensor(audio)
    result = model.transcribe(audio_tensor)
    return {"text": result["text"]}
```

---

## 📦 Containerization

### Dockerfile (multi-stage)

```Dockerfile
FROM python:3.11-slim AS base

# Dependencies
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

---

## ☁️ Infrastructure Automation

### Terraform Stack (AWS-ready)

* EKS Cluster provisioning (not implemented in MVP, but scoped)
* MetalLB used for testing on K3s (my personal VPS)
* Helm chart for deploying FastAPI container and exposing ingress

### Notes

> 🧪 MVP deployed and tested on K3s cluster (1 VPS) with MetalLB.
> Final deployment should use AWS EKS + ALB + HorizontalPodAutoscaler.

---

## 🚀 Deployment Process

```bash
# 1. Build and push Docker image
docker build -t <registry>/whisper-prod:latest .
docker push <registry>/whisper-prod:latest

# 2. Deploy infrastructure (locally or with Terraform)
terraform apply  # (for infra provisioning)

# 3. Deploy application
helm upgrade --install whisper-prod ./helm-chart --namespace whisper-prod
```

---

## 📈 Monitoring

### Tools

* **Prometheus**: via `prometheus-fastapi-instrumentator`
* **Grafana**: Pre-built dashboard JSON provided
* **Custom Metrics**:

  * `/metrics` endpoint exposed TODO
  * Inference duration
  * Error rates
  * Memory usage

---

## 🧱 Repository Structure

```
.
├── app/                      # FastAPI app
├── Dockerfile
├── helm-chart/
│   └── templates/
├── terraform/                # Infra-as-code (EKS planned)
├── requirements.txt
└── README.md
```

---

## 🛑 Current Limitations

| Area            | Limitation                                                     |
| --------------- | -------------------------------------------------------------- |
| **Scalability** | Only tested on single-node K3s cluster                         |
| **Latency**     | CPU inference may lag on long files or large batches           |
| **Security**    | No authentication, no rate-limiting yet                        |
| **GPU Support** | Not yet implemented; can reduce latency and cost significantly |

---

## 🔄 Potential Improvements

* ✅ **GPU Acceleration** (CUDA-based Whisper backend - vllm ?)
* ✅ **Auto-scaling** 
* ✅ **Authentication Layer** (OAuth or API keys)
* ✅ **Advanced Monitoring & Alerting**
* ✅ **CI/CD Integration** (GitHub Actions + Helm deploy)

---

## ⏱️ Time Spent

| Task                | Hours     |
| ------------------- | --------- |
| Research & Planning | 2         |
| Code Implementation | 2         |
| Infra Setup         | 1         |
| Documentation       | 30min     |
| **Total**           | **5h30m** |

---

## 🧭 Next Steps

* [ ] Benchmark GPU-backed inference on AWS EC2
* [ ] Deploy to AWS EKS via Terraform for full-scale usage
* [ ] Discuss metrics and monitoring with team
