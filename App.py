import streamlit as st
import os
from langchain.embeddings import OpenAIEmbeddings
import openai
import json
import neo4j_vector_search
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering.stuff_prompt import CHAT_PROMPT
from langchain.callbacks.manager import CallbackManagerForChainRun
from typing import Any, Dict, List
from pydantic import Field
from langchain.graphs import Neo4jGraph
vector_search = neo4j_vector_search.vectorforApp
graph = neo4j_vector_search.graphforApp


# Load the data from the JSON file
with open('chunks.json', 'r') as input_file:
    chunks_from_json = json.load(input_file)

# Streamlit app title
st.title("Inside Out Characters Explorer")
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="langchain_search_api_key_openai", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"

openai.api_key = openai_api_key
# Directory path for the scenes
dir_path = 'scenes'

# Check if directory exists
if not os.path.exists(dir_path):
    st.error(f"Directory {dir_path} does not exist.")
    st.stop()

# Get list of available HTML files in the directory
html_files = [f for f in os.listdir(dir_path) if f.endswith('.html') and f.split('.')[0].isdigit()]
html_files.sort(key=lambda f: int(f.split('.')[0]))  # Sort by scene number

scene_numbers = [int(f.split('.')[0])+1 for f in html_files]

col1, col2 = st.columns([1.5,1], gap='small')

with col2:
    selected_scene = st.select_slider(
        "Select Scene",
        options=scene_numbers)

    scene_file_path = os.path.join(dir_path, f"{selected_scene-1}.html")
    if st.button('Summary'):
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()
            
        scene_summary = chunks_from_json[selected_scene-1]['text']

        messages = [{'role': 'system', 'content': 'Please summarize what happens in the text.'},
                    {'role': 'user', 'content': scene_summary}]
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0)
        response = completion["choices"][0]["message"]["content"]
        st.write(response)

with col1:
    if os.path.exists(scene_file_path):
        with open(scene_file_path, 'r', encoding='utf-8') as selected_files:
            st.components.v1.html(selected_files.read(), width=400, height=320, scrolling=False)
    else:
        st.error(f"Scene file {selected_scene}.html does not exist.")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi there, ask me anything about the characters!"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Who is Sadness?"):
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    class Neo4jVectorChain(Chain):
        import os
        os.environ["OPENAI_API_KEY"] = openai_api_key

        """Chain for question-answering against a neo4j vector index."""

        graph: Neo4jGraph = Field(exclude=True)
        input_key: str = "query"  #: :meta private:
        output_key: str = "result"  #: :meta private:
        embeddings: OpenAIEmbeddings = OpenAIEmbeddings()
        qa_chain: LLMChain = LLMChain(llm=ChatOpenAI(model_name="gpt-4", temperature=0), prompt=CHAT_PROMPT)

        @property
        def input_keys(self) -> List[str]:
            """Return the input keys.
            :meta private:
            """
            return [self.input_key]

        @property
        def output_keys(self) -> List[str]:
            """Return the output keys.
            :meta private:
            """
            _output_keys = [self.output_key]
            return _output_keys

        def _call(self, inputs: Dict[str, str], run_manager, k=3) -> Dict[str, Any]:
            """Embed a question and do vector search."""
            question = inputs[self.input_key]
            embedding = self.embeddings.embed_query(question)
            # run_manager.on_text(
            #     "Vector search embeddings:", end="\n", verbose=self.verbose
            # )
            # run_manager.on_text(
            #     embedding[:5], color="green", end="\n", verbose=self.verbose
            # )

            context = self.graph.query(
                vector_search, {'embedding': embedding, 'k': 3})
            context = [el['result'] for el in context]
            # run_manager.on_text(
            #     "Retrieved context:", end="\n", verbose=self.verbose
            # )
            # run_manager.on_text(
            #     context, color="green", end="\n", verbose=self.verbose
            # )

            result = self.qa_chain(
                {"question": question, "context": context},
            )
            final_result = result[self.qa_chain.output_key]
            return {self.output_key: final_result}

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    embeddings = OpenAIEmbeddings()
    graph = neo4j_vector_search.graphforApp    
    vector_qa = Neo4jVectorChain(graph=graph, embeddings=embeddings, verbose=True)
    response = vector_qa.run(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)


   



