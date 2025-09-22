import hashlib
import time
from collections import OrderedDict
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar

from config.settings import get_config
from core.managers.base_manager import BaseManager

T = TypeVar("T")


class CacheEntry:

    def __init__(self, value: Any, ttl: Optional[float] = None):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = self.created_at

    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def access(self) -> Any:
        self.access_count += 1
        self.last_accessed = time.time()
        return self.value


class LRUCache:

    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None

        entry = self._cache[key]
        if entry.is_expired():
            del self._cache[key]
            return None

        self._cache.move_to_end(key)
        return entry.access()

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        if ttl is None:
            ttl = self.default_ttl

        if key in self._cache:
            self._cache[key] = CacheEntry(value, ttl)
            self._cache.move_to_end(key)
        else:
            self._cache[key] = CacheEntry(value, ttl)
            if len(self._cache) > self.max_size:
                self._cache.popitem(last=False)

    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        self._cache.clear()

    def cleanup_expired(self) -> int:
        expired_keys = []
        for key, entry in self._cache.items():
            if entry.is_expired():
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        total_accesses = sum(entry.access_count for entry in self._cache.values())
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "total_accesses": total_accesses,
            "hit_rate": (
                0.0 if total_accesses == 0 else len(self._cache) / total_accesses
            ),
        }


class CacheManager(BaseManager):

    def __init__(self):
        super().__init__("cache_manager")
        self._config = get_config("performance")
        self._caches: Dict[str, LRUCache] = {}
        self._enabled = self._config.get("cache_enabled", True)

    def _do_initialize(self) -> None:
        if not self._enabled:
            self.logger.info("Cache desabilitado na configuração")
            return

        self._caches["main"] = LRUCache(
            max_size=self._config.get("cache_size", 1000), default_ttl=3600
        )

        self._caches["resources"] = LRUCache(max_size=500, default_ttl=None)

        self._caches["calculations"] = LRUCache(max_size=200, default_ttl=1800)

        self.logger.info("Caches inicializados")

    def get_cache(self, cache_name: str = "main") -> Optional[LRUCache]:
        """Obtém um cache específico."""
        if not self._enabled:
            return None
        return self._caches.get(cache_name)

    def get(self, key: str, cache_name: str = "main") -> Optional[Any]:
        """Obtém valor de um cache."""
        cache = self.get_cache(cache_name)
        if cache is None:
            return None
        return cache.get(key)

    def set(
        self,
        key: str,
        value: Any,
        cache_name: str = "main",
        ttl: Optional[float] = None,
    ) -> None:
        """Define valor em um cache."""
        cache = self.get_cache(cache_name)
        if cache is not None:
            cache.set(key, value, ttl)

    def delete(self, key: str, cache_name: str = "main") -> bool:
        """Remove valor de um cache."""
        cache = self.get_cache(cache_name)
        if cache is not None:
            return cache.delete(key)
        return False

    def clear(self, cache_name: Optional[str] = None) -> None:
        """Limpa cache(s)."""
        if cache_name:
            cache = self.get_cache(cache_name)
            if cache is not None:
                cache.clear()
        else:
            for cache in self._caches.values():
                cache.clear()

    def cleanup_expired(self) -> Dict[str, int]:
        results = {}
        for name, cache in self._caches.items():
            results[name] = cache.cleanup_expired()
        return results

    def get_stats(self) -> Dict[str, Any]:
        stats = super().get_stats()
        if not self._enabled:
            stats["enabled"] = False
            return stats

        stats["enabled"] = True
        stats["caches"] = {}
        for name, cache in self._caches.items():
            stats["caches"][name] = cache.get_stats()

        return stats

    def _generate_cache_key(self, *args, **kwargs) -> str:
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()


_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    if not _cache_manager.is_initialized():
        _cache_manager.initialize()
    return _cache_manager


def cached(
    cache_name: str = "main",
    ttl: Optional[float] = None,
    key_func: Optional[Callable] = None,
):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            manager = get_cache_manager()
            if not manager._enabled:
                return func(*args, **kwargs)

            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = (
                    f"{func.__name__}:{manager._generate_cache_key(*args, **kwargs)}"
                )

            cached_result = manager.get(cache_key, cache_name)
            if cached_result is not None:
                return cached_result

            result = func(*args, **kwargs)
            manager.set(cache_key, result, cache_name, ttl)
            return result

        return wrapper

    return decorator


def cache_resource(resource_name: str, loader: Callable[[], T]) -> T:
    manager = get_cache_manager()
    cached_resource = manager.get(resource_name, "resources")

    if cached_resource is None:
        cached_resource = loader()
        manager.set(resource_name, cached_resource, "resources")

    return cached_resource
