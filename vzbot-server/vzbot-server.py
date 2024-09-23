import os
import dotenv
import logging
import traceback
from langchain_openai import OpenAIEmbeddings 
from langchain_community.vectorstores import FAISS 
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
from logtail import LogtailHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS

#Load local environment variables
dotenv.load_dotenv()
bot_token = os.getenv("TELEGRAM_API_TOKEN")
openai_token = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("MODEL_NAME")
embeddings_name = os.getenv("EMB_MODEL_NAME")
betterstack_token = os.getenv("BETTERSTACK_TOKEN")
base_url = os.getenv("BASE_URL")
k_value = int(os.getenv("K_VALUE"))
temperature = float(os.getenv("TEMPERATURE"))

#BetterStack logger if token is provided  
if betterstack_token:
  handler = LogtailHandler(source_token=betterstack_token)
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.INFO)
  logger.handlers = []
  logger.addHandler(handler)
  logger.info('bot_start')
  print("betterstack is ready")

def clean_text(text):
    #temporary disabled function
    #text = text.strip()
    #text = text.replace("<", "&lt;").replace(">", "&gt;")
    #text = re.sub(r'\s+', ' ', text)
    #text = re.sub(r'\n+', ' ', text)
    return text

embeddings = OpenAIEmbeddings(model=embeddings_name)

new_vector_store = FAISS.load_local(
    "faiss_db", embeddings, allow_dangerous_deserialization=True
)

#Request to OpenAI
llm = ChatOpenAI(
  base_url=base_url,
  openai_api_key=openai_token,
  temperature=temperature, 
  model_name=model_name,
  max_tokens=600
  )

retriever=new_vector_store.as_retriever(search_type="mmr", search_kwargs={"k": k_value})

system_prompt = (
    "You are an assistant for question-answering tasks. Use "
    "the following piece of retrieved context to answer the question."
    "Try to provide an example."
    "Context: {context}"
    "Question: {input}"
    "Answer:"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

message = "how to create a virtual machine"

print("SERVER IS READY")

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json['message']

    try:
        with get_openai_callback() as cb:
            answer = rag_chain.invoke({"input": message})
            #print(answer["context"])
        print(cb)

        answer_context = clean_text(answer["answer"] if 'answer' in answer else "I'm sorry, I couldn't find an answer.")

        sources = []
        if 'url' in answer["context"][0].metadata:
            sources = [doc.metadata['url'] for doc in answer["context"]]
        else:
            print("No source_documents found in bot_reply")

        source_text = "\nFor more information, check:\n" + "\n".join(sources) if sources else "No source available."

        response = jsonify({"reply": f"{answer_context}\n{source_text}"})
    except Exception as e:
        response = jsonify({"reply": "An error occurred. Please try again later."})
        print(f"Error: {str(e)}\nTraceback: {traceback.format_exc()}")

    response = make_response(response)
    return response

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port="8080")