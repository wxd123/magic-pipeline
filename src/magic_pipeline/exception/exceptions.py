# magic_pipeline/exceptions.py
"""
Pipeline 异常定义模块

定义 Pipeline 执行过程中可能抛出的所有异常类型。
遵循继承层次结构，便于框架统一捕获和处理。

异常层次结构:
    PipelineError                    # 所有异常的基类
    ├── CommandError                 # 命令相关异常
    │   └── ParamError               # 参数相关异常
    │       ├── MissingParamError    # 缺少必要参数
    │       ├── InvalidParamTypeError # 参数类型错误
    │       └── InvalidParamValueError # 参数值错误
    ├── ConfigError                  # 配置解析错误
    └── ResolveError                 # 变量引用解析错误

使用示例:
    >>> from magic_pipeline.exceptions import MissingParamError
    >>> 
    >>> def validate_params(params):
    ...     if "path" not in params:
    ...         raise MissingParamError("path")
    >>> 
    >>> try:
    ...     validate_params({})
    ... except MissingParamError as e:
    ...     print(e)  # Missing required parameter: 'path'
    ...     print(e.param_name)  # path
"""


class PipelineError(Exception):
    """
    Pipeline 异常基类
    
    所有 Pipeline 相关异常的顶层父类。
    框架捕获此异常及其子类进行统一处理。
    
    使用场景:
        当不确定具体异常类型时，可使用此异常作为通用异常抛出。
    """
    pass


class CommandError(PipelineError):
    """
    命令异常基类
    
    所有命令执行相关的异常继承自此异常。
    
    使用场景:
        - 命令执行过程中的通用错误
        - 作为命令相关异常的父类，便于统一捕获
    """
    pass


class ParamError(CommandError):
    """
    参数错误基类
    
    所有命令参数校验相关的异常继承自此异常。
    
    使用场景:
        - 作为参数相关异常的父类
        - 当需要统一捕获参数错误时使用
    """
    pass


class MissingParamError(ParamError):
    """
    缺少必要参数异常
    
    当命令的必要参数未在 params 字典中提供时抛出。
    
    Attributes:
        param_name: 缺少的参数名称
    
    示例:
        >>> raise MissingParamError("path")
        Missing required parameter: 'path'
    """
    
    def __init__(self, param_name: str):
        """
        初始化缺少参数异常
        
        Args:
            param_name: 缺少的参数名称
        """
        super().__init__(f"Missing required parameter: '{param_name}'")
        self.param_name = param_name


class InvalidParamTypeError(ParamError):
    """
    参数类型错误异常
    
    当参数值的类型与预期类型不符时抛出。
    
    Attributes:
        param_name: 参数名称
        expected: 期望的类型名称
        actual: 实际的类型对象
    
    示例:
        >>> raise InvalidParamTypeError("count", "int", type("3"))
        Parameter 'count' expected int, got str
    """
    
    def __init__(self, param_name: str, expected: str, actual: type):
        """
        初始化参数类型错误异常
        
        Args:
            param_name: 参数名称
            expected: 期望的类型名称（如 "int", "str", "list"）
            actual: 实际的类型对象
        """
        super().__init__(
            f"Parameter '{param_name}' expected {expected}, got {actual.__name__}"
        )
        self.param_name = param_name
        self.expected = expected
        self.actual = actual


class InvalidParamValueError(ParamError):
    """
    参数值错误异常
    
    当参数值不符合业务规则时抛出（如超出范围、格式不正确等）。
    
    Attributes:
        param_name: 参数名称
        value: 无效的参数值
        reason: 错误原因描述
    
    示例:
        >>> raise InvalidParamValueError("age", -1, "must be >= 0")
        Parameter 'age' value '-1' invalid: must be >= 0
        
        >>> raise InvalidParamValueError("email", "invalid", "invalid email format")
        Parameter 'email' value 'invalid' invalid: invalid email format
    """
    
    def __init__(self, param_name: str, value: any, reason: str):
        """
        初始化参数值错误异常
        
        Args:
            param_name: 参数名称
            value: 无效的参数值
            reason: 错误原因描述
        """
        super().__init__(
            f"Parameter '{param_name}' value '{value}' invalid: {reason}"
        )
        self.param_name = param_name
        self.value = value
        self.reason = reason


class ConfigError(PipelineError):
    """
    配置错误异常
    
    当 Pipeline 配置文件解析失败时抛出。
    
    使用场景:
        - YAML 格式错误
        - 缺少必需的配置字段（如 pipeline 顶层字段）
        - 步骤缺少 id 或 command 字段
        - 依赖引用了不存在的步骤
    
    示例:
        >>> raise ConfigError("Missing 'pipeline' field in config")
        >>> raise ConfigError("Step 'read' missing 'command' field")
        >>> raise ConfigError("Dependency 'unknown' not found")
    """
    pass


class ResolveError(PipelineError):
    """
    变量引用解析错误异常
    
    当 `{{step.field}}` 变量引用无法解析时抛出。
    
    使用场景:
        - 引用的步骤不存在
        - 引用的字段在步骤输出中不存在
        - 变量语法错误
    
    示例:
        >>> raise ResolveError("Step 'unknown' not found")
        >>> raise ResolveError("Field 'data' not found in step 'read'")
        >>> raise ResolveError("Invalid variable syntax: '{{read'")
    """
    pass