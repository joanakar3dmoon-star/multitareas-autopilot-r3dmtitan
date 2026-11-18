"""Cerebro común: selección de proveedor sin incrustar secretos ni ejecutar acciones."""
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class ProviderConfig:
    name: str
    model: str | None
    endpoint: str | None
    api_key_env: str | None

PROVIDERS = {
    "openai": ("OPENAI_MODEL", "OPENAI_BASE_URL", "OPENAI_API_KEY"),
    "xai": ("XAI_MODEL", "XAI_BASE_URL", "XAI_API_KEY"),
    "ollama": ("OLLAMA_MODEL", "OLLAMA_BASE_URL", None),
    "pollinations": ("POLLINATIONS_MODEL", "POLLINATIONS_BASE_URL", "POLLINATIONS_API_KEY"),
}

def provider_config(name: str | None = None) -> ProviderConfig:
    selected = (name or os.getenv("AI_PROVIDER", "ollama")).strip().lower()
    if selected not in PROVIDERS:
        raise ValueError(f"Unsupported AI provider: {selected}")
    model_env, endpoint_env, key_env = PROVIDERS[selected]
    return ProviderConfig(selected, os.getenv(model_env), os.getenv(endpoint_env), key_env)

# Este módulo solo resuelve configuración. La llamada HTTP se implementará
# en adaptadores con pruebas, timeouts, límites de coste y política de datos.
