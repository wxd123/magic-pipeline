
# magic_pipeline/core/parser/base_parser.py


from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar
from magic_pipeline.context import ParserContext


# 定义泛型变量
ParserType = TypeVar('ParseType')

from typing import List, Tuple

class BaseParser(Generic[ParserType]):
    @abstractmethod
    def parse(self, config: Dict[str, Any], context: ParserContext) -> ParserType:
        """解析配置字典为 IR"""
        pass
    
    @abstractmethod
    def validate(self, ir: ParserType) -> Tuple[bool, List[str]]:
        """
        验证 IR 有效性
        
        Args:
            ir: 解析后的 IR 节点
        
        Returns:
            Tuple[bool, List[str]]: 
                - bool: 验证是否通过（True=有效，False=无效）
                - List[str]: 错误信息列表（验证通过时为空列表）
        """
        pass