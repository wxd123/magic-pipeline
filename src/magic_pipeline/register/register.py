# magic_pipeline/register/register.py

from typing import Dict, Type, Optional, List
from magic_base import ApplicationContext
from magic_pipeline.constant import PIPELINE_PROJECT_CODE
from magic_pipeline.context import PipelineContext
from magic_pipeline.core.command import Command


class CommandRegistry:
    """
    命令注册器 - 统一管理命令的注册和获取
    
    使用方式:
        # 注册命令
        CommandRegistry.reg("comment", JavaCommentCleanCommand)
        CommandRegistry.reg_list("comment", [JavaCommentCleanCommand, JavaCommentReportCommand])
        
        # 获取命令
        cmd = CommandRegistry.get("comment", "java.clean")
        
        # 装饰器注册
        @CommandRegistry.cmd("comment")
        class JavaCommentGenerateCommand(Command):
            @property
            def name(self) -> str:
                return "java.generate"
    """
    
    _pipeline_context: PipelineContext= None
    _container = None

    def __init__(self):
        if CommandRegistry._pipeline_context is None:            
            self._pipeline_context = ApplicationContext[PipelineContext].get_context(PIPELINE_PROJECT_CODE)
            self._container = self._pipeline_context.command_context
            

    @classmethod
    def reg(cls, module: str, cmd_class: Type[Command]) -> None:
        """注册单个命令"""
        cls._container.register(module, cmd_class)
    
    @classmethod
    def reg_list(cls, module: str, cmd_list: List[Type[Command]]) -> None:
        """批量注册命令"""
        cls._container.regist_list(module, cmd_list)
    
    @classmethod
    def get(cls, module: str, command_name: str) -> Optional[Type[Command]]:
        """获取命令类"""
        return cls._container.get(module, command_name)
    
    @classmethod
    def get_with_default(cls, module: str, command_path: str, default_module: str = "java") -> Optional[Type[Command]]:
        """获取命令类（支持默认模块回退）"""
        return cls._container.get_with_default(module, command_path, default_module)
    
    @classmethod
    def has(cls, module: str, command_path: str) -> bool:
        """检查命令是否存在"""
        return cls._container.has(module, command_path)
    
    @classmethod
    def get_by_module(cls, module: str) -> Dict[str, Type[Command]]:
        """获取指定模块的所有命令"""
        return cls._container.get_by_module(module)
    
    @classmethod
    def get_by_command_path(cls, command_path: str) -> Dict[str, Type[Command]]:
        """获取所有模块中指定命令路径的命令"""
        return cls._container.get_by_command_path(command_path)
    
    @classmethod
    def list_all(cls) -> Dict[str, Dict[str, str]]:
        """列出所有命令"""
        return cls._container.list_all()
    
    @classmethod
    def list_modules(cls) -> List[str]:
        """列出所有模块"""
        return cls._container.list_modules()
    
    @classmethod
    def remove(cls, module: str, command_path: str) -> bool:
        """移除命令"""
        return cls._container.remove(module, command_path)
    
    @classmethod
    def remove_module(cls, module: str) -> bool:
        """移除整个模块"""
        return cls._container.remove_module(module)
    
    @classmethod
    def clear(cls) -> None:
        """清空所有命令"""
        cls._container.clear()
    
    @classmethod
    def size(cls) -> int:
        """获取命令总数"""
        return cls._container.size()
    
    @classmethod
    def is_empty(cls) -> bool:
        """检查是否为空"""
        return cls._container.is_empty()
    
    @classmethod
    def cmd(cls, module: str):
        """装饰器：自动注册命令"""
        def decorator(cmd_class):
            cls.reg(module, cmd_class)
            return cmd_class
        return decorator


# 便捷别名（可选）
reg_command = CommandRegistry.reg
reg_list = CommandRegistry.reg_list
get = CommandRegistry.get