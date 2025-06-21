import json
import yaml
import re
import streamlit as st
from typing import Dict, Any, List, Tuple


class InfrastructureParser:
    """
    Parser for different infrastructure file formats including CloudFormation, 
    CDK, Terraform, and AWS CLI outputs.
    """
    
    def __init__(self):
        self.supported_extensions = {
            '.yaml': 'yaml',
            '.yml': 'yaml', 
            '.json': 'json',
            '.tf': 'terraform',
            '.ts': 'typescript',
            '.py': 'python',
            '.js': 'javascript',
            '.txt': 'text'
        }
    
    def detect_file_type(self, content: str, filename: str) -> str:
        """
        Detect the type of infrastructure file based on content and filename.
        
        Args:
            content: File content as string
            filename: Name of the uploaded file
            
        Returns:
            Detected file type as string
        """
        # Get file extension
        extension = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        # Check content patterns for better detection
        if self._is_cloudformation(content):
            return 'cloudformation'
        elif self._is_terraform(content):
            return 'terraform'
        elif self._is_cdk(content, extension):
            return 'cdk'
        elif self._is_aws_cli_output(content):
            return 'aws_cli_output'
        elif extension in ['.yaml', '.yml']:
            return 'yaml'
        elif extension == '.json':
            return 'json'
        else:
            return 'text'
    
    def _is_cloudformation(self, content: str) -> bool:
        """Check if content is a CloudFormation template."""
        cf_indicators = [
            'AWSTemplateFormatVersion',
            'Resources:',
            'Parameters:',
            'Outputs:',
            'Mappings:',
            'Conditions:',
            'Transform:',
            'AWS::',
            '"AWSTemplateFormatVersion"',
            '"Resources"'
        ]
        return any(indicator in content for indicator in cf_indicators)
    
    def _is_terraform(self, content: str) -> bool:
        """Check if content is a Terraform file."""
        tf_indicators = [
            'resource "aws_',
            'provider "aws"',
            'terraform {',
            'variable "',
            'output "',
            'data "aws_',
            'locals {',
            'module "'
        ]
        return any(indicator in content for indicator in tf_indicators)
    
    def _is_cdk(self, content: str, extension: str) -> bool:
        """Check if content is a CDK file."""
        cdk_indicators = [
            '@aws-cdk/',
            'aws-cdk-lib',
            'import * as cdk',
            'from aws_cdk',
            'import aws_cdk',
            'Stack',
            'Construct',
            'new cdk.',
            'class.*Stack.*cdk.Stack'
        ]
        is_code_file = extension in ['.ts', '.js', '.py']
        has_cdk_content = any(indicator in content for indicator in cdk_indicators)
        return is_code_file and has_cdk_content
    
    def _is_aws_cli_output(self, content: str) -> bool:
        """Check if content is AWS CLI output."""
        cli_indicators = [
            'VPCS\t',
            'SUBNETS\t',
            'INSTANCES\t',
            'SECURITYGROUPS\t',
            'ROUTETABLES\t',
            'INTERNETGATEWAYS\t',
            'NATGATEWAYS\t',
            'LOADBALANCERS\t',
            'VPNCONNECTIONS\t',
            'ADDRESSES\t',
            'CLUSTERS\t'
        ]
        return any(indicator in content for indicator in cli_indicators)
    
    def parse_content(self, content: str, filename: str) -> Dict[str, Any]:
        """
        Parse infrastructure file content and extract relevant information.
        
        Args:
            content: File content as string
            filename: Name of the uploaded file
            
        Returns:
            Dictionary containing parsed information
        """
        file_type = self.detect_file_type(content, filename)
        
        result = {
            'file_type': file_type,
            'filename': filename,
            'content': content,
            'parsed_data': {},
            'analysis_summary': '',
            'aws_services': [],
            'security_groups': [],
            'subnets': [],
            'resources': []
        }
        
        try:
            if file_type == 'cloudformation':
                result = self._parse_cloudformation(content, result)
            elif file_type == 'terraform':
                result = self._parse_terraform(content, result)
            elif file_type == 'cdk':
                result = self._parse_cdk(content, result)
            elif file_type == 'aws_cli_output':
                result = self._parse_aws_cli_output(content, result)
            elif file_type in ['yaml', 'yml']:
                result = self._parse_yaml(content, result)
            elif file_type == 'json':
                result = self._parse_json(content, result)
            else:
                result = self._parse_text(content, result)
                
        except Exception as e:
            st.error(f"Error parsing file: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def _parse_cloudformation(self, content: str, result: Dict) -> Dict:
        """Parse CloudFormation template."""
        try:
            # Try parsing as YAML first, then JSON
            try:
                parsed = yaml.safe_load(content)
            except:
                parsed = json.loads(content)
            
            result['parsed_data'] = parsed
            
            # Extract resources
            if 'Resources' in parsed:
                resources = parsed['Resources']
                result['resources'] = list(resources.keys())
                
                # Extract AWS services
                aws_services = set()
                for resource_name, resource_config in resources.items():
                    resource_type = resource_config.get('Type', '')
                    if resource_type.startswith('AWS::'):
                        service = resource_type.split('::')[1]
                        aws_services.add(service)
                
                result['aws_services'] = list(aws_services)
            
            # Extract parameters, outputs, etc.
            result['parameters'] = list(parsed.get('Parameters', {}).keys())
            result['outputs'] = list(parsed.get('Outputs', {}).keys())
            
            result['analysis_summary'] = f"CloudFormation template with {len(result['resources'])} resources using {len(result['aws_services'])} AWS services"
            
        except Exception as e:
            result['error'] = f"Failed to parse CloudFormation: {str(e)}"
        
        return result
    
    def _parse_terraform(self, content: str, result: Dict) -> Dict:
        """Parse Terraform configuration."""
        # Extract resource blocks
        resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"'
        resources = re.findall(resource_pattern, content)
        
        result['resources'] = [f"{r[0]}.{r[1]}" for r in resources]
        
        # Extract AWS services from resources
        aws_services = set()
        for resource_type, _ in resources:
            if resource_type.startswith('aws_'):
                service = resource_type.replace('aws_', '').split('_')[0]
                aws_services.add(service)
        
        result['aws_services'] = list(aws_services)
        
        # Extract variables and outputs
        var_pattern = r'variable\s+"([^"]+)"'
        output_pattern = r'output\s+"([^"]+)"'
        
        result['variables'] = re.findall(var_pattern, content)
        result['outputs'] = re.findall(output_pattern, content)
        
        result['analysis_summary'] = f"Terraform configuration with {len(result['resources'])} resources using {len(result['aws_services'])} AWS services"
        
        return result
    
    def _parse_cdk(self, content: str, result: Dict) -> Dict:
        """Parse CDK code."""
        # Look for CDK constructs
        construct_patterns = [
            r'new\s+aws-\w+\.(\w+)',  # TypeScript/JavaScript
            r'aws_\w+\.(\w+)\(',      # Python
        ]
        
        constructs = []
        for pattern in construct_patterns:
            constructs.extend(re.findall(pattern, content))
        
        result['constructs'] = constructs
        
        # Extract AWS services from constructs
        aws_services = set()
        for construct in constructs:
            # Map common CDK constructs to services
            service_mapping = {
                'Bucket': 's3',
                'Function': 'lambda',
                'Table': 'dynamodb',
                'Vpc': 'ec2',
                'Instance': 'ec2',
                'Cluster': 'ecs',
                'LoadBalancer': 'elbv2'
            }
            
            for construct_type, service in service_mapping.items():
                if construct_type.lower() in construct.lower():
                    aws_services.add(service)
        
        result['aws_services'] = list(aws_services)
        result['analysis_summary'] = f"CDK code with {len(constructs)} constructs using {len(result['aws_services'])} AWS services"
        
        return result
    
    def _parse_aws_cli_output(self, content: str, result: Dict) -> Dict:
        """Parse AWS CLI describe output."""
        lines = content.strip().split('\n')
        
        # Parse tabular CLI output
        services = set()
        resources = []
        security_groups = []
        subnets = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Detect section headers
            if line.startswith('=== ') and line.endswith(' ==='):
                current_section = line.replace('=== ', '').replace(' ===', '').lower()
                continue
            
            # Skip empty lines
            if not line:
                continue
            
            # Parse based on current section
            if current_section:
                if 'vpc' in current_section:
                    services.add('VPC')
                elif 'subnet' in current_section:
                    services.add('VPC')
                    if line.startswith('SUBNETS'):
                        parts = line.split('\t')
                        if len(parts) > 10:
                            subnet_id = parts[12] if len(parts) > 12 else 'unknown'
                            cidr = parts[5] if len(parts) > 5 else 'unknown'
                            subnets.append({'id': subnet_id, 'cidr': cidr})
                elif 'security' in current_section:
                    services.add('EC2')
                    if line.startswith('SECURITYGROUPS'):
                        parts = line.split('\t')
                        if len(parts) > 2:
                            sg_id = parts[1] if len(parts) > 1 else 'unknown'
                            sg_name = parts[2] if len(parts) > 2 else 'unknown'
                            security_groups.append({'id': sg_id, 'name': sg_name})
                elif 'ec2' in current_section or 'instance' in current_section:
                    services.add('EC2')
                elif 'rds' in current_section or 'redshift' in current_section:
                    services.add('RDS' if 'rds' in current_section else 'Redshift')
                elif 'internet' in current_section:
                    services.add('Internet Gateway')
                elif 'nat' in current_section:
                    services.add('NAT Gateway')
                elif 'vpn' in current_section:
                    services.add('VPN')
                elif 'route' in current_section:
                    services.add('Route Tables')
                elif 'elastic' in current_section:
                    services.add('Elastic IP')
        
        result['aws_services'] = list(services)
        result['security_groups'] = security_groups
        result['subnets'] = subnets
        result['resources'] = [f"{service} resources" for service in services]
        
        result['analysis_summary'] = f"AWS CLI output showing {len(services)} AWS services with detailed configuration"
        
        return result
    
    def _parse_yaml(self, content: str, result: Dict) -> Dict:
        """Parse generic YAML file."""
        try:
            parsed = yaml.safe_load(content)
            result['parsed_data'] = parsed
            result['analysis_summary'] = "YAML configuration file"
        except Exception as e:
            result['error'] = f"Failed to parse YAML: {str(e)}"
        
        return result
    
    def _parse_json(self, content: str, result: Dict) -> Dict:
        """Parse generic JSON file."""
        try:
            parsed = json.loads(content)
            result['parsed_data'] = parsed
            result['analysis_summary'] = "JSON configuration file"
        except Exception as e:
            result['error'] = f"Failed to parse JSON: {str(e)}"
        
        return result
    
    def _parse_text(self, content: str, result: Dict) -> Dict:
        """Parse generic text file."""
        result['analysis_summary'] = f"Text file with {len(content.split())} words"
        return result
    
    def generate_analysis_prompt(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate a specialized prompt for infrastructure analysis based on parsed data.
        
        Args:
            parsed_data: Dictionary containing parsed infrastructure data
            
        Returns:
            Formatted prompt string for AI analysis
        """
        file_type = parsed_data.get('file_type', 'unknown')
        content = parsed_data.get('content', '')
        
        base_prompt = f"""
        Analyze the following {file_type} infrastructure configuration and provide a comprehensive assessment:

        File Type: {file_type}
        Content:
        ```
        {content}
        ```
        """
        
        if file_type == 'aws_cli_output':
            base_prompt += """
            This is AWS CLI output showing the current state of AWS infrastructure. Please provide:
            
            1. **Infrastructure Overview**: Summarize the overall architecture
            2. **Network Architecture**: Analyze VPC, subnets, routing, and connectivity
            3. **Security Analysis**: Review security groups, NACLs, and access patterns
            4. **Resource Inventory**: List all AWS resources and their configurations
            5. **Cost Implications**: Estimate costs and identify optimization opportunities
            6. **Security Recommendations**: Suggest security improvements
            7. **Architecture Best Practices**: Compare against AWS Well-Architected principles
            8. **Operational Considerations**: Backup, monitoring, and maintenance recommendations
            
            Focus on:
            - Current resource configurations and relationships
            - Security posture and potential vulnerabilities
            - Cost optimization opportunities
            - Compliance with AWS best practices
            - Migration and modernization recommendations
            """
        
        elif file_type == 'cloudformation':
            base_prompt += """
            This is a CloudFormation template. Please provide:
            
            1. **Template Analysis**: Overview of the template structure and purpose
            2. **Resource Dependencies**: Map resource relationships and dependencies  
            3. **Security Configuration**: Analyze IAM roles, security groups, and encryption
            4. **Best Practices Review**: Compare against CloudFormation best practices
            5. **Cost Estimation**: Estimate deployment costs
            6. **Improvement Recommendations**: Suggest optimizations and enhancements
            """
            
        elif file_type == 'terraform':
            base_prompt += """
            This is a Terraform configuration. Please provide:
            
            1. **Configuration Analysis**: Overview of the Terraform setup
            2. **Resource Mapping**: List all resources and their relationships
            3. **State Management**: Comment on state management approach
            4. **Security Review**: Analyze security configurations
            5. **Best Practices**: Compare against Terraform and AWS best practices
            6. **Optimization Suggestions**: Recommend improvements
            """
            
        elif file_type == 'cdk':
            base_prompt += """
            This is AWS CDK code. Please provide:
            
            1. **Code Analysis**: Overview of the CDK implementation
            2. **Construct Usage**: Analyze CDK constructs and patterns used
            3. **Architecture Design**: Describe the resulting AWS architecture
            4. **Best Practices**: Compare against CDK and AWS best practices
            5. **Code Quality**: Suggest code improvements and optimizations
            6. **Deployment Considerations**: Discuss deployment strategies
            """
        
        base_prompt += """
        
        Please be specific about AWS services, configurations, and provide actionable recommendations.
        Highlight any security concerns, cost optimization opportunities, and compliance considerations.
        Format your response with clear sections and bullet points for easy reading.
        """
        
        return base_prompt
    
    # Function to analyze infrastructure files
    def analyze_infrastructure_file(uploaded_file, file_content):
        """Analyze uploaded infrastructure file and generate insights"""
        parser = InfrastructureParser()
        
        # Parse the file content
        parsed_data = parser.parse_content(file_content, uploaded_file.name)
        
        # Generate specialized prompt for analysis
        analysis_prompt = parser.generate_analysis_prompt(parsed_data)
        
        # Initialize messages if not exists
        if 'reverse_messages' not in st.session_state:
            st.session_state.reverse_messages = []
        
        # Add the analysis prompt to messages
        st.session_state.reverse_messages.append({"role": "user", "content": analysis_prompt})
        
        # Get analysis from Bedrock
        try:
            response, stop_reason = invoke_bedrock_model_streaming(st.session_state.reverse_messages)
            
            # Add response to messages
            st.session_state.reverse_messages.append({"role": "assistant", "content": response})
            
            # Store interaction
            st.session_state.interaction.append({"type": "Infrastructure Analysis", "details": response})
            
            # Save conversation
            save_conversation(st.session_state.conversation_id, f"Infrastructure analysis for {uploaded_file.name}", response)
            
            return response
            
        except Exception as e:
            st.error(f"Error calling Bedrock model: {str(e)}")
            # Remove the failed prompt from messages
            if st.session_state.reverse_messages and st.session_state.reverse_messages[-1]["role"] == "user":
                st.session_state.reverse_messages.pop()
            raise e

    def analyze_infrastructure_file(self, uploaded_file, file_content, session_state, bedrock_functions):
        """
        Analyze uploaded infrastructure file and generate insights using Bedrock
        
        Args:
            uploaded_file: Streamlit uploaded file object
            file_content: String content of the file
            session_state: Streamlit session state object
            bedrock_functions: Dictionary containing Bedrock-related functions
            
        Returns:
            String response from AI analysis
        """
        import streamlit as st
        
        # Parse the file content
        parsed_data = self.parse_content(file_content, uploaded_file.name)
        
        # Generate specialized prompt for analysis
        analysis_prompt = self.generate_analysis_prompt(parsed_data)
        
        # Initialize messages if not exists
        if 'reverse_messages' not in session_state:
            session_state.reverse_messages = []
        
        # Add the analysis prompt to messages
        session_state.reverse_messages.append({"role": "user", "content": analysis_prompt})
        
        # Get analysis from Bedrock
        try:
            response, stop_reason = bedrock_functions['invoke_bedrock_model_streaming'](
                session_state.reverse_messages
            )
            
            # Add response to messages
            session_state.reverse_messages.append({"role": "assistant", "content": response})
            
            # Store interaction
            session_state.interaction.append({"type": "Infrastructure Analysis", "details": response})
            
            # Save conversation
            bedrock_functions['save_conversation'](
                session_state.conversation_id, 
                f"Infrastructure analysis for {uploaded_file.name}", 
                response
            )
            
            return response
            
        except Exception as e:
            st.error(f"Error calling Bedrock model: {str(e)}")
            # Remove the failed prompt from messages
            if session_state.reverse_messages and session_state.reverse_messages[-1]["role"] == "user":
                session_state.reverse_messages.pop()
            raise e        