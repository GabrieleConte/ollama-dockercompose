# Ollama Docker Compose Setup

This project is a full functioning chatbot service using ollama server as internal service.
## Getting Started

### Prerequisites
Make sure you have the following prerequisites installed on your machine:

- Docker
- Docker Compose

#### GPU Support (Optional)

If you have a GPU and want to leverage its power within a Docker container, follow these steps to install the NVIDIA Container Toolkit:

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure NVIDIA Container Toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test GPU integration
docker run --gpus all nvidia/cuda:11.5.2-base-ubuntu20.04 nvidia-smi
```

### Configuration

1. Clone the Docker Compose repository:


2. Change to the project directory:

    ```bash
    cd ollama-docker
    ```
3. Create a secrets file named like this:
    .env.secrets (can be blank)

## Usage

Start Ollama and its dependencies using Docker Compose:

if gpu is configured
```bash
docker-compose -f docker-compose-ollama-gpu.yaml up -d
```

else
```bash
docker-compose up -d
```

### Model Installation

Change the model/embedding names inside .env.config 

### Explore Langchain/Llamaindex and Ollama

You can explore Langchain/Lamaindex integrations with Ollama within the project. A second container named **app** has been created for this purpose. Inside, you'll find some examples.

### Devcontainer and Virtual Environment

The **app** container serves as a devcontainer, allowing you to boot into it for experimentation. Additionally, the run.sh file contains code to set up a virtual environment if you prefer not to use Docker for your development environment.
if you have vs code and the `Remote Development´ extension simply opening this project from the root will make vscode ask you to reopen in container
## Stop and Cleanup

To stop the containers and remove the network:

```bash
docker-compose down
```

## License

This project is licensed under the [Royalty-Share Open-Source License (RSOSL)](LICENSE). Feel free to use, modify, and distribute it according to the terms of the license. Just give me a mention and some credit

## Contact

If you have any questions or concerns, please contact me at [gabryconte90@gmail.com](mailto:gabryconte90@gmail.com).