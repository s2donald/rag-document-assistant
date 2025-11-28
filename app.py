import streamlit as st
import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain

# Page Config
st.set_page_config(page_title="Cloud RAG Demo", layout="wide")

st.title("☁️ AWS RAG Demo: Chat with PDF")
st.markdown("### A Serverless RAG App (Free Version with Hugging Face)")

# Sidebar for API Key and File Upload
with st.sidebar:
    st.header("Configuration")
    
    # Securely getting API Key
    api_token = st.text_input("Enter Hugging Face Token", type="password", help="Get your free token from huggingface.co/settings/tokens")
    
    st.divider()
    
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    
    st.info("This app uses the free Hugging Face Inference API and runs locally in a Docker container on AWS.")

# Main Logic
if uploaded_file and api_token:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_token
    
    # Save uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # 1. Load the PDF
        with st.spinner("Processing PDF..."):
            loader = PyPDFLoader(tmp_file_path)
            documents = loader.load()

            # 2. Split the text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)

            # 3. Create Vector Store (FAISS)
            # We use a lightweight local embedding model (all-MiniLM-L6-v2)
            # This runs ON the container CPU, so it costs nothing but RAM.
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            vectorstore = FAISS.from_documents(splits, embeddings)
            
            # 4. Define the LLM
            # We use the Mistral 7B model via the Hugging Face Hub API (Free Tier)
            repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
            llm = HuggingFaceEndpoint(
                repo_id=repo_id,
                temperature=0.1,
                model_kwargs={"max_length": 512}
            )

            # 5. Create Retrieval Chain
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=vectorstore.as_retriever(),
                return_source_documents=True
            )

        st.success("PDF Processed! You can now chat with your document.")

        # Chat Interface
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("Ask a question about the PDF..."):
            # Display user message
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # We pass an empty chat history for simplicity in this stateless demo
                    response = qa_chain({"question": prompt, "chat_history": []})
                    answer = response['answer']
                    st.markdown(answer)
                    
                    # Optional: Show sources
                    with st.expander("View Source Context"):
                        for doc in response['source_documents']:
                            st.write(doc.page_content[:200] + "...")

            st.session_state.messages.append({"role": "assistant", "content": answer})

    except Exception as e:
        st.error(f"An error occurred: {e}")
    
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

elif not api_token:
    st.warning("Please enter your Hugging Face API Token in the sidebar to proceed.")
elif not uploaded_file:
    st.info("Please upload a PDF document to start chatting.")