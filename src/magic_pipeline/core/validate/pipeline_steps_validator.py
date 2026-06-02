from pathlib import Path
from typing import Tuple, List, Set, Dict, Any
from .base_validator import BaseValidator
from magic_pipeline.core.model.step.step_yaml import  LoopStep, ConditionStep, ParallelStep, SubPipelineStep, Step
from magic_base.protocol.pipeline import CommandConfig

class PipelineStepsValidator(BaseValidator):
    """pipeline 步骤配置专用验证器"""
    
    def __init__(self, pipeline_data: list = None, model_names: Set[str] = None, file_path: Path = None):
        super().__init__(file_path) if file_path else None
        self.pipeline_data = pipeline_data
        self.model_names = model_names or set()
        self._converted_steps = None  # 存储转换后的 Step 对象
    
    def _do_validate(self, data: list = None):
        """验证pipeline步骤配置"""
        pipeline_data = data or self.pipeline_data
        
        if not pipeline_data:
            self.errors.append("pipeline 配置数据为空")
            return
        
        if not isinstance(pipeline_data, list):
            self.errors.append("pipeline 必须是列表类型")
            return
        
        for idx, step in enumerate(pipeline_data):
            self._validate_step(step, idx)
    
    def _validate_step(self, step: dict, idx: int):
        """验证单个步骤"""
        if not isinstance(step, dict):
            self.errors.append(f"pipeline[{idx}] 必须是字典类型")
            return
        
        if "command" in step:
            self._validate_command_step(step, idx)
        elif "loop" in step:
            self._validate_loop_step(step["loop"], idx)
        else:
            self.errors.append(f"pipeline[{idx}] 必须包含 'command' 或 'loop'")
    
    def _validate_command_step(self, step: dict, idx: int):
        """验证普通命令步骤"""
        required_fields = ["command", "source_dir", "output_dir"]
        for field in required_fields:
            if field not in step:
                self.errors.append(f"pipeline[{idx}] 缺少必需字段: {field}")
            elif not isinstance(step[field], str):
                self.errors.append(f"pipeline[{idx}].{field} 必须是字符串类型")
    
    def _validate_loop_step(self, loop: dict, idx: int):
        """验证循环命令步骤"""
        if not isinstance(loop, dict):
            self.errors.append(f"pipeline[{idx}].loop 必须是字典类型")
            return
        
        # 验证models
        self._validate_loop_models(loop, idx)
        
        # 验证steps
        self._validate_loop_steps(loop, idx)
    
    def _validate_loop_models(self, loop: dict, idx: int):
        """验证循环中的models配置"""
        if "models" not in loop:
            self.errors.append(f"pipeline[{idx}].loop 缺少必需字段: models")
            return
        
        if not isinstance(loop["models"], list):
            self.errors.append(f"pipeline[{idx}].loop.models 必须是列表类型")
            return
        
        # 验证模型引用
        for model_name in loop["models"]:
            if not isinstance(model_name, str):
                self.errors.append(f"pipeline[{idx}].loop.models 中的元素必须是字符串类型")
            elif self.model_names and model_name not in self.model_names:
                self.errors.append(
                    f"pipeline[{idx}].loop.models 引用的模型 '{model_name}' 未在models中定义"
                )
    
    def _validate_loop_steps(self, loop: dict, idx: int):
        """验证循环中的steps配置"""
        if "steps" not in loop:
            self.errors.append(f"pipeline[{idx}].loop 缺少必需字段: steps")
            return
        
        if not isinstance(loop["steps"], list):
            self.errors.append(f"pipeline[{idx}].loop.steps 必须是列表类型")
            return
        
        # 验证steps中的每个命令
        for cmd_idx, cmd in enumerate(loop["steps"]):
            self._validate_loop_command(cmd, idx, cmd_idx)
    
    def _validate_loop_command(self, cmd: dict, step_idx: int, cmd_idx: int):
        """验证循环中的单个命令"""
        if not isinstance(cmd, dict):
            self.errors.append(
                f"pipeline[{step_idx}].loop.steps[{cmd_idx}] 必须是字典类型"
            )
            return
        
        required_fields = ["command", "source_dir", "output_dir"]
        for field in required_fields:
            if field not in cmd:
                self.errors.append(
                    f"pipeline[{step_idx}].loop.steps[{cmd_idx}] 缺少必需字段: {field}"
                )
            elif not isinstance(cmd[field], str):
                self.errors.append(
                    f"pipeline[{step_idx}].loop.steps[{cmd_idx}].{field} 必须是字符串类型"
                )
    
    def convert_to_objects(self) -> List[Step]:
        """将验证通过的字典转换为 Step 对象列表"""
        if self.errors:
            raise ValueError("验证失败，无法转换")
        
        if self._converted_steps is None:
            self._converted_steps = self._convert_steps(self.pipeline_data)
        
        return self._converted_steps
    
    def _convert_steps(self, steps_data: List[dict]) -> List[Step]:
        """递归转换步骤字典为 Step 对象"""
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
                    id=loop_data.get('id'),
                    name=loop_data.get('name'),
                    steps=self._convert_steps(loop_data.get('steps', [])),
                    models=loop_data.get('models', []),
                    max_iterations=loop_data.get('max_iterations', 100)
                ))
            
            # Condition 节点（如果需要）
            elif 'condition' in item:
                cond_data = item['condition']
                cases = {}
                for case_value, case_steps in cond_data.get('cases', {}).items():
                    cases[case_value] = self._convert_steps(case_steps)
                
                default_steps = None
                if 'default' in cond_data:
                    default_steps = self._convert_steps(cond_data['default'])
                
                steps.append(ConditionStep(
                    on=cond_data.get('on', ''),
                    cases=cases,
                    default=default_steps
                ))
            
            # Parallel 节点（如果需要）
            elif 'parallel' in item:
                parallel_data = item['parallel']
                steps.append(ParallelStep(
                    steps=self._convert_steps(parallel_data.get('steps', [])),
                    max_concurrency=parallel_data.get('max_concurrency', 3),
                    fail_fast=parallel_data.get('fail_fast', True)
                ))
            
            # SubPipeline 节点（如果需要）
            elif 'sub' in item:
                sub_data = item['sub']
                steps.append(SubPipelineStep(
                    path=sub_data.get('path', ''),
                    params=sub_data.get('params')
                ))
        
        return steps


def validate_pipeline_steps(pipeline_data: list, model_names: Set[str] = None, file_path: Path = None) -> Tuple[bool, List[str], List[str]]:
    """验证pipeline步骤的便捷函数"""
    validator = PipelineStepsValidator(pipeline_data, model_names, file_path)
    validator._do_validate()
    return len(validator.errors) == 0, validator.errors, validator.warnings