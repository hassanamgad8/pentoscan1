import logging
import requests
import re
import json
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from typing import Dict, Any, List, Tuple
from py_mini_racer import MiniRacer

logger = logging.getLogger(__name__)

def execute_javascript(template, response):
    """Execute JavaScript code from template against response."""
    if not template.javascript:
        return None
        
    try:
        # Get raw headers as string
        raw_headers = "\r\n".join(f"{k}: {v}" for k, v in response.headers.items())
        
        # Create V8 context
        ctx = MiniRacer()
        
        # Prepare JavaScript code with headers
        js_code = f"""
        var template = {{ http_all_headers: {json.dumps(raw_headers)} }};
        {template.javascript[0]["code"]}
        """
        
        # Execute the JavaScript code
        cookie_names = ctx.eval(js_code)
        
        # Apply extractors if any
        findings = []
        if template.extractors:
            for cookie in cookie_names:
                for extractor in template.extractors:
                    if extractor["type"] == "regex":
                        for pattern in extractor["regex"]:
                            if re.match(pattern, cookie):
                                findings.append({
                                    "template_id": template.id,
                                    "cookie_name": cookie,
                                    "pattern": pattern
                                })
        
        return findings
    except Exception as e:
        logging.error(f"Error executing JavaScript: {str(e)}")
        return None

def match_response(response, matcher):
    """Match response against the given matcher."""
    if matcher["type"] == "word":
        return any(word in response.text for word in matcher["words"])
    elif matcher["type"] == "status":
        return response.status_code in matcher["status"]
    elif matcher["type"] == "regex":
        return any(re.search(pattern, response.text) for pattern in matcher["regex"])
    return False

def run_scan(target_url: str, template: Dict[str, Any]) -> Dict[str, Any]:
    """Run a scan using the provided template."""
    results = []
    
    try:
        # Handle HTTP requests
        if "http" in template:
            for http_req in template["http"]:
                method = http_req.get("method", "GET")
                paths = http_req.get("path", [])
                
                for path in paths:
                    url = urljoin(target_url, path)
                    response = requests.request(method, url)
                    
                    # Execute JavaScript if present
                    if "javascript" in template:
                        js_findings = execute_javascript(template, response)
                        if js_findings:
                            results.extend(js_findings)
                    
                    # Check matchers
                    if "matchers" in http_req:
                        for matcher in http_req["matchers"]:
                            if match_response(response, matcher):
                                results.append({
                                    "template_id": template["id"],
                                    "url": url,
                                    "status": response.status_code,
                                    "matcher": matcher
                                })
                                
    except Exception as e:
        logging.error(f"Error during scan: {str(e)}")
        
    return results
