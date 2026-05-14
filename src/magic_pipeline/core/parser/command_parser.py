# magic_pipeline/core/parser/command_parser.py

from typing import Any, Dict, List, Tuple
from uuid import uuid4

from magic_pipeline.context import ParserContext
from magic_pipeline.core.parser.base_parser import BaseParser
from magic_pipeline.core.command import StepCommand


class CommandParser(BaseParser[StepCommand]):
    """
    命令解析器 - 解析命令步骤配置为 StepCommand IR
    
    负责将 YAML/JSON 中的命令配置解析为 StepCommand 对象。
    处理 command 字段的解析、参数提取、依赖关系映射等。
    
    支持的配置格式:
        - 简写格式: "java:clean"
        - 完整格式: {"command": "java:clean"}
        - 带参数格式: {"command": "java:generate", "params": {...}}
        - 带依赖格式: {"command": "java:generate", "depends_on": ["step1", "step2"]}
        - 带ID格式: {"id": "my_step", "command": "java:clean"}
    
    示例:
        >>> parser = CommandParser()
        >>> config = {"command": "java:generate", "params": {"model": "qwen_0.5b"}}
        >>> step = parser.parse(config, context)
        >>> print(step.command)
        'java:generate'
    """
    
    def parse(self, config: Dict[str, Any], context: ParserContext) -> StepCommand:
        """
        解析命令配置为 StepCommand
        
        Args:
            config: 命令配置字典，支持以下格式：
                    - 简写: "command": "java:clean"
                    - 标准: {"command": "java:clean"}
                    - 带参数: {"command": "java:generate", "params": {...}}
                    - 带依赖: {"command": "java:generate", "depends_on": ["step1"]}
                    - 带ID: {"id": "my_step", "command": "java:clean"}
            context: 解析上下文，用于生成步骤 ID
        
        Returns:
            StepCommand: 解析后的命令步骤对象
        
        Raises:
            ValueError: 当 config 不是字典或缺少 command 字段时抛出
        """
        # 处理简写格式：如果 config 是字符串，转换为字典
        if isinstance(config, str):
            config = {"command": config}
        
        # 确保 config 是字典类型
        if not isinstance(config, dict):
            raise ValueError(f"Invalid command config type: {type(config)}")
        
        # 获取必需字段
        command = config.get("command")
        if not command:
            raise ValueError("Command config missing 'command' field")
        
        # 获取步骤 ID，如果没有则生成
        step_id = config.get("id")
        if not step_id:
            step_id = context.generate_step_id() if hasattr(context, 'generate_step_id') else str(uuid4())
        
        # 获取参数
        params = config.get("params", {})
        
        # 获取依赖关系
        depends_on = config.get("depends_on", [])
        
        return StepCommand(
            step_id=step_id,
            command=command,
            params=params,
            depends_on=depends_on
        )
    
    def validate(self, ir: StepCommand) -> Tuple[bool, List[str]]:
        """
        验证 StepCommand 的有效性
        
        检查必需的字段是否存在、格式是否正确。
        
        Args:
            ir: 待验证的 StepCommand 实例
        
        Returns:
            Tuple[bool, List[str]]: 
                - bool: 是否验证通过
                - List[str]: 错误信息列表（验证通过时为空）
        """
        errors = []
        
        # 验证 step_id
        if not ir.step_id:
            errors.append("StepCommand: step_id is empty")
        
        # 验证 command
        if not ir.command:
            errors.append(f"StepCommand {ir.step_id}: command is empty")
        
        # 验证 command 格式（可选：检查是否包含语言标识）
        if ir.command and ":" not in ir.command:
            errors.append(f"StepCommand {ir.step_id}: command '{ir.command}' should follow 'language:command' format")
        
        # 验证 depends_on（只检查类型，不检查引用是否存在）
        if ir.depends_on is not None and not isinstance(ir.depends_on, list):
            errors.append(f"StepCommand {ir.step_id}: depends_on must be a list")
        
        # params 可以为空，不需要验证
        return len(errors) == 0, errors