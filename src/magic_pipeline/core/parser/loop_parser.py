# magic_pipeline/core/parser/loop_parser.py

from typing import Any, Dict, List, Tuple
from uuid import uuid4

from magic_pipeline.context import ParserContext
from magic_pipeline.core.parser.base_parser import BaseParser
from magic_pipeline.core.step import LoopStep
from magic_pipeline.core.command import StepCommand


class LoopParser(BaseParser[LoopStep]):
    """
    循环解析器 - 解析循环步骤配置为 LoopStep IR
    
    负责将 YAML/JSON 中的循环配置解析为 LoopStep 对象。
    处理 loop 结构解析、模型列表提取、内部步骤递归解析等。
    
    支持的配置格式:
        - 标准格式: 
            {
                "loop": {
                    "models": ["qwen_0.5b", "qwen_1.5b"],
                    "steps": [
                        {"command": "java:generate"},
                        {"command": "java:report"}
                    ]
                }
            }
        
        - 带ID格式:
            {
                "id": "my_loop",
                "loop": {
                    "models": ["qwen_0.5b", "qwen_1.5b"],
                    "steps": [...]
                }
            }
        
        - 带依赖格式:
            {
                "loop": {...},
                "depends_on": ["previous_step"]
            }
    
    示例:
        >>> parser = LoopParser()
        >>> config = {
        ...     "loop": {
        ...         "models": ["qwen_0.5b", "qwen_1.5b"],
        ...         "steps": [
        ...             {"command": "java:generate"},
        ...             {"command": "java:qc"}
        ...         ]
        ...     }
        ... }
        >>> loop = parser.parse(config, context)
        >>> print(loop.models)
        ['qwen_0.5b', 'qwen_1.5b']
        >>> print(len(loop.steps))
        2
    """
    
    def parse(self, config: Dict[str, Any], context: ParserContext) -> LoopStep:
        """
        解析循环配置为 LoopStep
        
        解析流程：
            1. 提取 loop 配置块
            2. 获取或生成步骤 ID
            3. 提取模型列表
            4. 提取依赖关系
            5. 递归解析内部步骤
            6. 创建 LoopStep 实例
        
        Args:
            config: 循环配置字典，支持以下格式：
                    - 标准: {"loop": {"models": [...], "steps": [...]}}
                    - 带ID: {"id": "my_loop", "loop": {...}}
                    - 带依赖: {"loop": {...}, "depends_on": ["step1"]}
            context: 解析上下文，用于获取子解析器、生成 ID、缓存等
        
        Returns:
            LoopStep: 解析后的循环步骤对象
        
        Raises:
            ValueError: 当配置格式错误、缺少必需字段时抛出
        """
        # 提取 loop 配置块
        loop_config = config.get("loop")
        if not loop_config:
            raise ValueError("LoopParser requires 'loop' field in config")
        
        # 确保 loop_config 是字典类型
        if not isinstance(loop_config, dict):
            raise ValueError(f"Invalid loop config type: {type(loop_config)}")
        
        # 获取步骤 ID，如果没有则生成
        step_id = config.get("id")
        if not step_id:
            step_id = context.generate_step_id() if hasattr(context, 'generate_step_id') else str(uuid4())
        
        # 获取模型列表
        models = loop_config.get("models", [])
        if not models:
            raise ValueError(f"LoopStep {step_id}: 'models' field is required and cannot be empty")
        
        if not isinstance(models, list):
            raise ValueError(f"LoopStep {step_id}: 'models' must be a list")
        
        # 获取依赖关系
        depends_on = config.get("depends_on", [])
        if depends_on and not isinstance(depends_on, list):
            raise ValueError(f"LoopStep {step_id}: 'depends_on' must be a list")
        
        # 获取内部步骤配置
        steps_config = loop_config.get("steps", [])
        if not steps_config:
            raise ValueError(f"LoopStep {step_id}: 'steps' field is required and cannot be empty")
        
        if not isinstance(steps_config, list):
            raise ValueError(f"LoopStep {step_id}: 'steps' must be a list")
        
        # 递归解析内部步骤
        steps = self._parse_inner_steps(steps_config, context)
        
        return LoopStep(
            step_id=step_id,
            models=models,
            steps=steps,
            depends_on=depends_on
        )
    
    def _parse_inner_steps(
        self, 
        steps_config: List[Dict[str, Any]], 
        context: ParserContext
    ) -> List[Any]:
        """
        递归解析循环体内的步骤
        
        根据每个步骤配置的类型，从上下文获取对应的解析器进行处理。
        支持嵌套循环（LoopStep 内部可以继续包含 LoopStep）。
        
        Args:
            steps_config: 步骤配置列表
            context: 解析上下文，用于获取子解析器
        
        Returns:
            解析后的步骤对象列表（StepCommand 或 LoopStep）
        
        Raises:
            ValueError: 当步骤类型未知时抛出
        """
        steps = []
        
        for step_config in steps_config:
            # 检测步骤类型
            node_type = self._detect_node_type(step_config)
            
            # 从上下文获取对应的解析器
            parser = context.get_parser(node_type)
            if not parser:
                raise ValueError(f"Unknown node type '{node_type}' for config: {step_config}")
            
            # 递归解析
            step = parser.parse(step_config, context)
            steps.append(step)
        
        return steps
    
    def _detect_node_type(self, config: Dict[str, Any]) -> str:
        """
        检测步骤配置的节点类型
        
        根据配置字典中的字段判断是命令节点还是循环节点。
        
        Args:
            config: 步骤配置字典
        
        Returns:
            节点类型字符串:
                - "command": 命令节点（包含 command 字段）
                - "loop": 循环节点（包含 loop 字段）
                - "unknown": 未知类型
        """
        if "command" in config:
            return "command"
        if "loop" in config:
            return "loop"
        return "unknown"
    
    def validate(self, ir: LoopStep) -> Tuple[bool, List[str]]:
        """
        验证 LoopStep 的有效性
        
        检查必需的字段是否存在、格式是否正确。
        同时递归验证内部步骤的有效性。
        
        Args:
            ir: 待验证的 LoopStep 实例
        
        Returns:
            Tuple[bool, List[str]]: 
                - bool: 是否验证通过
                - List[str]: 错误信息列表（验证通过时为空）
        """
        errors = []
        
        # 验证 step_id
        if not ir.step_id:
            errors.append("LoopStep: step_id is empty")
        
        # 验证 models
        if not ir.models:
            errors.append(f"LoopStep {ir.step_id}: models list is empty")
        
        if ir.models and not isinstance(ir.models, list):
            errors.append(f"LoopStep {ir.step_id}: models must be a list")
        
        # 验证 depends_on
        if ir.depends_on and not isinstance(ir.depends_on, list):
            errors.append(f"LoopStep {ir.step_id}: depends_on must be a list")
        
        # 验证 steps
        if not ir.steps:
            errors.append(f"LoopStep {ir.step_id}: steps list is empty")
        
        # 递归验证内部步骤
        for idx, step in enumerate(ir.steps):
            if hasattr(step, 'validate'):
                # 如果步骤对象有 validate 方法，调用它
                is_valid, step_errors = step.validate()
                if not is_valid:
                    for err in step_errors:
                        errors.append(f"LoopStep {ir.step_id}.steps[{idx}]: {err}")
            else:
                # 基本验证
                if hasattr(step, 'step_id') and not step.step_id:
                    errors.append(f"LoopStep {ir.step_id}.steps[{idx}]: step_id is empty")
                if hasattr(step, 'command') and not step.command:
                    errors.append(f"LoopStep {ir.step_id}.steps[{idx}]: command is empty")
        
        return len(errors) == 0, errors
    
    def get_node_type(self) -> str:
        """
        获取该解析器处理的节点类型标识
        
        Returns:
            节点类型字符串 "loop"
        """
        return "loop"