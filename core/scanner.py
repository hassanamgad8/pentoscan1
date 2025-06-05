import re
import logging
import requests
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class ScannerError(Exception):
    """Custom exception for scanner-related errors"""
    pass

def match_response(response, matcher):
    """
    Match response content against a matcher
    
    Args:
        response (requests.Response): Response object
        matcher (dict): Matcher configuration
        
    Returns:
        bool: True if match found, False otherwise
    """
    matcher_type = matcher['type']
    
    if matcher_type == 'word':
        for word in matcher['words']:
            if word in response.text:
                return True
        return False
    
    elif matcher_type == 'status':
        return response.status_code == matcher['status']
    
    elif matcher_type == 'regex':
        pattern = re.compile(matcher['regex'])
        return bool(pattern.search(response.text))
    
    return False

def run_scan(target_url, template):
    """
    Run a scan using the provided template
    
    Args:
        target_url (str): Target URL to scan
        template (dict): Scan template
        
    Returns:
        dict: Scan results including vulnerability status
    """
    try:
        # Prepare request
        scan_config = template['scan']
        method = scan_config['method'].upper()
        path = scan_config['path']
        url = urljoin(target_url, path)
        
        # Make request
        logger.info(f"Sending {method} request to {url}")
        response = requests.request(
            method=method,
            url=url,
            timeout=10,
            verify=False  # Allow self-signed certificates
        )
        
        # Check matchers
        vulnerable = False
        for matcher in scan_config['matchers']:
            if match_response(response, matcher):
                vulnerable = True
                break
        
        # Prepare results
        result = {
            'template_id': template['id'],
            'template_name': template['name'],
            'severity': template['severity'],
            'target_url': url,
            'method': method,
            'status_code': response.status_code,
            'vulnerable': vulnerable,
            'response_length': len(response.text)
        }
        
        # Run exploit module if specified and vulnerable
        if vulnerable and 'exploit_module' in template:
            try:
                # TODO: Implement dynamic module loading
                logger.info(f"Vulnerability found, would run exploit module: {template['exploit_module']}")
            except Exception as e:
                logger.error(f"Failed to run exploit module: {str(e)}")
        
        return result
        
    except requests.RequestException as e:
        raise ScannerError(f"Request failed: {str(e)}")
    except Exception as e:
        raise ScannerError(f"Scan failed: {str(e)}")
