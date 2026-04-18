import streamlit as st
from core.extractor import extract_document_context
from core.agent import build_agent, stream_agent_response
from core.guardrails import check_scope, apply_guardrails
from utils.helpers import validate_uploaded_file, format_file_size
from utils.logger import logger
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(
    page_title="AI Financial Assistant",
    page_icon="🤖",
    layout="wide",          
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .document-panel {
            background: white;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            max-height: 500px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }
        .panel-dots {
            display: flex;
            gap: 6px;
            margin-bottom: 12px;
        }
        .dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        .dot-red    { background: #ff5f57; }
        .dot-yellow { background: #ffbd2e; }
        .dot-green  { background: #28c840; }

        /* Chat message styling */
        .chat-message {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin: 10px 0;
        }

        /* Warning box for guardrail alerts */
        .warning-box {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 10px 14px;
            margin-top: 8px;
            font-size: 13px;
        }

        /* Verified badge */
        .verified-badge {
            background: #d4edda;
            border: 1px solid #28a745;
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 12px;
            color: #155724;
            margin-top: 6px;
            display: inline-block;
        }
    </style>
    """, unsafe_allow_html= True
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "document_context" not in st.session_state:
    st.session_state.document_context = ""

if "agent" not in st.session_state:
    st.session_state.agent = None

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = ""

if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

with st.sidebar:
    st.markdown("## 🤖 AI Financial Assistant")
    st.markdown("Upload a financial document and ask questions about it.")
    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Statement or Invoice",
        type=["pdf", "png", "jpg", "jpeg", "webp"],
        help="Supported: PDF, PNG, JPG, WEBP — Max 10MB"
    )
    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.uploaded_filename:
            is_valid, error_msg = validate_uploaded_file(uploaded_file)
            if not is_valid:
                st.error(f" {error_msg}")
            else:
                with st.spinner("📄 Extracting document content..."):
                    try:
                        context = extract_document_context(uploaded_file)
                        agent = build_agent(context)
                        st.session_state.document_context = context
                        st.session_state.agent = agent
                        st.session_state.uploaded_filename = uploaded_file.name
                        st.session_state.file_processed = True
                        st.session_state.chat_history = []
                        logger.info(f"Document processed: {uploaded_file.name}")
                    except Exception as e:
                        st.error(f" Error processing file: {str(e)}")
                        logger.error(f"File processing error: {str(e)}", exc_info=True)

if st.session_state.file_processed:
    st.success(f" {st.session_state.uploaded_filename}")
    st.caption(
            f"Context length: "
            f"{len(st.session_state.document_context):,} characters"
        )
    st.divider()
    if st.button(" Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

        # Clear document button
    if st.button(" Upload New Document", use_container_width=True):
        st.session_state.document_context = ""
        st.session_state.agent = None
        st.session_state.uploaded_filename = ""
        st.session_state.file_processed = False
        st.session_state.chat_history = []
        st.rerun()

st.markdown("##  Financial Document Assistant")
col_doc, col_chat = st.columns([1, 1], gap="large")
with col_doc:
    st.markdown("### 📄 Document")

    if st.session_state.file_processed:
        st.markdown("""
        <div class="panel-dots">
            <div class="dot dot-red"></div>
            <div class="dot dot-yellow"></div>
            <div class="dot dot-green"></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(
            f'<div class="document-panel">'
            f'{st.session_state.document_context.replace(chr(10), "<br>")}'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        # Placeholder when no document uploaded
        st.info("👆 Upload a financial document from the sidebar to get started.")


with col_chat:
    st.markdown("### 💬 Ask Questions")

    if not st.session_state.file_processed:
        st.info("Upload a document first to start chatting.")

    else:
        # ── Chat History Display ──────────────
        chat_container = st.container(height=400)

        with chat_container:
            if not st.session_state.chat_history:
                st.markdown(
                    "👋 Document loaded! Ask me anything about your statement."
                )

            for message in st.session_state.chat_history:
                with st.chat_message(message["role"],
                                     avatar="🧑" if message["role"] == "user" else "🤖"):
                    st.markdown(message["content"])

                    # Show guardrail warnings if stored
                    if message["role"] == "assistant" and message.get("warnings"):
                        for warning in message["warnings"]:
                            st.markdown(
                                f'<div class="warning-box">{warning}</div>',
                                unsafe_allow_html=True
                            )

                    # Show verified badge
                    if message["role"] == "assistant" and message.get("math_verified"):
                        st.markdown(
                            '<div class="verified-badge">✅ Amounts verified</div>',
                            unsafe_allow_html=True
                        )
            # ── Chat Input ────────────────────────
        user_input = st.chat_input(
            "Ask about your financial document...",
            key="chat_input"
        )

        if user_input:

            # Step 1: Scope check (Phase 4)
            in_scope, rejection_msg = check_scope(user_input)

            if not in_scope:
                # Show rejection without calling LLM
                with chat_container:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(rejection_msg)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": rejection_msg,
                    "warnings": [],
                    "math_verified": False
                })

            else:
                # Step 2: Add user message to history + display it
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input
                })

                with chat_container:
                    with st.chat_message("user", avatar="🧑"):
                        st.markdown(user_input)

                # Step 3: Build LangChain message history for agent
                # Convert our dict history to LangChain message objects
                lc_history = []
                for msg in st.session_state.chat_history[:-1]:
                    if msg["role"] == "user":
                        lc_history.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        lc_history.append(AIMessage(content=msg["content"]))

                # Step 4: Stream response (Phase 2 + Phase 3)
                with chat_container:
                    with st.chat_message("assistant", avatar="🤖"):
                        # st.write_stream consumes our generator
                        full_response = st.write_stream(
                            stream_agent_response(
                                st.session_state.agent,
                                user_input,
                                lc_history
                            )
                        )

                # Step 5: Apply guardrails to completed response (Phase 4)
                guardrail_result = apply_guardrails(
                    full_response,
                    st.session_state.document_context,
                    user_input
                )

                # Step 6: Show warnings if any
                if guardrail_result["warnings"]:
                    with chat_container:
                        for warning in guardrail_result["warnings"]:
                            st.markdown(
                                f'<div class="warning-box">{warning}</div>',
                                unsafe_allow_html=True
                            )

                # Step 7: Show verified badge
                if guardrail_result["math_verified"]:
                    with chat_container:
                        st.markdown(
                            '<div class="verified-badge">✅ Amounts verified</div>',
                            unsafe_allow_html=True
                        )

                # Step 8: Store complete response in history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": guardrail_result["final_answer"],
                    "warnings": guardrail_result["warnings"],
                    "math_verified": guardrail_result["math_verified"]
                })

                logger.info(
                    f"Response complete | "
                    f"math_verified={guardrail_result['math_verified']} | "
                    f"warnings={len(guardrail_result['warnings'])}"
                )

st.divider()
st.caption(
    "🔒 Your documents are processed locally and never stored. "
    "Powered by Groq + Llama 3.3 70B."
)