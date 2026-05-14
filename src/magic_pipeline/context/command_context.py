# magicc_shared/container/command_container.py
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
    
    _commands:  Dict[str, Type[Command]] = {}
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
        注册命令到容器中。
        
        Args:           
            cmd_class: 命令类，必须继承自 Command
        
        Raises:
            TypeError: 如果 cmd_class 不是 Command 的子类
            ValueError: 如果 cmd_class.name 为空字符串
        
        示例:
            >>> container.register(PythonAnalyzeCommand)
        """
        if not issubclass(cmd_class, Command):
            raise TypeError(f"{cmd_class.__name__} must be a subclass of Command")
        
        if not cmd_class.name :
            raise ValueError(f"Command name cannot be empty: {cmd_class.name}")
        
        if cmd_class.name in self._commands:
            raise TypeError(f"{cmd_class.__name__} already registed")
        
        self._commands[cmd_class.name] = cmd_class

    def reg_list(self, cmd_list: List[Type[Command]]) -> None:
        """
        注册命令到容器中。
        
        Args:            
            cmd_list: 命令类集合，必须继承自 Command
        
        Raises:
            TypeError: 如果 cmd_class 不是 Command 的子类
            ValueError: 如果 cmd_class.name 为空字符串
        
        示例:
            >>> container.reg_list( [PythonAnalyzeCommand] )
        """
        accept_list:List[Type[Command]] = []
        if cmd_list:
            for cmd_class in cmd_list:
                if not issubclass(cmd_class, Command):
                    raise TypeError(f"{cmd_class.__name__} must be a subclass of Command")                
                if not cmd_class.name :
                    raise ValueError(f"Command name cannot be empty: {cmd_class.name}")                
                if cmd_class.name in self._commands:
                    raise TypeError(f"{cmd_class.__name__} already registed")   
                accept_list.append(cmd_class)

        if accept_list:
            for accept_class in accept_list:
                self._commands[accept_class.name] = accept_class
        
    
    def get(self, cmd_name: str) -> Optional[Type[Command]]:
        """
        获取命令类。
        
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
        
    
    
    
    def has(self,  cmd_name: str) -> bool:
        """
        检查命令是否存在。
        
        Args:
            cmd_name: 命令名
        
        Returns:
            命令存在返回 True，否则返回 False
        """
        return self.get(cmd_name) is not None    
    
    
    
    def get_commands_requiring_llm(self) -> List[Type[Command]]:
        """
        获取需要 LLM 的命令列表。
        
        筛选出所有继承自 LLMCommand 的命令。
        
        
        
        Returns:
            (cmd_class) 元组的列表
        
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
        列出所有已注册的命令。
        
        Returns:
            命令类集合 List[Type[Command]]
        
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
        移除指定的命令。
        
        Args:
            name: 命令名
        
        Returns:
            成功移除返回 True，命令不存在返回 False
        """
        if cmd_name in self._commands :
            del self._commands[cmd_name]
            return True
        return False
    
    
    
    def clear(self) -> None:
        """清空所有已注册的命令。"""
        self._commands.clear()
    
    def size(self) -> int:
        """
        获取注册的命令总数。
        
        Returns:
            所有语言中命令的总数量
        """
        return len(self._commands.values())
    
    def is_empty(self) -> bool:
        """
        检查容器是否为空。
        
        Returns:
            没有任何命令时返回 True，否则返回 False
        """
        return len(self._commands) == 0


# 全局单例实例
_command_container = CommandContext()
"""
全局命令容器单例实例，供便捷函数使用。
通常不直接访问此变量，而是使用下面的便捷函数。
"""


# ============ 便捷函数 ============

def register_command(cmd_class: Type[Command]) -> None:
    """
    注册命令到全局容器。
    
    这是 register 方法的便捷函数版本。
    
    Args:

        cmd_class: 命令类 (必须继承 Command)
    
    示例:
        >>> register_command( JavaCleanCommand)
    """
    _command_container.register(cmd_class)

def reg_list(cmd_list: List[Type[Command]]) -> None:
    """
    注册命令集合到全局容器。    
    Args:
        cmd_list: 命令类集合 (必须继承 Command)
    
    示例:
        >>> reg_list( [JavaCleanCommand, PythonGenerateCommand])
    """
    _command_container.reg_list(cmd_list)

def get_command( name: str) -> Optional[Type[Command]]:
    """
    从全局容器获取命令类。
    
    这是 get 方法的便捷函数版本。
    
    Args:
        name: 命令名
    
    Returns:
        命令类，不存在时返回 None
    
    示例:
        >>> cmd_class = get_command("python.generate")
    """
    return _command_container.get( name)




def has_command( name: str) -> bool:
    """
    检查命令是否存在。
    
    这是 has 方法的便捷函数版本。
    
    Args:
        name: 命令名
    
    Returns:
        存在返回 True，否则返回 False
    """
    return _command_container.has(name)





def list_all_commands() -> List[Type[Command]]:
    """
    列出所有命令。
    
    这是 list_all 方法的便捷函数版本。
    
    Returns:
        命令列表 List[Type[Command]]
    """
    return _command_container.list_all()




def remove_command( name: str) -> bool:
    """
    移除命令。
    
    这是 remove 方法的便捷函数版本。
    
    Args:
        name: 命令名
    
    Returns:
        成功移除返回 True
    """
    return _command_container.remove( name)


def clear_all_commands() -> None:
    """清空所有命令。"""
    _command_container.clear()


def get_command_container() -> CommandContext:
    """
    获取命令容器实例。
    
    用于需要直接操作容器对象的场景。
    
    Returns:
        全局命令容器单例实例
    """
    return _command_container


# ============ 装饰器语法糖 ============

def command():
    """
    装饰器：自动注册命令到全局容器。
    
    使用此装饰器可以简化命令注册流程，无需显式调用 register_command。
    
    
    Returns:
        装饰器函数
    
    使用方式:
        @command()
        class JavaCleanCommand(Command):
            name = "java.clean"  # 必须定义 name 属性
            def execute(self, ctx: Context) -> Result:
                # 命令实现
                pass
    
    注意:
        被装饰的类必须继承自 Command 或其子类。
    """
    def decorator(cls):
        register_command(cls)
        return cls
    return decorator