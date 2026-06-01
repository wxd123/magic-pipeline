import os
from pathlib import Path
from typing import Any, Dict, Optional

from magic_pipeline.core.model.pipeline_yaml import ProjectInfo


class ConfigLoader:
    """配置加载器"""
    
    @staticmethod
    def find_files(config_dir: Path):
        """自动查找配置文件"""
        if not config_dir.exists():
            return None, None
        
        pipeline = next((config_dir / p for p in 
                        ["pipeline.yaml", "pipeline.yml", "config.yaml", "config.yml"] 
                        if (config_dir / p).exists()), None)
        prompt = next((config_dir / p for p in 
                      ["prompt.txt", "prompt.md", "template.txt", "template.md"] 
                      if (config_dir / p).exists()), None)
        return pipeline, prompt
    
    @staticmethod
    def load_yaml(path: Path) -> Optional[Dict[str, Any]]:
        try:
            import yaml
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️  读取配置失败: {e}")
            return None


def get_config_files(args):
    """获取配置路径"""
    if args.pipeline:
        ConfigLoader.find_files(Path(args.pipeline)), None

    elif args.config_path:
        pipeline, prompt = ConfigLoader.find_files(Path(args.config_path))
        if pipeline:
            print(f"🔍 自动发现配置文件: {pipeline}")
        if prompt:
            print(f"🔍 自动发现配置文件: {prompt}")
            
        return pipeline, prompt
    return None, None


def validate_config(args) -> bool:
    """验证配置参数是否合法"""

    root_path = args.get("config_path", '')
    if not (root_path):
        print("🔍 --config-path 或 --pipeline 必须至少配置一个参数")
        return False
    
    
    # 可选：进一步验证配置路径是否存在
    if root_path and not os.path.exists(root_path):
        print(f"❌ 配置文件不存在: {root_path}")
        return False
    
    return True


def get_work_dir(config: ProjectInfo):
    work_dir = None    
    if config and config.work_path:  # 使用 get 避免 KeyError
        work_dir = config.work_path
    else:
        code = config.code if config else None  # 安全获取 code
        code = code or 'test'
        work_dir = f"{Path.home()}/magic/{code}"
    
    return work_dir