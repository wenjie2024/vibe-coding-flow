from typing import Dict, Type, List
from .adapter_interface import BaseAdapter

class AdapterRegistry:
    """
    Registry for IDE adapters.
    Allows decoupling adapter implementation from the CLI.
    """
    _registry: Dict[str, Type[BaseAdapter]] = {}

    @classmethod
    def register(cls, name: str):
        """
        Decorator to register an adapter class.
        Usage: @AdapterRegistry.register("cursor")
        """
        def decorator(adapter_cls: Type[BaseAdapter]):
            cls._registry[name] = adapter_cls
            return adapter_cls
        return decorator

    @classmethod
    def get(cls, name: str) -> BaseAdapter:
        """
        Get an instantiated adapter by name.
        """
        adapter_cls = cls._registry.get(name)
        if not adapter_cls:
            raise ValueError(f"Unknown IDE adapter: {name}. Available: {list(cls._registry.keys())}")
        return adapter_cls()

    @classmethod
    def available_adapters(cls) -> List[str]:
        return list(cls._registry.keys())
