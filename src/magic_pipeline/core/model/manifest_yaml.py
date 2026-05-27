from dataclasses import dataclass, field
from typing import List

@dataclass
class LocalNetwork:
    """本地网络配置"""
    id: int
    protocol: str
    addr: str
    port: int
    
    def __post_init__(self):
        if not 1 <= self.port <= 65535:
            raise ValueError(f"端口 {self.port} 超出有效范围(1-65535)")

@dataclass
class Whitelist:
    """白名单配置"""
    domains: List[str]
    ips: List[str]
    dns: List[str]
    local: List[LocalNetwork]

@dataclass
class ManifestConfig:
    """manifest.yaml 配置"""
    whitelist: Whitelist