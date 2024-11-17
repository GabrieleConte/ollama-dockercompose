#!/bin/bash

# Exit with status 1 if the command fails
ollama show $EMBEDDING_MODEL_NAME && ollama show $MODEL_NAME