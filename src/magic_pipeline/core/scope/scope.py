# magic_pipeline/core/scope/scope.py
from typing import Any, Dict, Optional, TypeVar, cast
import time
from magic_pipeline.core.providers import LLMProvider, get_llm_manager

T = TypeVar('T')


class BaseScope:
    """作用域基类 - 只管理资源"""
    
    def __init__(self, name: str):
        self.name = name        
        self.resources: Dict[str, Any] = {}
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self._on_enter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._on_exit(exc_type, exc_val, exc_tb)
        elapsed = time.time() - self.start_time
        print(f"⏱️  {self.name} 耗时: {elapsed:.2f}s")
        return False
    
    def _on_enter(self):
        """子类可覆盖"""
        print(f"🔧 进入: {self.name}")
    
    def _on_exit(self, exc_type, exc_val, exc_tb):
        """子类可覆盖"""
        print(f"✅ 退出: {self.name}")
    
    def set(self, key: str, value: Any):
        """设置资源"""
        self.resources[key] = value
    
    def get(self, key: str, expected_type: type[T]) -> Optional[T]:
        """获取资源（带类型检查）"""
        resource = self.resources.get(key)
        if resource is None:
            return None
        if not isinstance(resource, expected_type):
            raise TypeError(f"资源 '{key}' 类型错误")
        return cast(T, resource)
    
    def get_llm(self)->Optional[T]:
        return self.get('llm')
    
    