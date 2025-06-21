import re


def get_code_from_markdown(markdown_text, language=None):
    """
    Extract code blocks from markdown text.
    
    Args:
        markdown_text (str): Markdown text containing code blocks
        language (str, optional): Specific language to extract (e.g., 'xml', 'yaml', 'python')
    
    Returns:
        list: List of code blocks found in the markdown
    """
    if language:
        # Look for specific language code blocks
        pattern = rf'```{re.escape(language)}\n(.*?)\n```'
    else:
        # Look for any code blocks
        pattern = r'```[\w]*\n(.*?)\n```'
    
    # Use DOTALL flag to match across newlines
    matches = re.findall(pattern, markdown_text, re.DOTALL)
    
    if not matches:
        # Try without language specification
        pattern = r'```\n(.*?)\n```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)
    
    if not matches:
        # Try single backticks for inline code
        pattern = r'`([^`]+)`'
        matches = re.findall(pattern, markdown_text)
    
    return matches if matches else [markdown_text.strip()]


def extract_xml_from_response(response_text):
    """
    Specifically extract XML content from AI response.
    
    Args:
        response_text (str): Full response text from AI
    
    Returns:
        str: Extracted XML content
    """
    # Look for XML code blocks
    xml_blocks = get_code_from_markdown(response_text, 'xml')
    
    if xml_blocks:
        return xml_blocks[0]
    
    # If no code blocks, look for XML patterns
    xml_pattern = r'<\?xml.*?</[^>]+>'
    xml_match = re.search(xml_pattern, response_text, re.DOTALL)
    
    if xml_match:
        return xml_match.group(0)
    
    # Look for any content between angle brackets that might be XML
    angle_bracket_pattern = r'<[^<>]*>.*?</[^<>]*>'
    angle_match = re.search(angle_bracket_pattern, response_text, re.DOTALL)
    
    if angle_match:
        return angle_match.group(0)
    
    return response_text.strip()


def extract_yaml_from_response(response_text):
    """
    Extract YAML content from AI response.
    
    Args:
        response_text (str): Full response text from AI
    
    Returns:
        str: Extracted YAML content
    """
    yaml_blocks = get_code_from_markdown(response_text, 'yaml')
    
    if not yaml_blocks:
        yaml_blocks = get_code_from_markdown(response_text, 'yml')
    
    return yaml_blocks[0] if yaml_blocks else response_text.strip()


def extract_json_from_response(response_text):
    """
    Extract JSON content from AI response.
    
    Args:
        response_text (str): Full response text from AI
    
    Returns:
        str: Extracted JSON content
    """
    json_blocks = get_code_from_markdown(response_text, 'json')
    
    if json_blocks:
        return json_blocks[0]
    
    # Look for JSON patterns
    json_pattern = r'\{.*?\}'
    json_match = re.search(json_pattern, response_text, re.DOTALL)
    
    return json_match.group(0) if json_match else response_text.strip()


def extract_terraform_from_response(response_text):
    """
    Extract Terraform content from AI response.
    
    Args:
        response_text (str): Full response text from AI
    
    Returns:
        str: Extracted Terraform content
    """
    tf_blocks = get_code_from_markdown(response_text, 'hcl')
    
    if not tf_blocks:
        tf_blocks = get_code_from_markdown(response_text, 'terraform')
    
    return tf_blocks[0] if tf_blocks else response_text.strip()


def extract_typescript_from_response(response_text):
    """
    Extract TypeScript content from AI response.
    
    Args:
        response_text (str): Full response text from AI
    
    Returns:
        str: Extracted TypeScript content
    """
    ts_blocks = get_code_from_markdown(response_text, 'typescript')
    
    if not ts_blocks:
        ts_blocks = get_code_from_markdown(response_text, 'ts')
    
    return ts_blocks[0] if ts_blocks else response_text.strip()


def extract_python_from_response(response_text):
    """
    Extract Python content from AI response.
    
    Args:
        response_text (str): Full response text from AI
    
    Returns:
        str: Extracted Python content
    """
    py_blocks = get_code_from_markdown(response_text, 'python')
    
    if not py_blocks:
        py_blocks = get_code_from_markdown(response_text, 'py')
    
    return py_blocks[0] if py_blocks else response_text.strip()