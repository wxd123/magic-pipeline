# magic_pipeline/conext/command_context.py
"""
命令容器模块 - 统一管理所有命令的注册和获取
"""

from typing import Dict, Type, Optional, List, Tuple
from magic_pipeline.core.command import Command, LLMCommand


class CommandContext:
    """
    命令容器 - 单例模式，全局唯一
    
    提供命令的注册、查询、删除等管理功能。
    
    设计模式:
        - 单例模式: 全局只有一个容器实例
        - 注册表模式: 集中管理所有命令类
    
    示例:
        >>> container = CommandContext()
        >>> container.register(JavaCleanCommand)
        >>> cmd_class = container.get("java.clean")
        
        >>> # 使用便捷函数
        >>> from magicc_shared.container import register_command
        >>> register_command(PythonGenerateCommand)
    """
    
    _instance: Optional['CommandContext'] = None
    """单例实例"""
    
    _commands: Dict[str, Type[Command]] = {}
    """存储命令的字典:  {command_name: command_class}"""
    
    def __new__(cls) -> 'CommandContext':
        """
        实现单例模式，确保全局只有一个容器实例。
        
        Returns:
            CommandContext 的单例实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._commands = {}
        return cls._instance
    
    def register(self, cmd_class: Type[Command]) -> None:
        """
        注册单个命令到容器中。
        
        Args:           
            cmd_class: 命令类，必须继承自 Command
        
        Raises:
            TypeError: 如果 cmd_class 不是 Command 的子类，或命令名已存在
            ValueError: 如果 cmd_class.name 为空字符串
        
        示例:
            >>> container.register(PythonAnalyzeCommand)
        """
        if not issubclass(cmd_class, Command):
            raise TypeError(f"{cmd_class.__name__} must be a subclass of Command")
        
        if not cmd_class.name:
            raise ValueError(f"Command name cannot be empty: {cmd_class.name}")
        
        if cmd_class.name in self._commands:
            raise TypeError(f"{cmd_class.__name__} already registed")
        
        self._commands[cmd_class.name] = cmd_class

    def register_list(self, cmd_list: List[Type[Command]]) -> None:
        """
        批量注册命令到容器中。
        
        Args:            
            cmd_list: 命令类列表，所有类必须继承自 Command
        
        Raises:
            TypeError: 如果任一命令类不是 Command 的子类，或命令名已存在
            ValueError: 如果任一命令类的 name 属性为空字符串
        
        示例:
            >>> container.register_list([PythonAnalyzeCommand, JavaCleanCommand])
        """
        accept_list: List[Type[Command]] = []
        if cmd_list:
            for cmd_class in cmd_list:
                if not issubclass(cmd_class, Command):
                    raise TypeError(f"{cmd_class.__name__} must be a subclass of Command")                
                if not cmd_class.name:
                    raise ValueError(f"Command name cannot be empty: {cmd_class.name}")                
                if cmd_class.name in self._commands:
                    raise TypeError(f"{cmd_class.__name__} already registed")   
                accept_list.append(cmd_class)

        if accept_list:
            for accept_class in accept_list:
                self._commands[accept_class.name] = accept_class
        
    
    def get(self, cmd_name: str) -> Optional[Type[Command]]:
        """
        根据命令名获取命令类。
        
        Args:
            cmd_name: 命令名
        
        Returns:
            命令类，如果不存在返回 None
        
        示例:
            >>> cmd_class = container.get("java.clean")
            >>> if cmd_class:
            ...     result = cmd_class().execute(ctx)
        """
        cmd_command = self._commands.get(cmd_name)        
        return cmd_command
        
    
    def has(self, cmd_name: str) -> bool:
        """
        检查指定名称的命令是否已注册。
        
        Args:
            cmd_name: 命令名
        
        Returns:
            命令存在返回 True，否则返回 False
        """
        return self.get(cmd_name) is not None    
    
    
    def get_commands_requiring_llm(self) -> List[Type[Command]]:
        """
        获取所有需要 LLM 的命令类列表。
        
        筛选出所有继承自 LLMCommand 的命令。
        
        Returns:
            继承自 LLMCommand 的命令类列表
        
        示例:
            >>> # 获取所有需要 LLM 的命令
            >>> llm_cmds = container.get_commands_requiring_llm()
            >>> for cmd_class in llm_cmds:
            ...     print(f"{cmd_class.name}: {cmd_class.__name__}")
        """
        result = []
        
        for cmd_class in self._commands.values():
            if issubclass(cmd_class, LLMCommand):
                result.append(cmd_class)
        return result
    
    def list_all(self) -> List[Type[Command]]:
        """
        列出所有已注册的命令类。
        
        Returns:
            所有已注册命令类的列表
        
        示例:
            >>> all_cmds = container.list_all()
            >>> # 返回示例:
            >>> # [JavaCleanCommand, PythonGenerateCommand]
        """
        result: List[Type[Command]] = []
        for name, cmd_class in self._commands.items():
            result.append(cmd_class)
        return result
    
    
    def remove(self, cmd_name: str) -> bool:
        """
        根据命令名移除指定的命令。
        
        Args:
            cmd_name: 命令名
        
        Returns:
            成功移除返回 True，命令不存在返回 False
        """
        if cmd_name in self._commands:
            del self._commands[cmd_name]
            return True
        return False
    
    
    def clear(self) -> None:
        """清空容器中所有已注册的命令。"""
        self._commands.clear()
    
    def size(self) -> int:
        """
        获取容器中注册的命令总数。
        
        Returns:
            已注册命令的总数量
        """
        return len(self._commands.values())
    
    def is_empty(self) -> bool:
        """
        检查容器是否为空。
        
        Returns:
            没有任何命令时返回 True，否则返回 False
        """
        return len(self._commands) == 0





