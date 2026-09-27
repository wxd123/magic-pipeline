# magic-pipeline 架构

## 定位

magic-pipeline 是为 magic 生态提供通用节点编排能力的基础设施。

它是生态的公共底座，不隶属任何具体项目。它只做一件事：接收一个 pipeline 定义文件，按文件里声明的节点关系，调度实现了 Command 协议的命令依次执行。

它不关心命令来自哪个应用，也不知道有哪些应用存在。任何实现了 Command 协议的应用，都可以通过编写 pipeline 定义文件来使用它。

对外提供：

1. 一个通用的 pipeline 定义文件格式。
2. 一个执行接口。
3. 一个命令注册机制。
4. （消费）magic-protocol 的 Command 协议。

依赖：只依赖 magic-protocol（拿 Command 协议与共享类型）。

## 职责

提供：

- 通用 pipeline 定义文件格式（YAML 结构、字段、语义）。
- 执行接口（入口、调度、运行环境支撑）。
- 命令注册与发现机制。
- 配置校验（manifest / pipeline / models / project）。
- 持久化（项目 / 任务 / 方法）。
- LLM 接入（provider 管理）。

不做：

- 不定义 Command 协议（归 magic-protocol）。
- 不实现任何具体 Command（归应用）。
- 不关心、也不知道有哪些应用。
- 不做语言无关规范化。
- 不做语言相关解析 / 生成。

## 项目结构

src/magic_pipeline/
├── __init__.py
├── py.typed
│
├── constant/                   常量
│   └── pipeline.py             表名、项目码
│
├── context/                    上下文
│   ├── command_context.py      命令容器（单例）
│   ├── command_decorator.py    命令注册装饰器
│   ├── context.py              管道上下文聚合
│   ├── model_context.py        模型上下文
│   ├── step_context.py         步骤上下文
│   └── trace_context.py        审计追踪上下文
│
├── core/
│   ├── executor/               执行器
│   │   ├── executor.py         PipelineExecutor
│   │   ├── step_executor.py    StepExecutor
│   │   └── command_executor.py CommandExecutor
│   ├── model/                  配置模型
│   │   ├── pipeline_yaml.py    PipelineConfig / Builder / Executor
│   │   ├── manifest_yaml.py    ManifestConfig
│   │   ├── models.py           ModelConfig
│   │   ├── loops.py            LoopConfig
│   │   └── projects.py         ProjectInfo / ProviderConfig
│   ├── providers/              LLM provider
│   │   ├── base_provider.py    BaseProvider
│   │   └── ...                 OllamaProvider 等
│   ├── scope/                  作用域
│   │   ├── scope.py            BaseScope
│   │   └── step_scope.py       StepScope
│   └── validate/               校验器
│       ├── base_validator.py
│       ├── manifest_validator.py
│       ├── pipeline_validator.py
│       ├── pipeline_steps_validator.py
│       ├── models_validator.py
│       ├── provider_validator.py
│       ├── project_validator.py
│       ├── structure_validator.py
│       └── validator.py
│
├── data_access/                持久化
│   └── ...                     Projects / Repository / Service
│
├── messages/                   国际化消息
│   ├── en_US.py
│   ├── zh_CN.py
│   └── message.py
│
└── register/                   命令注册
    └── register.py             CommandRegistry

## 数据流

pipeline 自身的执行流：

pipeline 定义文件（pipeline.yaml + manifest.yaml）
    ↓ validate/*（配置校验）
PipelineConfig / ManifestConfig
    ↓ PipelineExecutor（执行入口）
    ↓ 按步骤
StepExecutor
    ↓ 找命令
CommandRegistry / CommandContext
    ↓ 建运行环境
StepScope / TraceContext
    ↓ 执行
Command.execute(ctx)
    ↓ 返回
Result
    ↓
下一步 / 最终结果

关键：pipeline 不知道命令来自哪个应用，只按注册名查找。

## 模块职责

### context/

命令与运行上下文的容器。

- command_context.py：CommandContext，单例，注册 / 查询 / 删除命令。
- command_decorator.py：@command() 装饰器及便捷函数。
- context.py：PipelineContext（聚合容器）、MagicPipelineContext（全局单例管理）。
- model_context.py：ModelContext，模型配置注册与查询。
- step_context.py：StepContext，步骤配置与运行时变量。
- trace_context.py：TraceContext，四层审计追踪（Agent → Pipeline → Step → Command）。

### core/executor/

三级执行器。

- executor.py：PipelineExecutor，读配置、注册命令、按步骤执行、释放资源。
- step_executor.py：StepExecutor，执行单个步骤。
- command_executor.py：CommandExecutor，执行单条命令。

### core/model/

配置模型。

- pipeline_yaml.py：PipelineConfig、PipelineBuilder、ExecutionContext。
- manifest_yaml.py：ManifestConfig、Whitelist、LocalNetwork。
- models.py：ModelConfig。
- loops.py：LoopConfig。
- projects.py：ProjectInfo、ProviderConfig。

### core/providers/

LLM provider 抽象与实现。

- base_provider.py：BaseProvider（start / stop / is_running / has_model / pull_model / generate）。

### core/scope/

作用域，管理资源与临时目录。

- scope.py：BaseScope（set / get / get_llm）。
- step_scope.py：StepScope（create_temp_dir / require_model / require_cmd）。

### core/validate/

配置校验器，按配置段分工。

- base_validator.py：BaseValidator。
- manifest_validator.py / pipeline_validator.py / pipeline_steps_validator.py / models_validator.py / provider_validator.py / project_validator.py：各配置段专用。
- structure_validator.py：项目结构校验。
- validator.py：ProjectArchitectureValidator，按顺序组合验证。

### data_access/

持久化。项目 / 任务 / 方法的仓储与服务。

### messages/

国际化消息。en_US / zh_CN 两套，get_pipeline_msg 自动检测语言。

### register/

命令注册表。CommandRegistry，按 module + command_name 注册与查找。

## 核心原则

1. 通用编排框架：只认 Command 协议，不关心应用是谁。
2. 编排即数据：流程写在 pipeline 定义文件里，不写死在代码里。
3. 协议归 protocol：Command 协议在 magic-protocol，pipeline 只消费。
4. 运行环境不外泄：StepScope / TraceContext / PipelineExecutor 是 pipeline 内部，应用不见。
5. 只依赖 protocol：pipeline 的唯一项目依赖是 magic-protocol。
6. 不知道应用：pipeline 不 import、不引用任何应用，也不在文档里提及具体应用。

## 接入契约

pipeline 对外的接口面：

契约                    内容                                              归属
Command 协议            Command / CommandConfig / Result 类型             magic-protocol
pipeline 定义文件格式    pipeline.yaml / manifest.yaml 的结构与字段        magic-pipeline
执行接口                PipelineExecutor 等入口                           magic-pipeline
命令注册机制            CommandRegistry / @command 装饰器                 magic-pipeline

一个应用要使用 pipeline，只需：实现 Command 协议、注册命令、编写 pipeline 定义文件、调用执行接口。pipeline 不关心这个应用是什么。

## 当前状态

已实现：

- context/：命令容器、装饰器、上下文聚合、模型上下文、步骤上下文、追踪上下文。
- core/executor/：PipelineExecutor / StepExecutor / CommandExecutor。
- core/model/：pipeline / manifest / models / loops / projects 配置模型。
- core/providers/：BaseProvider 及具体 provider。
- core/scope/：BaseScope / StepScope。
- core/validate/：各配置段校验器。
- data_access/：项目持久化。
- messages/：中英双语消息。
- register/：CommandRegistry。

未实现 / 待确认：

- 准确清单需人工核对。

## 演进方向

短期：

- 补全 provider 实现。
- 补全校验覆盖。
- 明确循环 / 条件 / 并行 / 子管道的语义与文档。

中期：

- 扩展 pipeline 定义文件格式的表达能力。
- 完善命令发现机制（entry points 等）。

长期：

- 保持通用性：不引入任何应用的语义。
- 保持单向依赖：只依赖 protocol。
- 文档里不出现具体应用名。