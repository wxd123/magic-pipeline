# magic_pipeline/core/model/pipeline_yaml.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import yaml
import re
import subprocess
import concurrent.futures

from magic_base.protocol.pipeline import CommandConfig
from magic_pipeline.core.model.models import ModelConfig
from magic_pipeline.core.model.projects import ProjectInfo, ProviderConfig
from magic_pipeline.core.model.step.step_yaml import ConditionStep, LoopStep, ParallelStep, Step, SubPipelineStep








# ============ Pipeline 配置 ============

@dataclass
class PipelineConfig:
    """Pipeline 配置根节点"""
    project: ProjectInfo
    models: Dict[str, ModelConfig]
    provider: Dict[str, ProviderConfig]
    pipeline: List[Step]
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PipelineConfig':
        """从字典解析配置"""
        # 解析 project
        project_data = data.get('project', {})
        project = ProjectInfo(
            name=project_data.get('name', ''),
            code=project_data.get('code', ''),
            type=project_data.get('type', ''),
            description=project_data.get('description', ''),
            version=project_data.get('version', '1.0.0'),
            language=project_data.get('language', 'java'),
            work_path=project_data.get('work_path', '')
        )
        
        # 解析 models
        models = {}
        for name, cfg in data.get('models', {}).items():
            models[name] = ModelConfig(
                provider=cfg.get('provider', 'ollama'),
                name=cfg.get('name', ''),
                temperature=cfg.get('temperature', 0.3),
                max_tokens=cfg.get('max_tokens', 500)
            )
        
        # 解析 provider
        providers = {}
        for name, cfg in data.get('provider', {}).items():
            providers[name] = ProviderConfig(
                type=cfg.get('type', 'local'),
                url=cfg.get('url', 'http://localhost'),
                port=cfg.get('port', 11434)
            )
        
        # 解析 pipeline steps
        steps = cls._parse_steps(data.get('pipeline', []))
        
        return cls(
            project=project,
            models=models,
            provider=providers,
            pipeline=steps
        )
    
    @classmethod
    def _parse_steps(cls, steps_data: List[Dict]) -> List[Step]:
        """递归解析步骤"""
        steps = []
        
        for item in steps_data:
            # Command 节点
            if 'command' in item:
                steps.append(CommandConfig(
                    command=item['command'],
                    source_dir=item.get('source_dir', ''),
                    output_dir=item.get('output_dir', ''),
                    params=item.get('params'),
                    timeout=item.get('timeout')
                ))
            
            # Loop 节点
            elif 'loop' in item:
                loop_data = item['loop']
                steps.append(LoopStep(
                    items=loop_data.get('items', []),
                    steps=cls._parse_steps(loop_data.get('steps', [])),
                    item_var=loop_data.get('item_var', 'item'),
                    max_iterations=loop_data.get('max_iterations', 100)
                ))
            
            # Condition 节点
            elif 'condition' in item:
                cond_data = item['condition']
                cases = {}
                for case_value, case_steps in cond_data.get('cases', {}).items():
                    cases[case_value] = cls._parse_steps(case_steps)
                
                default_steps = None
                if 'default' in cond_data:
                    default_steps = cls._parse_steps(cond_data['default'])
                
                steps.append(ConditionStep(
                    on=cond_data.get('on', ''),
                    cases=cases,
                    default=default_steps
                ))
            
            # Parallel 节点
            elif 'parallel' in item:
                parallel_data = item['parallel']
                steps.append(ParallelStep(
                    steps=cls._parse_steps(parallel_data.get('steps', [])),
                    max_concurrency=parallel_data.get('max_concurrency', 3),
                    fail_fast=parallel_data.get('fail_fast', True)
                ))
            
            # SubPipeline 节点
            elif 'sub' in item:
                sub_data = item['sub']
                steps.append(SubPipelineStep(
                    path=sub_data.get('path', ''),
                    params=sub_data.get('params')
                ))
        
        return steps
    
    @classmethod
    def from_yaml(cls, path: str) -> 'PipelineConfig':
        """从 YAML 文件加载配置"""
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)
    
    def to_yaml(self, path: str):
        """保存为 YAML 文件"""
        data = {
            'project': {
                'name': self.project.name,
                'code': self.project.code,
                'type': self.project.type,
                'description': self.project.description,
                'version': self.project.version,
                'language': self.project.language,
                'work_path': self.project.work_path
            },
            'models': {
                name: {
                    'provider': cfg.provider,
                    'name': cfg.name,
                    'temperature': cfg.temperature,
                    'max_tokens': cfg.max_tokens
                }
                for name, cfg in self.models.items()
            },
            'provider': {
                name: {
                    'type': cfg.type,
                    'url': cfg.url,
                    'port': cfg.port
                }
                for name, cfg in self.provider.items()
            },
            'pipeline': self._steps_to_dict(self.steps)
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    def _steps_to_dict(self, steps: List[Step]) -> List[Dict]:
        """将步骤转换为字典"""
        result = []
        for step in steps:
            if isinstance(step, CommandConfig):
                item = {'command': step.command}
                if step.source_dir:
                    item['source_dir'] = step.source_dir
                if step.output_dir:
                    item['output_dir'] = step.output_dir
                if step.params:
                    item['params'] = step.params
                if step.timeout:
                    item['timeout'] = step.timeout
                result.append(item)
            
            elif isinstance(step, LoopStep):
                result.append({
                    'loop': {
                        'items': step.items,
                        'steps': self._steps_to_dict(step.steps),
                        'item_var': step.item_var,
                        'max_iterations': step.max_iterations
                    }
                })
            
            elif isinstance(step, ConditionStep):
                cases = {}
                for case_value, case_steps in step.cases.items():
                    cases[case_value] = self._steps_to_dict(case_steps)
                cond_dict = {'on': step.on, 'cases': cases}
                if step.default:
                    cond_dict['default'] = self._steps_to_dict(step.default)
                result.append({'condition': cond_dict})
            
            elif isinstance(step, ParallelStep):
                result.append({
                    'parallel': {
                        'steps': self._steps_to_dict(step.steps),
                        'max_concurrency': step.max_concurrency,
                        'fail_fast': step.fail_fast
                    }
                })
            
            elif isinstance(step, SubPipelineStep):
                item = {'sub': {'path': step.path}}
                if step.params:
                    item['sub']['params'] = step.params
                result.append(item)
        
        return result


# ============ 执行上下文 ============

class ExecutionContext:
    """执行上下文"""
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.current_item: Optional[str] = None
        self.results: List[Dict] = []
    
    def set(self, key: str, value: Any):
        """设置变量"""
        self.variables[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取变量，支持嵌套如 'result.status'"""
        keys = key.split('.')
        value = self.variables
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    def resolve(self, text: str) -> str:
        """解析路径中的变量 ${var}"""
        def replace(match):
            var_name = match.group(1)
            return str(self.get(var_name, match.group(0)))
        return re.sub(r'\${([^}]+)}', replace, text)


# ============ Pipeline 执行器 ============

class PipelineExecutor:
    """Pipeline 执行器"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.context = ExecutionContext()
    
    def execute(self) -> bool:
        """执行整个 Pipeline"""
        print(f"\n{'='*60}")
        print(f"开始执行 Pipeline: {self.config.project.name}")
        print(f"版本: {self.config.project.version}")
        print(f"{'='*60}\n")
        
        # 设置项目信息到上下文
        self.context.set('project', {
            'name': self.config.project.name,
            'code': self.config.project.code,
            'work_path': self.config.project.work_path
        })
        
        # 执行所有步骤
        for i, step in enumerate(self.config.steps, 1):
            print(f"步骤 {i}/{len(self.config.steps)}")
            if not self._execute_step(step):
                print(f"\n❌ Pipeline 执行失败")
                return False
            print()
        
        print(f"\n✅ Pipeline 执行成功")
        return True
    
    def _execute_step(self, step: Step, indent: int = 0) -> bool:
        """执行单个步骤"""
        prefix = "  " * indent
        
        if isinstance(step, CommandConfig):
            return self._execute_command(step, prefix)
        elif isinstance(step, LoopStep):
            return self._execute_loop(step, indent)
        elif isinstance(step, ConditionStep):
            return self._execute_condition(step, prefix)
        elif isinstance(step, ParallelStep):
            return self._execute_parallel(step, indent)
        elif isinstance(step, SubPipelineStep):
            return self._execute_sub(step, prefix)
        return False
    
    def _execute_command(self, cmd: CommandConfig, prefix: str) -> bool:
        """执行命令"""
        resolved_source = self.context.resolve(cmd.source_dir) if cmd.source_dir else ""
        resolved_output = self.context.resolve(cmd.output_dir) if cmd.output_dir else ""
        
        # 解析命令中的变量
        command_str = self.context.resolve(cmd.get_command_str())
        
        print(f"{prefix}🔧 执行命令: {command_str}")
        if resolved_source:
            print(f"{prefix}   源目录: {resolved_source}")
        if resolved_output:
            print(f"{prefix}   输出目录: {resolved_output}")
        
        try:
            # 执行命令
            result = subprocess.run(
                command_str,
                shell=True,
                capture_output=True,
                text=True,
                timeout=cmd.timeout,
                cwd=resolved_source or None
            )
            
            # 保存结果
            output = {
                'command': command_str,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'source_dir': resolved_source,
                'output_dir': resolved_output
            }
            
            self.context.set('last_result', output)
            self.context.results.append(output)
            
            if result.returncode != 0:
                print(f"{prefix}   ❌ 命令失败 (返回码: {result.returncode})")
                if result.stderr:
                    print(f"{prefix}   错误: {result.stderr[:200]}")
                return False
            
            print(f"{prefix}   ✅ 命令执行成功")
            return True
            
        except subprocess.TimeoutExpired:
            print(f"{prefix}   ❌ 命令超时 ({cmd.timeout}秒)")
            return False
        except Exception as e:
            print(f"{prefix}   ❌ 命令异常: {e}")
            return False
    
    def _execute_loop(self, loop: LoopStep, indent: int) -> bool:
        """执行循环"""
        prefix = "  " * indent
        print(f"{prefix}🔄 开始循环，共 {len(loop.items)} 项")
        
        for idx, item in enumerate(loop.items):
            if idx >= loop.max_iterations:
                break
            
            print(f"{prefix}   迭代 {idx + 1}/{len(loop.items)}: {loop.item_var}={item}")
            self.context.current_item = item
            self.context.set(loop.item_var, item)
            
            for step in loop.steps:
                if not self._execute_step(step, indent + 2):
                    return False
        
        print(f"{prefix}   ✅ 循环完成")
        return True
    
    def _execute_condition(self, cond: ConditionStep, prefix: str) -> bool:
        """执行条件分支"""
        value = self.context.get(cond.on)
        print(f"{prefix}🔀 条件判断: {cond.on} = {value}")
        
        # 查找匹配的 case
        str_value = str(value) if value is not None else "None"
        steps = cond.cases.get(str_value)
        
        if steps is None:
            steps = cond.default
        
        if not steps:
            print(f"{prefix}   没有匹配的分支，跳过")
            return True
        
        print(f"{prefix}   执行分支: {str_value}")
        for step in steps:
            if not self._execute_step(step, len(prefix) + 2):
                return False
        
        return True
    
    def _execute_parallel(self, parallel: ParallelStep, indent: int) -> bool:
        """并行执行"""
        prefix = "  " * indent
        print(f"{prefix}⚡ 并行执行 {len(parallel.steps)} 个步骤，最大并发: {parallel.max_concurrency}")
        
        def execute_wrapper(step, step_idx):
            print(f"{prefix}   并行任务 {step_idx + 1} 开始")
            result = self._execute_step(step, indent + 2)
            print(f"{prefix}   并行任务 {step_idx + 1} {'✅ 完成' if result else '❌ 失败'}")
            return result
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel.max_concurrency) as executor:
            futures = {
                executor.submit(execute_wrapper, step, idx): step 
                for idx, step in enumerate(parallel.steps)
            }
            
            for future in concurrent.futures.as_completed(futures):
                if not future.result() and parallel.fail_fast:
                    print(f"{prefix}   ❌ 并行步骤失败，快速失败")
                    return False
        
        print(f"{prefix}   ✅ 并行执行完成")
        return True
    
    def _execute_sub(self, sub: SubPipelineStep, prefix: str) -> bool:
        """执行子流程"""
        # 解析路径中的变量
        resolved_path = self.context.resolve(sub.path)
        print(f"{prefix}📎 执行子流程: {resolved_path}")
        
        # 传递参数
        if sub.params:
            for key, value in sub.params.items():
                resolved_value = self.context.resolve(value)
                self.context.set(key, resolved_value)
                print(f"{prefix}   参数: {key} = {resolved_value}")
        
        try:
            # 加载并执行子 pipeline
            sub_config = PipelineConfig.from_yaml(resolved_path)
            sub_executor = PipelineExecutor(sub_config)
            
            # 共享上下文变量
            sub_executor.context.variables = self.context.variables.copy()
            
            result = sub_executor.execute()
            if result:
                print(f"{prefix}   ✅ 子流程执行成功")
            else:
                print(f"{prefix}   ❌ 子流程执行失败")
            return result
            
        except FileNotFoundError:
            print(f"{prefix}   ❌ 子流程文件不存在: {resolved_path}")
            return False
        except Exception as e:
            print(f"{prefix}   ❌ 子流程异常: {e}")
            return False


# ============ 构建器（可选，用于代码构建） ============

class PipelineBuilder:
    """Pipeline 构建器 - 提供流畅的 API"""
    
    def __init__(self):
        self._project = None
        self._models = {}
        self._providers = {}
        self._steps = []
    
    def with_project(self, name: str, code: str, type: str = "default",
                     version: str = "1.0.0", language: str = "java",
                     work_path: str = "") -> 'PipelineBuilder':
        self._project = ProjectInfo(
            name=name, code=code, type=type,
            version=version, language=language, work_path=work_path
        )
        return self
    
    def add_model(self, name: str, provider: str, model_name: str,
                  temperature: float = 0.3, max_tokens: int = 500) -> 'PipelineBuilder':
        self._models[name] = ModelConfig(provider, model_name, temperature, max_tokens)
        return self
    
    def add_command(self, command: str, source_dir: str = "", 
                    output_dir: str = "", params: Dict = None,
                    timeout: int = None) -> 'PipelineBuilder':
        self._steps.append(CommandConfig(command, source_dir, output_dir, params, timeout))
        return self
    
    def add_loop(self, items: List[str], steps: List[Step],
                 item_var: str = "item") -> 'PipelineBuilder':
        self._steps.append(LoopStep(items, steps, item_var))
        return self
    
    def add_condition(self, on: str, cases: Dict, default: List[Step] = None) -> 'PipelineBuilder':
        self._steps.append(ConditionStep(on, cases, default))
        return self
    
    def add_parallel(self, steps: List[Step], max_concurrency: int = 3) -> 'PipelineBuilder':
        self._steps.append(ParallelStep(steps, max_concurrency))
        return self
    
    def add_sub(self, path: str, params: Dict = None) -> 'PipelineBuilder':
        self._steps.append(SubPipelineStep(path, params))
        return self
    
    def build(self) -> PipelineConfig:
        if not self._project:
            raise ValueError("Project is required")
        
        return PipelineConfig(
            project=self._project,
            models=self._models,
            provider=self._providers,
            steps=self._steps
        )


# ============ 使用示例 ============

def main():
    # 方式1: 从 YAML 文件加载并执行
    config = PipelineConfig.from_yaml('pipeline.yaml')
    executor = PipelineExecutor(config)
    executor.execute()


if __name__ == "__main__":
    main()