import streamlit as st
from langchain_mistralai import ChatMistralAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import (SentenceTransformerEmbeddings)


# app config
st.set_page_config(page_title="Streaming bot", page_icon="🤖")
st.title("PredixionAI ChatBot")

llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=2,
)

# Connecting the MySQL database
db_uri = "mysql+mysqlconnector://root:password@localhost:3306/user_bg"
db = SQLDatabase.from_uri(db_uri)
execute_query = QuerySQLDataBaseTool(db=db)
generate_query = create_sql_query_chain(llm, db)
chain = generate_query | execute_query 


# Function to fetch user data dynamically
def get_user_data(user_name):
    """Fetch user data from the database based on the provided name."""
    query = generate_query.invoke({"question": f"Select all data for the user where the name is '{user_name}' "})
    context = execute_query.run(query)
    return context

# Storing the Embeddings of RBL pdf Data
embedding_function = SentenceTransformerEmbeddings(model_name = "all-MiniLM-L6-v2")
embedding_db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)

def get_response(user_query, chathistory, context, doc_context):

    # Define the template for LLM
    llm_query_res_template = """
        Answer the question based on the context below. If the question cannot be answered using the information provided, reply with "I don't know". Also, make sure to answer the following questions considering the history of the conversation:
        You are an intelligent virtual financial assistant for Predixion AI, directly engaging with customers about their loan repayments. Your role is to help manage their loan, facilitate payments, and answer financial questions in a clear, professional way. Communicate in a friendly, authoritative manner, addressing the customer directly ("you") with concise responses suitable for WhatsApp.
        Make sure you communicate with the user in such a way that your response should always lead to payment collection.
        Based on the user question, you should respond in a short way. Do not write much; it should be short and precise.

        Instructions:
        1. Use precise financial language and ensure clear, accurate information.
        2. Facilitate payments: If the user is willing to pay the loan then please provide this link '''https://www.predixion.ai'''. Do not send the link until user requests or user wants to pay the loan.
        3. Offer solutions: If the customer is struggling, provide options like grace periods, payment restructuring, or deadline extensions.
        4. Keep responses short and to the point.
        5. Ensure confidentiality and remind the customer to keep their payment details secure.
        6. You can only extend the loan dates by 10 days if user requests for grace periods or deadline extensions.

        Important: If the user ask anything related to the content in Doc context then only you can use this information mention in the Doc context else you cannot use.

        Context: {context}
        Question: {user_query}
        Chat history: {chathistory}
        Doc context: {doc_context}
        Answer: """

    # Create the chat prompt template
    prompt_query_res_template = ChatPromptTemplate.from_template(llm_query_res_template)
    llm_chain = prompt_query_res_template | llm | StrOutputParser()

    return llm_chain.stream({
        "user_query": user_query,      
        "chathistory": chathistory,       
        "context": context, 
        "doc_context": doc_context,     
    })


# Chatbot session state initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am from PredixionAI. How can I help you?"),
    ]

if "user_name" not in st.session_state:
    st.session_state.user_name = None
    st.session_state.context = None
    st.session_state.doc_context = None 

# Conversation handling
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# Input Handling
if st.session_state.user_name is None:
    if "name_asked" not in st.session_state:
        st.session_state.name_asked = True 
        st.session_state.chat_history.append(AIMessage(content="Please provide your name so that we can fetch your data:"))
        with st.chat_message("AI"):
            st.write("Please provide your name so that we can fetch your data:")

    user_name = st.chat_input("Type your name here...")
    if user_name:
        st.session_state.user_name = user_name

        # Fetch the context (user data) dynamically from DB
        st.session_state.context = get_user_data(st.session_state.user_name)
        st.session_state.chat_history.append(AIMessage(content=f"Thank you, {st.session_state.user_name}. How can I assist you today?"))
        with st.chat_message("AI"):
            st.write(f"Thank you, {st.session_state.user_name}. How can I assist you today?")

else:
    user_query = st.chat_input("Type your message here...")
    if user_query:
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        with st.chat_message("Human"):
            st.markdown(user_query)

        # Perform document similarity search for doc_context
        st.session_state.doc_context = embedding_db.similarity_search(user_query)

        # Get the response from LLM using the context fetched earlier and the document context
        response = st.write_stream(
            get_response(
                user_query, 
                st.session_state.chat_history, 
                st.session_state.context, 
                st.session_state.doc_context  
            )
        )

        st.session_state.chat_history.append(AIMessage(content=response))