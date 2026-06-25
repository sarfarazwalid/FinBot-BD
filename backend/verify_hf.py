from app.retrieval.vector_store import EmbeddingModel, configure_huggingface_auth, get_hf_auth_status
import os

# 1. HF auth
print('=== HF Auth Status ===')
result = configure_huggingface_auth()
print(f'Authenticated: {result["authenticated"]}')
print(f'User: {result["user"]}')
print()

# 2. Embedding singleton
print('=== Embedding Singleton Verification ===')
info_before = EmbeddingModel.get_info()
print(f'Model loaded: {info_before["model_loaded"]}')

v1 = EmbeddingModel.embed('hello')
print(f'First call shape: {v1.shape}')

model_id_1 = id(EmbeddingModel._model)

v2 = EmbeddingModel.embed('world')
model_id_2 = id(EmbeddingModel._model)
print(f'Same model instance: {model_id_1 == model_id_2}')
print()

# 3. Dimension
print('=== Dimension Verification ===')
print(f'Expected: 1024, Got: {v1.shape[1]}')
print(f'Match: {v1.shape[1] == 1024}')
print()

# 4. Debug endpoint status
print('=== Debug Endpoint Status ===')
status = get_hf_auth_status()
print(f'Auth: {status}')
info = EmbeddingModel.get_info()
print(f'Embedding info: {info}')
print()

# 5. Cache paths
print('=== Cache Paths ===')
print(f'HF_HOME: {os.environ.get("HF_HOME", "not set")}')
print(f'TRANSFORMERS_CACHE: {os.environ.get("TRANSFORMERS_CACHE", "not set")}')
print(f'HF_TOKEN set: {"HF_TOKEN" in os.environ}')