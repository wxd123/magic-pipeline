#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# magic_pipeline/core/validate/project_validate.py

class ProjectConfigValidator:
    """项目配置解析器"""
    
    
    
    @classmethod
    def validate(cls, config_data: dict[str, str]) -> bool:
        """
        解析配置文件
        args:
            config_data: 传入的配置字典，包含必要的字段如 name 和 description
        Returns:
            bool: 验证结果，True 表示验证通过，False 表示验证失败
        """
        # 检查配置项是否为空
        if not config_data:
            print(f"项目配置项不存在")    
            return False   
        
        # 检查必需的 name  字段
        
        if not config_data['name'] or not config_data['name'].strip():
            print("project 配置缺少必需的 'name' 字段")  
            return False
         
        cls.print_debug_info(config_data)
        return True
    
    @classmethod
    def print_debug_info(cls, config_dict):
        """
        在控制台输出调试信息
        
        Args:
            config_dict: 配置字典
        """
        print("=" * 60)
        print("项目配置解析结果调试信息")
        print("=" * 60)
        
        for key, value in config_dict.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
        
        print("\n" + "=" * 60)
        print(f"配置项总数: {len(config_dict)}")
        print("必要字段验证:")
        print(f"  ✓ name: {config_dict.get('name')}")
        print(f"  ✓ description: {config_dict.get('description')}")
        print("=" * 60)


