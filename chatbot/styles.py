import streamlit as st


def apply_styles():
    """Apply custom CSS to the Streamlit app."""
    st.markdown("""
    <style>
    /* Adjust the gap between tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        display: flex;
        flex-wrap: wrap; /* Allow wrapping when space is limited */
        justify-content: space-between; /* Distribute tabs evenly */
    }
    /* Style each individual tab */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #F0F2F6; /* Light gray background */
        border-radius: 8px 8px 0 0; /* Rounded top corners */
        padding: 12px 24px; /* More padding for better spacing */
        font-size: 16px; /* Slightly larger text */
        font-weight: 600; /* Make the text semi-bold */
        text-align: center;
        transition: background-color 0.3s ease, transform 0.3s ease; /* Smooth transitions */
        cursor: pointer;
        flex: 1;  /* Make tabs grow equally */
        min-width: 0;  /* Allow tabs to shrink if needed */
        margin: 0 1px;  /* Small margin between tabs */
    }
    /* Active tab styles */
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50; /* Green background for active tab */
        color: white; /* White text for active tab */
        transform: translateY(-3px); /* Slight "lift" effect for active tab */
    }
    /* Hover effect for tabs */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #E8E8E8; /* Light hover effect */
        transform: translateY(-2px); /* Lift effect on hover */
        color: black;
    }
    /* Style for the tab list container */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: space-evenly; /* Even spacing between tabs */
        margin-bottom: 20px; /* Space between tabs and content */
        width: 100%;  /* Ensure full width */
    }
    /* Adjust the tab content area */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 20px;
        background-color: #fafafa; /* Light background for tab content */
        border-radius: 8px; /* Rounded corners for content */
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); /* Soft shadow around content */
    }
    /* Text input style */
    .stTextInput > div > input {
        background-color: #f4f4f9;  /* Light background */
        border: 2px solid #0073e6;  /* Blue border */
        border-radius: 12px;  /* Rounded corners */
        font-size: 16px;  /* Font size */
        padding: 10px 15px;  /* Padding inside input box */
        width: 100%;  /* Full width */
        box-sizing: border-box;  /* Prevent overflow issues */
    }
    .stTextInput > div > input:focus {
        outline: none;  /* Remove outline on focus */
        border-color: #005bb5;  /* Darker border on focus */
        box-shadow: 0 0 5px rgba(0, 92, 181, 0.5);  /* Focus effect */
    }
    /* Style the submit button (optional) */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border: 2px solid #4CAF50;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 14px;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #4CAF50;  /* Hover effect */
        color: white;
    }
    /* Responsive Styles: For smaller screen sizes (mobile) */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab-list"] {
            flex-direction: row; /* Keep tabs in a row, but allow wrapping */
            flex-wrap: wrap; /* Allow the tabs to wrap */
            justify-content: space-evenly; /* Distribute tabs evenly */
        }
        /* Ensure that tabs take up equal space on smaller screens */
        .stTabs [data-baseweb="tab"] {
            font-size: 14px;  /* Smaller text size */
            padding: 10px 12px;    /* Adjust padding for mobile */
            margin: 5px 0;    /* More space between tabs */
            flex-basis: 30%;  /* Allow the tabs to be more flexible */
        }
        .stTabs [data-baseweb="tab-panel"] {
            padding: 15px;    /* Adjust padding for mobile */
        }
        .stTextInput > div > input {
            font-size: 14px;  /* Smaller font size on mobile */
            padding: 8px 12px;  /* Adjust padding for mobile */
        }
        .stButton > button {
            font-size: 12px;   /* Smaller button text */
            padding: 8px 16px; /* Adjust padding for mobile */
        }
    }
/* ===== IMPROVED CHAT INPUT STYLES ===== */
    .stChatInput {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: white !important;
        padding: 15px 20px !important;
        border-top: 1px solid #e0e0e0 !important;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1) !important;
        z-index: 1000 !important;
        margin: 0 !important;
    }

    /* Ajustar margen izquierdo cuando el sidebar está visible */
    @media (min-width: 769px) {
        .stChatInput {
            margin-left: 21rem !important; /* Espacio para el sidebar */
        }
    }

    /* Cuando el sidebar está colapsado (pantalla completa) */
    .stApp[data-sidebar-state="collapsed"] .stChatInput,
    .stApp[data-sidebar-state="auto"] .stChatInput {
        margin-left: 0 !important;
    }

    /* Aumentar tamaño del textarea pero mantener proporción */
    .stChatInput > div > div > textarea {
        min-height: 50px !important;
        height: 50px !important;
        font-size: 16px !important;
        padding: 12px 16px !important;
        border-radius: 12px !important;
        border: 2px solid #ddd !important;
        resize: none !important;
        line-height: 1.4 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: #fafafa !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        flex: 1 !important;
    }

    /* Estilo cuando está enfocado */
    .stChatInput > div > div > textarea:focus {
        border-color: #4CAF50 !important;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.15) !important;
        outline: none !important;
        background-color: white !important;
    }

    /* Placeholder más visible */
    .stChatInput > div > div > textarea::placeholder {
        font-size: 16px !important;
        color: #999 !important;
        font-weight: 400 !important;
        opacity: 0.8 !important;
    }

    /* Botón de envío A LA DERECHA - Múltiples estrategias */
    .stChatInput > div > div > button {
        height: 50px !important;
        width: 50px !important;
        padding: 0 !important;
        border-radius: 12px !important;
        background-color: #4CAF50 !important;
        border: none !important;
        margin-left: auto !important; /* Empuja hacia la derecha */
        margin-right: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        flex-shrink: 0 !important;
        order: 99 !important; /* Forzar al final */
        grid-column: 2 !important; /* Para CSS Grid */
        position: relative !important;
        z-index: 10 !important;
    }

    /* Estrategia adicional: usar float si es necesario */
    .stChatInput > div > div > button {
        float: right !important;
    }

    /* Limpiar float del contenedor padre */
    .stChatInput > div > div::after {
        content: "" !important;
        display: table !important;
        clear: both !important;
    }

    .stChatInput > div > div > button:hover {
        background-color: #45a049 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3) !important;
    }

    .stChatInput > div > div > button:active {
        transform: translateY(0) !important;
    }

    /* Icono del botón de envío */
    .stChatInput > div > div > button svg {
        width: 18px !important;
        height: 18px !important;
        color: white !important;
    }

    /* Contenedor del chat input - FORZAR orden correcto */
    .stChatInput > div {
        max-width: 100% !important;
        margin: 0 !important;
        width: 100% !important;
    }

    .stChatInput > div > div {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        width: 100% !important;
        flex-direction: row !important; /* Asegurar dirección horizontal */
    }

    /* FORZAR: Textarea debe ser el primer elemento y expandirse */
    .stChatInput > div > div > textarea {
        order: 1 !important;
        flex: 1 !important; /* Toma todo el espacio disponible */
    }

    /* FORZAR: Botón debe ser el último elemento */
    .stChatInput > div > div > button {
        order: 99 !important; /* Número alto para asegurar que vaya al final */
        flex-shrink: 0 !important; /* No se encoge */
        margin-left: auto !important; /* Empuja el botón hacia la derecha */
    }

    /* Alternativa: usar CSS Grid para control absoluto */
    .stChatInput > div > div {
        display: grid !important;
        grid-template-columns: 1fr auto !important; /* Textarea toma espacio, botón tamaño fijo */
        gap: 8px !important;
        width: 100% !important;
        align-items: center !important;
    }

    /* Con Grid: textarea en primera columna */
    .stChatInput > div > div > textarea {
        grid-column: 1 !important;
    }

    /* Con Grid: botón en segunda columna */
    .stChatInput > div > div > button {
        grid-column: 2 !important;
    }

    /* Asegurar que el main content tenga espacio para el chat input fijo */
    .main .block-container {
        padding-bottom: 120px !important;
    }

    /* Específico para el contenido de chat */
    .stChatMessage {
        margin-bottom: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)


def apply_custom_styles():
    """Apply custom CSS to the Streamlit app."""
    st.markdown("""
    <style>
        /* Style the button (optional) */
        .stButton.gen-style > button {
            background-color: #0073e6;
            color: black;
            border: 2px solid #0073e6;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 2px;
            cursor: pointer;
        }
    </style>
    """, unsafe_allow_html=True)
