import uuid
import streamlit as st
from utils import BEDROCK_MODEL_ID
from utils import store_in_s3
from utils import save_conversation
from utils import collect_feedback
from utils import invoke_bedrock_model_streaming
import get_code_from_markdown
from utils import convert_xml_to_html


@st.fragment
def generate_reverse_arch(reverse_messages):
    """Generate architecture diagram from reverse engineered infrastructure"""
    
    reverse_messages = reverse_messages[:]

    # Retain messages and previous insights in the chat section
    if 'reverse_arch_messages' not in st.session_state:
        st.session_state.reverse_arch_messages = []

    # Create the radio button for architecture generation selection
    if 'reverse_arch_user_select' not in st.session_state:
        st.session_state.reverse_arch_user_select = False

    left, middle, right = st.columns([3, 1, 0.5])

    with left:
        st.markdown(
            "<div style='font-size: 18px'><b>Generate visual architecture diagram from the analyzed infrastructure</b></div>",
            unsafe_allow_html=True)
        st.divider()
        st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
        select_reverse_arch = st.checkbox(
            "Check this box to generate architecture diagram",
            key="reverse_arch"
        )
        # Only update the session state when the checkbox value changes
        if select_reverse_arch != st.session_state.reverse_arch_user_select:
            st.session_state.reverse_arch_user_select = select_reverse_arch
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        if st.session_state.reverse_arch_user_select:
            st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
            if st.button(label="⟳ Retry", key="retry-reverse-arch", type="secondary"):
                st.session_state.reverse_arch_user_select = True
            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.reverse_arch_user_select:
        # Concatenate all assistant responses for context
        concatenated_message = ' '.join(
            message['content'] for message in reverse_messages if message['role'] == 'assistant'
        )

        architecture_prompt = f"""
        Based on the infrastructure analysis provided, generate an AWS architecture diagram that visualizes the current infrastructure setup. Follow these steps:
        
        Infrastructure Analysis:
        {concatenated_message}
        
        Instructions:
        1. Create an XML file suitable for draw.io that captures the existing architecture and data flow.
        2. Use the latest AWS architecture icons from: https://aws.amazon.com/architecture/icons/
        3. Respond only with the XML in markdown format—no additional text.
        4. Ensure the XML is complete, with all elements having proper opening and closing tags.
        5. All AWS services/icons should be properly connected and enclosed within an AWS Cloud icon, deployed inside the VPC.
        6. Remove unnecessary whitespace to optimize size and minimize output tokens.
        7. Use valid AWS architecture icons to represent services, avoiding random images.
        8. Create a clearly structured and highly readable architecture diagram with proper spacing and alignment.
        9. For any on-premises connections (like VPN), use appropriate generic icons from draw.io.
        10. The diagram should accurately reflect the current state of the infrastructure as analyzed.
        11. Include network flow arrows showing data paths and connections between services.
        12. Group related services logically (e.g., by subnet, by function, etc.).
        """

        st.session_state.reverse_arch_messages.append({"role": "user", "content": architecture_prompt})
        reverse_messages.append({"role": "user", "content": architecture_prompt})

        try:
            arch_response, stop_reason = invoke_bedrock_model_streaming(reverse_messages)
            st.session_state.reverse_arch_messages.append({"role": "assistant", "content": arch_response})

            # Extract XML from markdown and convert to HTML
            arch_content_xml = get_code_from_markdown.get_code_from_markdown(arch_response, language="xml")[0]
            arch_content_html = convert_xml_to_html(arch_content_xml)

            with st.container():
                st.components.v1.html(arch_content_html, scrolling=True, height=350)

            st.session_state.interaction.append({"type": "Reverse Engineered Architecture", "details": arch_response})
            store_in_s3(content=arch_response, content_type='reverse_architecture')
            save_conversation(st.session_state['conversation_id'], architecture_prompt, arch_response)
            collect_feedback(str(uuid.uuid4()), arch_content_xml, "generate_reverse_architecture", BEDROCK_MODEL_ID)

        except Exception as e:
            st.error("Internal error occurred while generating architecture diagram. Please try again.")
            print(f"Error occurred when generating reverse architecture: {str(e)}")
            # Remove last element from list so we can retry request
            if st.session_state.reverse_arch_messages:
                del st.session_state.reverse_arch_messages[-1]
            if reverse_messages and reverse_messages[-1]["role"] == "user":
                del reverse_messages[-1]


@st.fragment
def generate_reverse_doc(reverse_messages):
    """Generate technical documentation from reverse engineered infrastructure"""
    
    reverse_messages = reverse_messages[:]

    # Retain messages and previous insights in the chat section
    if 'reverse_doc_messages' not in st.session_state:
        st.session_state.reverse_doc_messages = []

    # State management for documentation generation
    if 'reverse_doc_user_select' not in st.session_state:
        st.session_state.reverse_doc_user_select = False

    left, middle, right = st.columns([3, 1, 0.5])

    with left:
        st.markdown(
            "<div style='font-size: 18px'><b>Generate comprehensive technical documentation from the analyzed infrastructure</b></div>",
            unsafe_allow_html=True)
        st.divider()
        st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
        select_reverse_doc = st.checkbox(
            "Check this box to generate technical documentation",
            key="reverse_doc"
        )
        # Only update the session state when the checkbox value changes
        if select_reverse_doc != st.session_state.reverse_doc_user_select:
            st.session_state.reverse_doc_user_select = select_reverse_doc
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        if st.session_state.reverse_doc_user_select:
            st.markdown("<div class=stButton gen-style'>", unsafe_allow_html=True)
            if st.button(label="⟳ Retry", key="retry-reverse-doc", type="secondary"):
                st.session_state.reverse_doc_user_select = True
            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.reverse_doc_user_select:
        # Concatenate all assistant responses for context
        concatenated_message = ' '.join(
            message['content'] for message in reverse_messages if message['role'] == 'assistant'
        )

        doc_prompt = f"""
        Based on the infrastructure analysis provided, generate comprehensive technical documentation for the existing AWS infrastructure. 
        
        Infrastructure Analysis:
        {concatenated_message}
        
        Create a professional technical documentation that includes:
        
        1. **Executive Summary** - High-level overview of the infrastructure
        2. **Architecture Overview** - Description of the overall architecture design
        3. **Network Configuration** - Detailed VPC, subnet, routing, and security group configurations
        4. **Compute Resources** - EC2 instances, their purposes, and configurations
        5. **Storage Solutions** - Any storage services identified and their configurations
        6. **Database Services** - Database instances, clusters, and their configurations
        7. **Security Implementation** - Security groups, NACLs, IAM roles, and security best practices
        8. **Connectivity** - VPN connections, internet gateways, NAT gateways
        9. **Monitoring and Logging** - Any monitoring or logging solutions identified
        10. **Cost Optimization Opportunities** - Recommendations for cost optimization
        11. **Security Recommendations** - Security improvements and best practices
        12. **Operational Considerations** - Backup strategies, disaster recovery, maintenance
        13. **Compliance and Governance** - Tagging strategies and compliance considerations
        14. **Migration Recommendations** - If applicable, modernization opportunities
        15. **Appendices** - Technical specifications, configuration details, and reference materials
        
        Make sure the documentation is:
        - Professional and well-structured
        - Technically accurate based on the analysis
        - Includes specific configuration details where available
        - Provides actionable recommendations
        - Follows AWS documentation standards
        """

        st.session_state.reverse_doc_messages.append({"role": "user", "content": doc_prompt})
        reverse_messages.append({"role": "user", "content": doc_prompt})

        doc_response, stop_reason = invoke_bedrock_model_streaming(reverse_messages)
        st.session_state.reverse_doc_messages.append({"role": "assistant", "content": doc_response})

        with st.container(height=350):
            st.markdown(doc_response)

        st.session_state.interaction.append({"type": "Reverse Engineering Documentation", "details": doc_response})
        store_in_s3(content=doc_response, content_type='reverse_documentation')
        save_conversation(st.session_state['conversation_id'], doc_prompt, doc_response)
        collect_feedback(str(uuid.uuid4()), doc_response, "generate_reverse_documentation", BEDROCK_MODEL_ID)