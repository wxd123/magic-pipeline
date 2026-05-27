# magic_pipeline/core/scope/scope_protocol.py
from typing import Protocol, Any, Optional, TypeVar, runtime_checkable


T = TypeVar('T')

@runtime_checkable
class ScopeProtocol(Protocol):
    """Scope接口协议 - 供外部模块依赖"""
    
    @property
    def name(self) -> str:
        """作用域名称"""
        ...
    
    def set(self, key: str, value: Any) -> None:
        """设置资源"""
        ...
    
    def get(self, key: str, expected_type: type[T]) -> Optional[T]:
        """获取资源（带类型检查）"""
        ...
    
    def get_llm(self) -> Optional[Any]:
        """获取LLM实例"""
        ...

