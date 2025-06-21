import streamlit as st
import os
import boto3
from botocore.config import Config
from PIL import Image
from utils import invoke_bedrock_agent
from utils import read_agent_response
from utils import enable_artifacts_download
from utils import retrieve_environment_variables
from utils import save_conversation
from utils import invoke_bedrock_model_streaming
from layout import create_tabs, create_option_tabs, create_reverse_option_tabs, welcome_sidebar, login_page
from styles import apply_styles
from cost_estimate_widget import generate_cost_estimates
from generate_arch_widget import generate_arch
from generate_cdk_widget import generate_cdk
from generate_cfn_widget import generate_cfn
from generate_doc_widget import generate_doc
from generate_reverse_widget import generate_reverse_arch, generate_reverse_doc
from infrastructure_parser import InfrastructureParser
import io

# Streamlit configuration 
st.set_page_config(page_title="DevGenius", layout='wide')
apply_styles()

# Initialize AWS clients
AWS_REGION = os.getenv("AWS_REGION")
config = Config(read_timeout=1000, retries=dict(max_attempts=5))
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION, config=config)
s3_client = boto3.client('s3', region_name=AWS_REGION)
sts_client = boto3.client('sts', region_name=AWS_REGION)
dynamodb_resource = boto3.resource('dynamodb', region_name=AWS_REGION)

ACCOUNT_ID = sts_client.get_caller_identity()["Account"]
# Constants
BEDROCK_MODEL_ID = f"arn:aws:bedrock:{AWS_REGION}:{ACCOUNT_ID}:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0"  # noqa
CONVERSATION_TABLE_NAME = retrieve_environment_variables("CONVERSATION_TABLE_NAME")
FEEDBACK_TABLE_NAME = retrieve_environment_variables("FEEDBACK_TABLE_NAME")
SESSION_TABLE_NAME = retrieve_environment_variables("SESSION_TABLE_NAME")
S3_BUCKET_NAME = retrieve_environment_variables("S3_BUCKET_NAME")
BEDROCK_AGENT_ID = retrieve_environment_variables("BEDROCK_AGENT_ID")
BEDROCK_AGENT_ALIAS_ID = retrieve_environment_variables("BEDROCK_AGENT_ALIAS_ID")


def display_image(image, width=600, caption="Uploaded Image", use_center=True):
    if use_center:
        # Center the image using columns
        col1, col2, col3 = st.columns([1, 2, 1])
        display_container = col2
    else:
        # Use full width container
        display_container = st

    with display_container:
        st.image(
            image,
            caption=caption,
            width=width,
            use_container_width=False,
            clamp=True  # Prevents image from being larger than its original size
        )


# # Function to interact with the Bedrock model using an image and query
# def get_image_insights(image_data, query="Explain in detail the architecture flow"):
#     query = ('''Explain in detail the architecture flow.
#              If the given image is not related to technical architecture, then please request the user to upload an AWS architecture or hand drawn architecture.
#              When generating the solution , highlight the AWS service names in bold
#              ''')  # noqa
#     messages = [{
#         "role": "user",
#         "content": [
#             {"image": {"format": "png", "source": {"bytes": image_data}}},
#             {"text": query}
#         ]}
#     ]
#     try:
#         streaming_response = bedrock_client.converse_stream(
#             modelId=BEDROCK_MODEL_ID,
#             messages=messages,
#             inferenceConfig={"maxTokens": 2000, "temperature": 0.1, "topP": 0.9}
#         )

#         full_response = ""
#         output_placeholder = st.empty()
#         for chunk in streaming_response["stream"]:
#             if "contentBlockDelta" in chunk:
#                 text = chunk["contentBlockDelta"]["delta"]["text"]
#                 full_response += text
#                 output_placeholder.markdown(f"<div class='wrapped-text'>{full_response}</div>", unsafe_allow_html=True)
#         output_placeholder.write("")

#         if 'mod_messages' not in st.session_state:
#             st.session_state.mod_messages = []
#         st.session_state.mod_messages.append({"role": "assistant", "content": full_response})
#         st.session_state.interaction.append({"type": "Architecture details", "details": full_response})
#         save_conversation(st.session_state['conversation_id'], prompt, full_response)

#     except Exception as e:
#         st.error(f"ERROR: Can't invoke '{BEDROCK_MODEL_ID}'. Reason: {e}")

def get_image_insights(image_data, query="Explain in detail the architecture flow"):
    """
    Function to interact with the Bedrock model using an image and query
    """
    try:
        # Definir el query y prompt
        analysis_prompt = '''Explain in detail the architecture flow.
             If the given image is not related to technical architecture, then please request the user to upload an AWS architecture or hand drawn architecture.
             When generating the solution, highlight the AWS service names in bold.
             '''
        
        messages = [{
            "role": "user",
            "content": [
                {"image": {"format": "png", "source": {"bytes": image_data}}},
                {"text": analysis_prompt}
            ]}
        ]
        
        # Usar modelo específico para análisis de imágenes (debe soportar multimodal)
        # El modelo de inference profile puede no soportar imágenes
        image_model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"  # Modelo que soporta imágenes
        
        streaming_response = bedrock_client.converse_stream(
            modelId=image_model_id,
            messages=messages,
            inferenceConfig={"maxTokens": 2000, "temperature": 0.1, "topP": 0.9}
        )

        full_response = ""
        output_placeholder = st.empty()
        
        for chunk in streaming_response["stream"]:
            if "contentBlockDelta" in chunk:
                text = chunk["contentBlockDelta"]["delta"]["text"]
                full_response += text
                output_placeholder.markdown(f"<div class='wrapped-text'>{full_response}</div>", unsafe_allow_html=True)
        
        output_placeholder.write("")

        # Inicializar session state si no existe
        if 'mod_messages' not in st.session_state:
            st.session_state.mod_messages = []
        
        # Agregar la respuesta a los mensajes
        st.session_state.mod_messages.append({"role": "assistant", "content": full_response})
        st.session_state.interaction.append({"type": "Architecture details", "details": full_response})
        
        # Guardar conversación con prompt correcto
        save_conversation(st.session_state['conversation_id'], analysis_prompt, full_response)
        
        return full_response

    except Exception as e:
        error_msg = f"ERROR: Can't invoke image analysis. Reason: {e}"
        st.error(error_msg)
        print(f"Image analysis error: {str(e)}")
        
        # Retornar mensaje de error en lugar de fallar
        error_response = "I'm having trouble analyzing this image. Please ensure it's a valid architecture diagram and try again."
        
        # Guardar el error también
        try:
            save_conversation(
                st.session_state['conversation_id'], 
                "Image analysis request", 
                error_response
            )
        except:
            pass  # Si save_conversation falla, no hacer nada
            
        return error_response

# Reset the chat history in session state
def reset_chat():
    # Clear specific message-related session states
    keys_to_keep = {'conversation_id', 'user_authenticated', 'user_name', 'user_email', 'cognito_authentication', 'token', 'midway_user'}  # noqa
    keys_to_remove = set(st.session_state.keys()) - keys_to_keep

    for key in keys_to_remove:
        del st.session_state[key]

    st.session_state.messages = []


# Reset the chat history in session state
def reset_messages():
    # st.session_state['conversation_id'] = str(uuid.uuid4())

    initial_question = get_initial_question(st.session_state.topic_selector)
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to DevGenius — turning ideas into reality. Together, we’ll design your architecture and solution, with each conversation shaping your vision. Let’s get started on building!"}]

    if initial_question:
        st.session_state.messages.append({"role": "user", "content": initial_question})
        response = invoke_bedrock_agent(st.session_state.conversation_id, initial_question)
        event_stream = response['completion']
        ask_user, agent_answer = read_agent_response(event_stream)
        st.session_state.messages.append({"role": "assistant", "content": agent_answer})


# Function to format assistant's response for markdown
def format_for_markdown(response_text):
    return response_text.replace("\n", "\n\n")  # Ensure proper line breaks for markdown rendering


def get_initial_question(topic):
    return {
        "Data Lake": "How can I build an enterprise data lake on AWS?",
        "Log Analytics": "How can I build a log analytics solution on AWS?"
    }.get(topic, "")


# Function to compress or resize image if it exceeds 5MB
def resize_or_compress_image(uploaded_image):
    # Open the image using PIL
    image = Image.open(uploaded_image)

    # Check the size of the uploaded image
    image_bytes = uploaded_image.getvalue()
    if len(image_bytes) > 5 * 1024 * 1024:  # 5MB in bytes
        st.write("Image size exceeds 5MB. Resizing...")

        # Resize the image (you can adjust the dimensions as needed)
        image = image.resize((800, 600))  # Example resize, you can adjust this

        # Compress the image by saving it to a BytesIO object with reduced quality
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG", quality=85)  # Adjust quality if needed
        img_byte_arr.seek(0)

        # Return the compressed image
        return img_byte_arr
    else:
        # If the image is under 5MB, no resizing is needed, just return the original
        return uploaded_image


#########################################
# Streamlit Main Execution Starts Here
#########################################
if 'user_authenticated' not in st.session_state:
    st.session_state.user_authenticated = False
if 'interaction' not in st.session_state:
    st.session_state.interaction = []

if not st.session_state.user_authenticated:
    login_page()
else:
    tabs = create_tabs()
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Build a solution"
    with st.sidebar:
        # st.title("DevGenius")
        welcome_sidebar()

    # Tab for "Generate Architecture Diagram and Solution"
    with tabs[0]:
        st.header("Generate Architecture Diagram and Solution")

        if "topic_selector" not in st.session_state:
            st.session_state.topic_selector = ""
            reset_messages()

        if st.session_state.active_tab != "Build a solution":
            print("inside tab1 active_tab:", st.session_state.active_tab)
            st.session_state.active_tab = "Build a solution"

        # col1, col2, _, _, right = st.columns(5)
        # with col1:
        #     topic = st.selectbox("Select the feature to proceed", ["","Data Lake", "Log Analytics"], key="topic_selector", on_change=reset_messages)  # noqa
        # with right:
        #     st.button('Clear Chat History', on_click=reset_messages)

        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "Welcome"}]

        # Display the conversation messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        prompt = st.chat_input(
            placeholder="Ask me about AWS architecture, costs, or infrastructure solutions...",
            key='Generate'
        )

        if prompt:

            # when the user refines the solution , reset checkbox of all tabs
            # and force user to re-check to generate updated solution
            st.session_state.cost = False
            st.session_state.arch = False
            st.session_state.cdk = False
            st.session_state.cfn = False
            st.session_state.doc = False

            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = invoke_bedrock_agent(st.session_state.conversation_id, prompt)
                    event_stream = response['completion']
                    ask_user, agent_answer = read_agent_response(event_stream)
                    st.markdown(agent_answer)

            st.session_state.messages.append({"role": "assistant", "content": agent_answer})

            # Check if we have reached the number of questions
            if not ask_user:
                st.session_state.interaction.append(
                    {"type": "Details", "details": st.session_state.messages[-1]['content']})
                devgenius_option_tabs = create_option_tabs()
                with devgenius_option_tabs[0]:
                    generate_cost_estimates(st.session_state.messages)
                with devgenius_option_tabs[1]:
                    generate_arch(st.session_state.messages)
                with devgenius_option_tabs[2]:
                    generate_cdk(st.session_state.messages)
                with devgenius_option_tabs[3]:
                    generate_cfn(st.session_state.messages)
                with devgenius_option_tabs[4]:
                    generate_doc(st.session_state.messages)
                enable_artifacts_download()

            save_conversation(st.session_state['conversation_id'], prompt, agent_answer)

    # Tab for "Generate Solution from Existing Architecture"
    with tabs[1]:
        st.header("Generate Solution from Existing Architecture")

        # Custom CSS to style the file uploader button
        st.markdown("""
            <style>
            /* Target the file uploader button */
            .stFileUploader button {
                background-color: #4CAF50; /* Green background for the button */
                color: white !important; /* White text color */
                border: none !important; /* Remove default border */
                padding: 10px 20px; /* Add padding */
                border-radius: 5px; /* Rounded corners */
                font-size: 16px; /* Font size */
                cursor: pointer; /* Pointer cursor on hover */
            }

            /* Add hover effect to make the button look more interactive */
            .stFileUploader button:hover {
                background-color: #45a049; /* Darker green when hovered */
            }
            </style>
        """, unsafe_allow_html=True)

        # File uploader and image insights logic
        uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"], on_change=reset_chat)
        if st.session_state.active_tab != "Modify your existing architecture":
            print("inside tab2 active_tab:", st.session_state.active_tab)
            # reset_chat()
            st.session_state.active_tab = "Modify your existing architecture"

        if uploaded_file:
            # write the upload file to S3 bucket
            s3_key = f"{st.session_state.conversation_id}/uploaded_file/{uploaded_file.name}"  # noqa
            # response = s3_client.put_object(Body=uploaded_file.getvalue(), Bucket=S3_BUCKET_NAME, Key=s3_key)
            # print(response)
            # st.session_state.uploaded_image = uploaded_file
            resized_image = resize_or_compress_image(uploaded_file)
            response = s3_client.put_object(Body=resized_image, Bucket=S3_BUCKET_NAME, Key=s3_key)
            st.session_state.uploaded_image = resized_image
            image = Image.open(st.session_state.uploaded_image)
            display_image(image)
            image_bytes = st.session_state.uploaded_image.getvalue()

            if 'image_insights' not in st.session_state:
                st.session_state.image_insights = get_image_insights(
                    image_data=image_bytes)

        if 'mod_messages' not in st.session_state:
            st.session_state.mod_messages = []

        if 'generate_arch_called' not in st.session_state:
            st.session_state.generate_arch_called = False

        if 'generate_cost_estimates_called' not in st.session_state:
            st.session_state.generate_cost_estimates_called = False

        if 'generate_cdk_called' not in st.session_state:
            st.session_state.generate_cdk_called = False

        if 'generate_cfn_called' not in st.session_state:
            st.session_state.generate_cfn_called = False

        if 'generate_doc_called' not in st.session_state:
            st.session_state.generate_doc_called = False

        # Display chat history
        for msg in st.session_state.mod_messages:
            if msg["role"] == "user":
                st.chat_message("user").markdown(msg["content"])
            elif msg["role"] == "assistant":
                # Format the assistant's response for markdown (ensure proper rendering)
                formatted_content = format_for_markdown(msg["content"])
                st.chat_message("assistant").markdown(formatted_content)

        # Trigger actions for generating solution
        if uploaded_file:
            devgenius_option_tabs = create_option_tabs()
            with devgenius_option_tabs[0]:
                if not st.session_state.generate_cost_estimates_called:
                    generate_cost_estimates(st.session_state.mod_messages)
                    st.session_state.generate_cost_estimates_called = True
            with devgenius_option_tabs[1]:
                if not st.session_state.generate_arch_called:
                    generate_arch(st.session_state.mod_messages)
                    st.session_state.generate_arch_called = True

            with devgenius_option_tabs[2]:
                if not st.session_state.generate_cdk_called:
                    generate_cdk(st.session_state.mod_messages)
                    st.session_state.generate_cdk_called = True

            with devgenius_option_tabs[3]:
                if not st.session_state.generate_cfn_called:
                    generate_cfn(st.session_state.mod_messages)
                    st.session_state.generate_cfn_called = True

            with devgenius_option_tabs[4]:
                if not st.session_state.generate_doc_called:
                    generate_doc(st.session_state.mod_messages)
                    st.session_state.generate_doc_called = True

            if st.session_state.interaction:
                enable_artifacts_download()

        # Handle new chat input
        if prompt := st.chat_input():
            st.session_state.generate_arch_called = False
            st.session_state.generate_cdk_called = False
            st.session_state.generate_cfn_called = False
            st.session_state.generate_cost_estimates_called = False
            st.session_state.generate_doc_called = False

            # when the user refines the solution , reset checkbox of all tabs
            # and force user to re-check to generate updated solution
            st.session_state.cost = False
            st.session_state.arch = False
            st.session_state.cdk = False
            st.session_state.cfn = False
            st.session_state.doc = False

            st.session_state.mod_messages.append({"role": "user", "content": prompt})
            st.chat_message("user").markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = invoke_bedrock_model_streaming(st.session_state.mod_messages)
                    st.session_state.interaction.append({"type": "Architecture details", "details": response})
                    st.markdown(f"<div class='wrapped-text'>{response}</div>", unsafe_allow_html=True)

            st.session_state.mod_messages.append({"role": "assistant", "content": response[0]})
            save_conversation(st.session_state['conversation_id'], prompt, response[0])
            st.rerun()

    # Tab for "Reverse Engineering" - PHASE 3 IMPLEMENTATION
    with tabs[2]:
        st.header("🔍 Reverse Engineering - Analyze Existing Infrastructure")
        
        # Display supported file types with improved styling
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
        <h4>📁 Supported File Types:</h4>
        <ul style='margin-bottom: 0;'>
            <li><strong>CloudFormation</strong>: <code>.yaml</code>, <code>.yml</code>, <code>.json</code> templates</li>
            <li><strong>CDK</strong>: <code>.ts</code>, <code>.py</code>, <code>.js</code> code files</li>
            <li><strong>Terraform</strong>: <code>.tf</code> configuration files</li>
            <li><strong>AWS CLI</strong>: <code>.txt</code> describe command outputs</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        # Custom CSS to style the file uploader button
        st.markdown("""
            <style>
            .stFileUploader button {
                background-color: #4CAF50;
                color: white !important;
                border: none !important;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .stFileUploader button:hover {
                background-color: #45a049;
            }
            .reverse-info {
                background-color: #e8f4fd;
                padding: 10px;
                border-radius: 5px;
                border-left: 4px solid #1f77b4;
                margin: 10px 0;
            }
            </style>
        """, unsafe_allow_html=True)

        # File uploader for infrastructure files
        uploaded_file = st.file_uploader(
            "📤 Choose an infrastructure file to analyze...", 
            type=["yaml", "yml", "json", "tf", "ts", "py", "js", "txt"], 
            help="Upload your CloudFormation, CDK, Terraform, or AWS CLI output files",
            on_change=reset_chat
        )
        
        # Update active tab state
        if st.session_state.active_tab != "Reverse Engineering":
            print("inside tab3 active_tab:", st.session_state.active_tab)
            st.session_state.active_tab = "Reverse Engineering"

        # Handle file upload and analysis
        if uploaded_file:
            # Upload file to S3
            s3_key = f"{st.session_state.conversation_id}/uploaded_file/{uploaded_file.name}"
            file_content = uploaded_file.getvalue()
            
            # Handle different file encodings
            try:
                if uploaded_file.type == "text/plain" or uploaded_file.name.endswith('.txt'):
                    file_content_str = file_content.decode('utf-8')
                else:
                    file_content_str = file_content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    file_content_str = file_content.decode('latin-1')
                except:
                    st.error("Unable to decode file. Please ensure the file is in a supported text format.")
                    st.stop()
            
            # Store file in S3
            try:
                response = s3_client.put_object(Body=file_content, Bucket=S3_BUCKET_NAME, Key=s3_key)
                
                # Display file upload success with details
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.success(f"✅ Successfully uploaded: **{uploaded_file.name}**")
                with col2:
                    st.info(f"📊 Size: {len(file_content):,} bytes")
                with col3:
                    st.info(f"🗂️ Type: {uploaded_file.type or 'text/plain'}")
                
            except Exception as e:
                st.error(f"Failed to upload file to S3: {str(e)}")
                st.stop()
            
            # Show file preview for small files
            if len(file_content_str) < 2000:
                with st.expander("👀 File Preview", expanded=False):
                    st.code(file_content_str[:1000] + ("..." if len(file_content_str) > 1000 else ""), 
                            language=None)
            
            # Analyze the infrastructure file
            if 'infrastructure_analysis' not in st.session_state or st.session_state.get('last_uploaded_file') != uploaded_file.name:
                st.session_state.last_uploaded_file = uploaded_file.name
                
                with st.spinner("🔍 Analyzing infrastructure configuration... This may take a moment."):
                    try:
                        # Create parser instance
                        parser = InfrastructureParser()
                        
                        # Create bedrock functions dictionary
                        bedrock_functions = {
                            'invoke_bedrock_model_streaming': invoke_bedrock_model_streaming,
                            'save_conversation': save_conversation
                        }
                        
                        # Call the analyze method
                        analysis = parser.analyze_infrastructure_file(
                            uploaded_file, 
                            file_content_str, 
                            st.session_state, 
                            bedrock_functions
                        )
                        st.session_state.infrastructure_analysis = analysis
                        
                        # Show analysis summary
                        if analysis:
                            st.markdown("""
                            <div class='reverse-info'>
                            <strong>📋 Analysis Complete!</strong><br>
                            Your infrastructure has been analyzed and is ready for diagram generation and documentation.
                            </div>
                            """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")
                        st.error("Please check your file format and try again.")
                        st.stop()

        # Initialize session state for reverse engineering
        if 'reverse_messages' not in st.session_state:
            st.session_state.reverse_messages = []

        if 'generate_reverse_arch_called' not in st.session_state:
            st.session_state.generate_reverse_arch_called = False

        if 'generate_reverse_doc_called' not in st.session_state:
            st.session_state.generate_reverse_doc_called = False

        # Display chat history (excluding the initial long analysis prompt)
        for msg in st.session_state.reverse_messages:
            if msg["role"] == "user":
                # Don't display the initial analysis prompt (too long and technical)
                if not msg["content"].startswith("Analyze the following") and len(msg["content"]) < 1000:
                    st.chat_message("user").markdown(msg["content"])
            elif msg["role"] == "assistant":
                formatted_content = format_for_markdown(msg["content"])
                st.chat_message("assistant").markdown(formatted_content)

        # Show reverse engineering options when file is uploaded and analyzed
        if uploaded_file and 'infrastructure_analysis' in st.session_state:
            st.markdown("---")
            st.markdown("### 🛠️ Generate Content from Analysis")
            
            # Create reverse engineering option tabs
            reverse_option_tabs = create_reverse_option_tabs()
            
            with reverse_option_tabs[0]:  # Architecture Diagram
                if not st.session_state.generate_reverse_arch_called:
                    generate_reverse_arch(st.session_state.reverse_messages)
                    st.session_state.generate_reverse_arch_called = True

            with reverse_option_tabs[1]:  # Technical Documentation
                if not st.session_state.generate_reverse_doc_called:
                    generate_reverse_doc(st.session_state.reverse_messages)
                    st.session_state.generate_reverse_doc_called = True

            # Enable artifacts download if interactions exist
            if st.session_state.interaction:
                st.markdown("---")
                enable_artifacts_download()

        # Handle additional chat input for refinements and questions
        if uploaded_file:
            st.markdown("---")
            st.markdown("### 💬 Ask Questions or Request Modifications")
            
            if prompt := st.chat_input(
                placeholder="Ask questions about your infrastructure or request specific analysis...",
                key="reverse_chat"
            ):
                # Reset generation flags to allow regeneration with new context
                st.session_state.generate_reverse_arch_called = False
                st.session_state.generate_reverse_doc_called = False

                # Reset checkbox states to allow user to regenerate content
                if 'reverse_arch' in st.session_state:
                    st.session_state.reverse_arch = False
                if 'reverse_doc' in st.session_state:
                    st.session_state.reverse_doc = False

                # Add user message
                st.session_state.reverse_messages.append({"role": "user", "content": prompt})
                st.chat_message("user").markdown(prompt)

                # Generate response
                with st.chat_message("assistant"):
                    with st.spinner("🤔 Analyzing your question..."):
                        try:
                            response, stop_reason = invoke_bedrock_model_streaming(st.session_state.reverse_messages)
                            st.session_state.interaction.append({
                                "type": "Infrastructure Analysis Q&A", 
                                "details": response
                            })
                            st.markdown(f"<div class='wrapped-text'>{response}</div>", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error generating response: {str(e)}")
                            st.error("Please try rephrasing your question.")
                            # Remove the user message if response failed
                            if st.session_state.reverse_messages and st.session_state.reverse_messages[-1]["role"] == "user":
                                st.session_state.reverse_messages.pop()
                            st.stop()

                # Add assistant response to conversation
                st.session_state.reverse_messages.append({"role": "assistant", "content": response})
                save_conversation(st.session_state['conversation_id'], prompt, response)
                st.rerun()
        
        # Show helpful tips when no file is uploaded
        else:
            st.markdown("""
            <div style='background-color: #fff3cd; padding: 20px; border-radius: 10px; border-left: 4px solid #ffc107;'>
            <h4>💡 Getting Started with Reverse Engineering</h4>
            <p><strong>Step 1:</strong> Upload your infrastructure file using the file uploader above</p>
            <p><strong>Step 2:</strong> Wait for the automatic analysis to complete</p>
            <p><strong>Step 3:</strong> Generate architecture diagrams and documentation</p>
            <p><strong>Step 4:</strong> Ask questions or request modifications via chat</p>
            
            <h5>📝 Example files you can upload:</h5>
            <ul>
                <li>CloudFormation templates from your AWS projects</li>
                <li>Terraform .tf files from your infrastructure</li>
                <li>CDK code files (TypeScript, Python, JavaScript)</li>
                <li>AWS CLI describe command outputs (like the infrastructure_details.txt you provided)</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)