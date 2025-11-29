import streamlit as st
import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

# Page Config
st.set_page_config(page_title="RAG Document Assistant", layout="wide")

st.title("☁️ AWS RAG Demo: Understand the contents of the PDF")
st.markdown("### A Serverless RAG App (HF Router via Featherless.ai)")

# Sidebar for API Key and File Upload
with st.sidebar:
    st.header("Configuration")
    api_token = st.text_input("Enter Hugging Face Token", type="password", help="Get your free token from huggingface.co/settings/tokens")
    st.divider()
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
    st.info("This app uses the Hugging Face 'Chat Completion' Router to access specific providers.")

# Main Logic
if uploaded_file and api_token:
    os.environ["OPENAI_API_KEY"] = api_token
    
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
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            vectorstore = FAISS.from_documents(splits, embeddings)
            
            # 4. Define the LLM (ChatOpenAI pointed at Hugging Face)
            llm = ChatOpenAI(
                base_url="https://router.huggingface.co/v1",
                model="HuggingFaceH4/zephyr-7b-beta:featherless-ai",
                temperature=0.1,
                max_tokens=512,
            )

            # 5. Define a Strict Prompt Template
            # We explicitly tell it how to behave.
            custom_template = """
            <|system|>
            You are a helpful AI assistant. Use the following pieces of context to answer the user's question.
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            </s>
            <|user|>
            Context:
            {context}

            Question:
            {question}
            </s>
            <|assistant|>
            """
            
            QA_CHAIN_PROMPT = PromptTemplate.from_template(custom_template)

            # 6. Create Retrieval Chain with Custom Prompt
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=vectorstore.as_retriever(),
                return_source_documents=True,
                combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT}
            )

        st.success("PDF Processed! You can now ask questions about your document to the chat.")

        # Chat Interface
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("Ask a question about the PDF..."):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = qa_chain.invoke({"question": prompt, "chat_history": []})
                    answer = response['answer']
                    st.markdown(answer)
                    
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
    st.info("Please upload a PDF document to start asking questions about it.")