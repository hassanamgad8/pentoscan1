import yaml
import logging
import glob
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class TemplateError(Exception):
    """Custom exception for template-related errors"""
    pass

class Template:
    def __init__(self, template_id, info, http_steps=None, javascript=None, extractors=None):
        self.id = template_id
        self.info = info
        self.http_steps = http_steps or []
        self.javascript = javascript
        self.extractors = extractors or []

def load_template(template_path):
    """
    Load a template from a YAML file.
    Returns a Template object.
    """
    try:
        with open(template_path, 'r') as f:
            spec = yaml.safe_load(f)
            
        template_id = spec.get('id')
        if not template_id:
            raise TemplateError(f"Template {template_path} missing required 'id' field")
            
        info = spec.get('info', {})
        http_steps = spec.get('http', [])
        javascript = spec.get('javascript')
        extractors = spec.get('extractors', [])
        
        return Template(
            template_id=template_id,
            info=info,
            http_steps=http_steps,
            javascript=javascript,
            extractors=extractors
        )
    except Exception as e:
        logging.error(f"Error loading template {template_path}: {str(e)}")
        return None

def load_templates(template_dir="templates"):
    """
    Load all templates from the specified directory.
    Returns a list of Template objects.
    """
    templates = []
    try:
        # Find all YAML files in the template directory
        template_files = glob.glob(f"{template_dir}/**/*.yaml", recursive=True)
        
        for template_file in template_files:
            try:
                template = load_template(template_file)
                if template:
                    templates.append(template)
            except TemplateError as e:
                logger.error(f"Error loading template {template_file}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error loading templates: {str(e)}")
        
    return templates
