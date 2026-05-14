# magicc_shared/container/decorators.py
"""
命令装饰器模块 - 提供命令注册的装饰器语法糖
"""

from typing import List, Optional, Type
from magic_pipeline.core.command import Command
from .command_context import CommandContext


def command():
    """
    装饰器：自动注册命令类到全局容器。
    
    使用此装饰器可以简化命令注册流程，无需显式调用 register_command。
    
    使用方式:
        from magicc_shared.container.decorators import command
        
        @command()
        class JavaCleanCommand(Command):
            name = "java.clean"  # 必须定义 name 属性
            def execute(self, ctx: Context) -> Result:
                # 命令实现
                pass
    
    注意:
        被装饰的类必须继承自 Command 或其子类，并且必须定义 name 类属性。
    
    Returns:
        装饰器函数
    """
    def decorator(cls: Type[Command]) -> Type[Command]:
        register_command(cls)
        return cls
    return decorator


def auto_register():
    """
    装饰器：自动注册命令类的别名。
    
    与 command() 装饰器功能完全相同，提供更具语义化的名称。
    
    使用方式:
        from magicc_shared.container.decorators import auto_register
        
        @auto_register()
        class PythonAnalyzeCommand(Command):
            name = "python.analyze"
            def execute(self, ctx: Context) -> Result:
                pass
    """
    return command()

# ============ 便捷函数 ============

# 全局单例实例
_command_container = CommandContext()
"""
全局命令容器单例实例，供便捷函数使用。
通常不直接访问此变量，而是使用下面的便捷函数。
"""

def register_command(cmd_class: Type[Command]) -> None:
    """
    注册单个命令到全局容器。
    
    这是 register 方法的便捷函数版本。
    
    Args:
        cmd_class: 命令类 (必须继承 Command)
    
    示例:
        >>> register_command(JavaCleanCommand)
    """
    _command_container.register(cmd_class)

def register_list(cmd_list: List[Type[Command]]) -> None:
    """
    批量注册命令到全局容器。
    
    Args:
        cmd_list: 命令类列表 (所有类必须继承 Command)
    
    示例:
        >>> register_list([JavaCleanCommand, PythonGenerateCommand])
    """
    _command_container.register_list(cmd_list)

def get_command(name: str) -> Optional[Type[Command]]:
    """
    从全局容器根据命令名获取命令类。
    
    这是 get 方法的便捷函数版本。
    
    Args:
        name: 命令名
    
    Returns:
        命令类，不存在时返回 None
    
    示例:
        >>> cmd_class = get_command("python.generate")
    """
    return _command_container.get(name)


def has_command(name: str) -> bool:
    """
    检查命令是否已注册到全局容器。
    
    这是 has 方法的便捷函数版本。
    
    Args:
        name: 命令名
    
    Returns:
        存在返回 True，否则返回 False
    """
    return _command_container.has(name)


def list_all_commands() -> List[Type[Command]]:
    """
    列出全局容器中所有已注册的命令。
    
    这是 list_all 方法的便捷函数版本。
    
    Returns:
        命令类列表
    
    示例:
        >>> all_cmds = list_all_commands()
    """
    return _command_container.list_all()


def remove_command(name: str) -> bool:
    """
    从全局容器中移除指定的命令。
    
    这是 remove 方法的便捷函数版本。
    
    Args:
        name: 命令名
    
    Returns:
        成功移除返回 True，命令不存在返回 False
    """
    return _command_container.remove(name)


def clear_all_commands() -> None:
    """清空全局容器中的所有命令。"""
    _command_container.clear()


def get_command_container() -> CommandContext:
    """
    获取全局命令容器单例实例。
    
    用于需要直接操作容器对象的场景。
    
    Returns:
        全局命令容器单例实例
    """
    return _command_container