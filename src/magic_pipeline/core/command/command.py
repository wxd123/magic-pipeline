# magic_pipeline/core/command/command.py
# BaseCommand 抽象接口

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseCommand(ABC):
    """
    命令抽象基类
    
    所有具体命令必须继承此类并实现 execute 方法和 name 属性。
    
    层级化命名规范:
        命令名称支持点分隔的多级命名，用于表达命令的领域归属和层级关系。
        
        Examples:
            # 一级命令（基础操作）
            "clean"                 # 清理操作
            "report"                # 报告生成
            
            # 二级命令（领域.操作）
            "comment.generate"      # 注释生成
            "comment.report"        # 注释报告
            "test.run"              # 测试执行
            "test.analyze"          # 测试分析
            
            # 三级命令（领域.子领域.操作）
            "comment.quality.check"     # 注释质量检查
            "comment.quality.score"     # 注释质量评分
            "test.coverage.report"      # 测试覆盖率报告
            
            # 四级命令（语言.领域.子领域.操作）
            "java.comment.generate"     # Java 注释生成
            "python.test.run"           # Python 测试执行
            "go.comment.quality.check"  # Go 注释质量检查
            
            # 版本化命令
            "comment.generate.v2"       # 注释生成 V2 版本
            "test.run.v3"               # 测试执行 V3 版本
            
            # 共享命令（跨语言通用）
            "shared.log.info"           # 通用日志输出
            "shared.metrics.collect"    # 通用指标收集
    
    使用示例:
        >>> class JavaCommentGenerateCommand(Command):
        ...     @property
        ...     def name(self) -> str:
        ...         return "java.comment.generate"
        ...     
        ...     def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ...         # 实现注释生成逻辑
        ...         return {"result": "success"}
        
        >>> class CleanCommand(Command):
        ...     @property
        ...     def name(self) -> str:
        ...         return "clean"
        ...     
        ...     def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        ...         # 实现清理逻辑
        ...         return {"status": "cleaned"}
    """
    
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行命令
        
        Args:
            params: 命令参数字典，键值对由具体命令定义
                   框架只负责传递，不校验具体内容
            
        Returns:
            执行结果字典，结构由具体命令定义
            
        Raises:
            MissingParamError: 缺少必要参数
            InvalidParamTypeError: 参数类型错误
            CommandError: 命令执行失败
        
        Examples:
            >>> cmd = ReadCSVCommand()
            >>> result = cmd.execute({"path": "data.csv"})
            >>> print(result["data"])
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        命令注册名称（只读属性）
        
        命名规范:
            - 使用小写字母、数字、下划线、点分隔符
            - 点号用于表达层级关系
            - 推荐深度: 1-4 级
            
        命名示例:
            一级: "clean", "report"
            二级: "comment.generate", "test.run"
            三级: "comment.quality.check"
            四级: "java.comment.generate"
            版本: "comment.generate.v2"
            共享: "shared.log.info"
        
        Returns:
            命令名称字符串，用于注册和调用
            
        Examples:
            >>> cmd.name
            'java.comment.generate'
        """
        pass

    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        验证参数
        
        子类可重写此方法进行参数校验。
        验证失败时抛出对应异常。
        
        Raises:
            MissingParamError: 缺少必要参数
            InvalidParamTypeError: 参数类型错误
            ParamError: 参数值错误
        """
        pass