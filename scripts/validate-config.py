#!/usr/bin/env python3
"""
Configuration Validator for Multi-Agent Pipeline
Validates .github/configs/agents.yaml and checks agent directories
"""

import yaml
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

class ConfigValidator:
    def __init__(self, config_path: str = ".github/configs/agents.yaml"):
        self.config_path = config_path
        self.errors = []
        self.warnings = []
        self.config = None
        
    def load_config(self) -> bool:
        """Load and parse YAML configuration"""
        try:
            if not os.path.exists(self.config_path):
                self.errors.append(f"Configuration file not found: {self.config_path}")
                return False
                
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            return True
        except yaml.YAMLError as e:
            self.errors.append(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error loading config: {e}")
            return False
    
    def validate_structure(self) -> None:
        """Validate basic configuration structure"""
        required_sections = ['agents', 'global', 'environments', 'labels']
        
        for section in required_sections:
            if section not in self.config:
                self.errors.append(f"Missing required section: {section}")
        
        # Validate agents section
        if 'agents' in self.config:
            if not isinstance(self.config['agents'], list):
                self.errors.append("'agents' must be a list")
            elif len(self.config['agents']) == 0:
                self.warnings.append("No agents configured")
    
    def validate_agents(self) -> None:
        """Validate each agent configuration"""
        if 'agents' not in self.config:
            return
            
        required_agent_fields = ['name', 'service', 'port', 'description', 'resources']
        required_resource_fields = ['cpu', 'memory', 'min_instances', 'max_instances', 'concurrency']
        
        agent_names = set()
        agent_services = set()
        agent_ports = set()
        
        for i, agent in enumerate(self.config['agents']):
            prefix = f"Agent {i+1}"
            
            # Check required fields
            for field in required_agent_fields:
                if field not in agent:
                    self.errors.append(f"{prefix}: Missing required field '{field}'")
            
            if 'name' in agent:
                # Check for duplicates
                if agent['name'] in agent_names:
                    self.errors.append(f"{prefix}: Duplicate agent name '{agent['name']}'")
                agent_names.add(agent['name'])
                
                # Check agent directory exists
                agent_dir = f"agents/{agent['name']}"
                if not os.path.exists(agent_dir):
                    self.errors.append(f"{prefix}: Agent directory not found: {agent_dir}")
                else:
                    # Check for Dockerfile
                    dockerfile_path = f"{agent_dir}/Dockerfile"
                    if not os.path.exists(dockerfile_path):
                        self.errors.append(f"{prefix}: Dockerfile not found: {dockerfile_path}")
                    
                    # Check for requirements.txt
                    requirements_path = f"{agent_dir}/requirements.txt"
                    if not os.path.exists(requirements_path):
                        self.warnings.append(f"{prefix}: requirements.txt not found: {requirements_path}")
            
            if 'service' in agent:
                if agent['service'] in agent_services:
                    self.errors.append(f"{prefix}: Duplicate service name '{agent['service']}'")
                agent_services.add(agent['service'])
            
            if 'port' in agent:
                if agent['port'] in agent_ports:
                    self.errors.append(f"{prefix}: Duplicate port '{agent['port']}'")
                agent_ports.add(agent['port'])
                
                # Validate port range
                try:
                    port = int(agent['port'])
                    if port < 1024 or port > 65535:
                        self.warnings.append(f"{prefix}: Port {port} outside recommended range (1024-65535)")
                except (ValueError, TypeError):
                    self.errors.append(f"{prefix}: Invalid port value '{agent['port']}'")
            
            # Validate resources - only prod required now
            if 'resources' in agent:
                if 'prod' not in agent['resources']:
                    self.errors.append(f"{prefix}: Missing 'prod' environment in resources")
                else:
                    prod_resources = agent['resources']['prod']
                    for field in required_resource_fields:
                        if field not in prod_resources:
                            self.errors.append(f"{prefix}: Missing resource field '{field}' for prod environment")
                    
                    # Validate resource values
                    self._validate_resource_values(f"{prefix} (prod)", prod_resources)
    
    def _validate_resource_values(self, prefix: str, resources: Dict[str, Any]) -> None:
        """Validate individual resource values"""
        
        # CPU validation
        if 'cpu' in resources:
            cpu = resources['cpu']
            if isinstance(cpu, str):
                try:
                    cpu_float = float(cpu)
                    if cpu_float <= 0 or cpu_float > 8:
                        self.warnings.append(f"{prefix}: CPU {cpu} outside recommended range (0.1-8)")
                except ValueError:
                    self.errors.append(f"{prefix}: Invalid CPU value '{cpu}'")
        
        # Memory validation
        if 'memory' in resources:
            memory = resources['memory']
            if isinstance(memory, str):
                if not memory.endswith(('Mi', 'Gi')):
                    self.warnings.append(f"{prefix}: Memory {memory} should end with 'Mi' or 'Gi'")
        
        # Instance validation
        for field in ['min_instances', 'max_instances', 'concurrency']:
            if field in resources:
                try:
                    value = int(resources[field])
                    if value < 0:
                        self.errors.append(f"{prefix}: {field} cannot be negative")
                    elif field == 'max_instances' and value > 100:
                        self.warnings.append(f"{prefix}: {field} {value} is very high, consider costs")
                    elif field == 'concurrency' and value > 1000:
                        self.warnings.append(f"{prefix}: {field} {value} is very high")
                except (ValueError, TypeError):
                    self.errors.append(f"{prefix}: Invalid {field} value '{resources[field]}'")
        
        # Instance relationship validation
        if 'min_instances' in resources and 'max_instances' in resources:
            try:
                min_inst = int(resources['min_instances'])
                max_inst = int(resources['max_instances'])
                if min_inst > max_inst:
                    self.errors.append(f"{prefix}: min_instances ({min_inst}) > max_instances ({max_inst})")
            except (ValueError, TypeError):
                pass  # Already caught above
    
    def validate_global_config(self) -> None:
        """Validate global configuration"""
        if 'global' not in self.config:
            return
            
        global_config = self.config['global']
        
        # Validate timeout
        if 'timeout' in global_config:
            try:
                timeout = int(global_config['timeout'])
                if timeout < 1 or timeout > 3600:
                    self.warnings.append(f"Timeout {timeout} outside recommended range (1-3600 seconds)")
            except (ValueError, TypeError):
                self.errors.append(f"Invalid timeout value: {global_config['timeout']}")
        
        # Validate execution environment
        if 'execution_environment' in global_config:
            valid_envs = ['gen1', 'gen2']
            if global_config['execution_environment'] not in valid_envs:
                self.errors.append(f"Invalid execution_environment. Must be one of: {valid_envs}")
    
    def check_agent_directories(self) -> None:
        """Check for agent directories without configuration"""
        agents_dir = "agents"
        if not os.path.exists(agents_dir):
            self.warnings.append(f"Agents directory not found: {agents_dir}")
            return
        
        configured_agents = set()
        if self.config and 'agents' in self.config:
            configured_agents = {agent['name'] for agent in self.config['agents']}
        
        # Find directories in agents/
        for item in os.listdir(agents_dir):
            item_path = os.path.join(agents_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                if item not in configured_agents:
                    self.warnings.append(f"Agent directory '{item}' exists but not configured in agents.yaml")
    
    def validate(self) -> bool:
        """Run all validations"""
        print(f"Validating configuration: {self.config_path}")
        
        if not self.load_config():
            return False
        
        self.validate_structure()
        self.validate_global_config()
        self.validate_agents()
        self.check_agent_directories()
        
        return len(self.errors) == 0
    
    def print_results(self) -> None:
        """Print validation results"""
        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print("\nWARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\nConfiguration is valid!")
        elif not self.errors:
            print(f"\nConfiguration is valid with {len(self.warnings)} warnings")
        else:
            print(f"\nConfiguration has {len(self.errors)} errors and {len(self.warnings)} warnings")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate agents configuration")
    parser.add_argument("--config", default=".github/configs/agents.yaml", 
                       help="Path to agents.yaml config file")
    parser.add_argument("--json", action="store_true",
                       help="Output results in JSON format")
    
    args = parser.parse_args()
    
    validator = ConfigValidator(args.config)
    is_valid = validator.validate()
    
    if args.json:
        result = {
            "valid": is_valid,
            "errors": validator.errors,
            "warnings": validator.warnings,
            "config_path": args.config
        }
        print(json.dumps(result, indent=2))
    else:
        validator.print_results()
    
    return 0 if is_valid else 1

if __name__ == "__main__":
    sys.exit(main())