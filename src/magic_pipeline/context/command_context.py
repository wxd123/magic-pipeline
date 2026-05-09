# magicc_shared/container/command_context.py
"""
命令容器模块 - 统一管理所有命令的注册和获取

两层设计:
- 第一层: 业务/模块标识 (comment, generate, test, report, etc.)
- 第二层: 命令路径，支持点号进行多级划分 (java.clean, java.save, python.run)

命令唯一标识格式: {module}:{command_path}
例如: 
    - comment:java.clean
    - generate:java.save
    - test:java.run
    - report:java.show
"""

from typing import Dict, Type, Optional, List, Tuple
from magic_pipeline.core import BaseCommand


class CommandContext:
    """
    命令容器 - 单例模式，全局唯一
    
    提供命令的注册、查询、删除等管理功能。采用两层结构组织命令：
    第一层按业务模块分类，第二层按命令路径分类（支持点号多级划分）。
    
    设计模式:
        - 单例模式: 全局只有一个容器实例
        - 注册表模式: 集中管理所有命令类
    
    命令唯一标识格式: {module}:{command_path}
    
    示例:
        >>> container = CommandContext()
        >>> container.register("comment",  JavaCommentCleanCommand)
        >>> cmd_class = container.get("comment", "java.clean")
        
        >>> # 使用便捷函数
        >>> from magicc_shared.container import regist_command
        >>> regist_command("test",  JavaTestRunCommand)
    """
    
    _instance: Optional['CommandContext'] = None
    """单例实例"""
    
    _commands: Dict[str, Dict[str, Type[BaseCommand]]] = {}
    """存储命令的嵌套字典: {module: {command_path: command_class}}"""
    
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
    
    def register(self, module: str, cmd_class: Type[BaseCommand]) -> None:
        """
        注册命令到容器中。
        
        Args:
            module: 业务/模块标识，如 "comment", "generate", "test", "report"            
            cmd_class: 命令类，必须继承自 BaseCommand
        
        Raises:
            TypeError: 如果 cmd_class 不是 BaseCommand 的子类
            ValueError: 如果 module 或 command_path 为空字符串
        
        示例:
            >>> container.register("comment", "java.clean", JavaCommentCleanCommand)
        """
        if not issubclass(cmd_class, BaseCommand):
            raise TypeError(f"{cmd_class.__name__} must be a subclass of BaseCommand")
        
        _command_path = cmd_class.name
        if not module or not _command_path:
            raise ValueError(f"Module and command_path cannot be empty: {module}:{_command_path}")
        
        if module not in self._commands:
            self._commands[module] = {}
        
        self._commands[module][_command_path] = cmd_class

    def regist_list(self, module: str, cmd_list: List[Type[BaseCommand]]) -> None:
        """
        注册命令到容器中。
        
        Args:
            module: 业务/模块标识，如 "comment", "generate", "test", "report"            
            cmd_list: 命令类集合，必须继承自 BaseCommand
        
        Raises:
            TypeError: 如果 cmd_class 不是 BaseCommand 的子类
            ValueError: 如果 module 或 command_path 为空字符串
        
        示例:
            >>> container.regist_list("comment", [JavaCommentCleanCommand])
        """

        
        
        if not module or not cmd_list:
            raise ValueError(f"Module and command_path cannot be empty: {module}:{cmd_list}")
        
        if module not in self._commands:
            self._commands[module] = {}

        for cmd_class in cmd_list:
            if not issubclass(cmd_class, BaseCommand):
                raise TypeError(f"{cmd_class.__name__} must be a subclass of BaseCommand")
            else:
                cmd_name = cmd_class.name
                self._commands[module][cmd_name] = cmd_class        
        
    
    def get(self, module: str, command_name: str) -> Optional[Type[BaseCommand]]:
        """
        获取命令类。
        
        Args:
            module: 业务/模块标识
            command_name: 命令名称(BaseCommand.name)
        
        Returns:
            命令类，如果不存在返回 None
        
        示例:
            >>> cmd_class = container.get("comment", "java.clean")
        """
        lang_commands = self._commands.get(module)
        if lang_commands:
            return lang_commands.get(command_name)
        return None
    
    def get_with_default(self, module: str, command_name: str, default_module: str = "java") -> Optional[Type[BaseCommand]]:
        """
        获取命令类，支持回退到默认模块。
        
        当指定模块中找不到命令时，自动尝试从默认模块中获取。
        
        Args:
            module: 首选模块标识
            command_name: 命令名称(BaseCommand.name)
            default_module: 默认模块（首选模块找不到时使用），默认为 "java"
        
        Returns:
            命令类，如果都不存在返回 None
        
        示例:
            >>> # 如果 comment 模块中没有 java.clean，会尝试获取 java 模块的 java.clean 命令
            >>> cmd = container.get_with_default("comment", "java.clean", default_module="java")
        """
        cmd = self.get(module, command_name)
        if cmd is None and module != default_module:
            cmd = self.get(default_module, command_name)
        return cmd
    
    def has(self, module: str, command_name: str) -> bool:
        """
        检查命令是否存在。
        
        Args:
            module: 业务/模块标识
            command_name: 命令名称(BaseCommand.name)
        
        Returns:
            命令存在返回 True，否则返回 False
        """
        return self.get(module, command_name) is not None
    
    def get_by_module(self, module: str) -> Dict[str, Type[BaseCommand]]:
        """
        获取指定模块的所有命令。
        
        Args:
            module: 业务/模块标识
        
        Returns:
            字典的副本，键为命令路径，值为命令类；如果模块不存在则返回空字典
        
        示例:
            >>> comment_commands = container.get_by_module("comment")
            >>> for path, cmd_class in comment_commands.items():
            ...     print(f"{path}: {cmd_class.__name__}")
        """
        return self._commands.get(module, {}).copy()
    
    def get_by_command_name(self, command_name: str) -> Dict[str, Type[BaseCommand]]:
        """
        获取所有模块中指定命令路径的命令。
        
        跨模块搜索相同命令路径的实现。
        
        Args:
            command_name: 命令名称(BaseCommand.name)如 "java.clean"
        
        Returns:
            字典，键为模块名，值为命令类；如果找不到则返回空字典
        
        示例:
            >>> clean_commands = container.get_by_command_name("java.clean")
            >>> # 可能返回 {"comment": JavaCommentCleanCommand, "generate": JavaGenerateCleanCommand}
        """
        result = {}
        for module, commands in self._commands.items():
            if command_name in commands:
                result[module] = commands[command_name]
        return result
    
    def get_commands_requiring_llm(self, module: str = None) -> List[Tuple[str, str, Type[BaseCommand]]]:
        """
        获取需要 LLM 的命令列表。
        
        筛选出所有继承自 LLMCommand 的命令。
        
        Args:
            module: 可选，指定模块；若为 None 则搜索所有模块
        
        Returns:
            (module, command_path, cmd_class) 元组的列表
        
        示例:
            >>> # 获取所有需要 LLM 的命令
            >>> llm_cmds = container.get_commands_requiring_llm()
            >>> for mod, path, cmd_class in llm_cmds:
            ...     print(f"{mod}:{path}: {cmd_class.__name__}")
            
            >>> # 只获取 comment 模块中需要 LLM 的命令
            >>> comment_llm = container.get_commands_requiring_llm("comment")
        """
        result = []
        modules = [module] if module else self._commands.keys()
        
        for mod in modules:
            for path, cmd_class in self._commands.get(mod, {}).items():
                if issubclass(cmd_class, BaseCommand):
                    result.append((mod, path, cmd_class))
        return result
    
    def list_all(self) -> Dict[str, Dict[str, str]]:
        """
        列出所有已注册的命令。
        
        Returns:
            嵌套字典，格式为 {module: {command_path: class_path}}，
            其中 class_path 为 "模块名.类名" 格式的字符串
        
        示例:
            >>> all_cmds = container.list_all()
            >>> # 返回示例:
            >>> # {
            >>> #     "comment": {"java.clean": "comment_commands.JavaCommentCleanCommand"},
            >>> #     "generate": {"java.save": "generate_commands.JavaGenerateSaveCommand"}
            >>> # }
        """
        result = {}
        for module, commands in self._commands.items():
            result[module] = {
                command_path: f"{cmd_class.__module__}.{cmd_class.__name__}"
                for command_path, cmd_class in commands.items()
            }
        return result
    
    def list_modules(self) -> List[str]:
        """
        列出所有已注册的模块。
        
        Returns:
            模块标识符列表
        
        示例:
            >>> modules = container.list_modules()
            >>> print(modules)  # ['comment', 'generate', 'test', 'report']
        """
        return list(self._commands.keys())
    
    def remove(self, module: str, command_path: str) -> bool:
        """
        移除指定的命令。
        
        Args:
            module: 业务/模块标识
            command_path: 命令路径
        
        Returns:
            成功移除返回 True，命令不存在返回 False
        """
        if module in self._commands and command_path in self._commands[module]:
            del self._commands[module][command_path]
            return True
        return False
    
    def remove_module(self, module: str) -> bool:
        """
        移除整个模块的所有命令。
        
        Args:
            module: 业务/模块标识
        
        Returns:
            成功移除返回 True，模块不存在返回 False
        """
        if module in self._commands:
            del self._commands[module]
            return True
        return False
    
    def clear(self) -> None:
        """清空所有已注册的命令。"""
        self._commands.clear()
    
    def size(self) -> int:
        """
        获取注册的命令总数。
        
        Returns:
            所有模块中命令的总数量
        """
        return sum(len(cmds) for cmds in self._commands.values())
    
    def is_empty(self) -> bool:
        """
        检查容器是否为空。
        
        Returns:
            没有任何命令时返回 True，否则返回 False
        """
        return self.size() == 0


