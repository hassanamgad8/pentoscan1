import importlib.util
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

class ModuleError(Exception):
    """Custom exception for module-related errors"""
    pass

def load_module(module_path):
    """
    Dynamically load a Python module from file
    
    Args:
        module_path (str): Path to the Python module file
        
    Returns:
        module: Loaded module object
        
    Raises:
        ModuleError: If module cannot be loaded
    """
    try:
        # Convert to absolute path
        module_path = Path(module_path).resolve()
        
        # Check if file exists
        if not module_path.exists():
            raise ModuleError(f"Module file not found: {module_path}")
        
        # Load module
        spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
        if spec is None:
            raise ModuleError(f"Could not load module spec from {module_path}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_path.stem] = module
        spec.loader.exec_module(module)
        
        # Validate module has required interface
        if not hasattr(module, 'run'):
            raise ModuleError("Module must have a 'run' function")
        
        return module
        
    except Exception as e:
        raise ModuleError(f"Failed to load module: {str(e)}")

def run_exploit(module_path, target_url, scan_result):
    """
    Run an exploit module with the given target and scan results
    
    Args:
        module_path (str): Path to the exploit module
        target_url (str): Target URL
        scan_result (dict): Results from the scan
        
    Returns:
        dict: Results from the exploit
    """
    try:
        module = load_module(module_path)
        return module.run(target_url, scan_result)
    except ModuleError as e:
        logger.error(f"Exploit failed: {str(e)}")
        return {'success': False, 'error': str(e)} 