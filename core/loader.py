import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class TemplateError(Exception):
    """Custom exception for template-related errors"""
    pass

def load_template(template_path):
    """
    Load and validate a YAML template file
    
    Args:
        template_path (str): Path to the YAML template file
        
    Returns:
        dict: Validated template data
        
    Raises:
        TemplateError: If template is invalid or missing required fields
    """
    try:
        with open(template_path, 'r') as f:
            template = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise TemplateError(f"Invalid YAML format: {str(e)}")
    except FileNotFoundError:
        raise TemplateError(f"Template file not found: {template_path}")
    
    # Validate required fields
    required_fields = ['id', 'name', 'severity', 'scan']
    for field in required_fields:
        if field not in template:
            raise TemplateError(f"Missing required field: {field}")
    
    # Validate scan section
    scan = template['scan']
    if 'method' not in scan or 'path' not in scan:
        raise TemplateError("Scan section must contain 'method' and 'path'")
    
    # Validate matchers
    if 'matchers' not in scan:
        raise TemplateError("Scan section must contain 'matchers'")
    
    for matcher in scan['matchers']:
        if 'type' not in matcher:
            raise TemplateError("Each matcher must have a 'type'")
        
        matcher_type = matcher['type']
        if matcher_type == 'word' and 'words' not in matcher:
            raise TemplateError("Word matcher must contain 'words' list")
        elif matcher_type == 'status' and 'status' not in matcher:
            raise TemplateError("Status matcher must contain 'status' code")
        elif matcher_type == 'regex' and 'regex' not in matcher:
            raise TemplateError("Regex matcher must contain 'regex' pattern")
    
    return template
