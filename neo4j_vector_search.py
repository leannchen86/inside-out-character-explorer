from langchain.graphs import Neo4jGraph
import streamlit as st
import os

NEO4J_URI= st.secrets(["NEO4J_URI"])
NEO4J_USERNAME= st.secrets(["NEO4J_USERNAME"])
NEO4J_PASSWORD= st.secrets(["NEO4J_PASSWORD"])

graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD
)

try:
    create_index_query = """
    CALL db.index.vector.createNodeIndex(
      'roles',    // index name
      'Chunk',    // node label
      'embedding',// node property
      1536,      // vector size
      'cosine'   // similarity metric
    )
    """
    graph.query(create_index_query)
except Exception as e:
    # Check for the specific error message or type here
    if "EquivalentSchemaRuleAlreadyExistsException" in str(e):
        pass  # Index already exists, so just continue
    else:
        raise  # If it's another exception, raise it

import sys
sys.path.append('../..')

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

# Embeddings/Text

import json

with open('chunks.json', 'r') as input_file:
    chunks_from_json = json.load(input_file)

# Store vectors to Neo4j
graph.query("""
    UNWIND $data AS row
    CREATE (c:Chunk {text: row.text})
    WITH c, row
    CALL db.create.setVectorProperty(c, 'embedding', row.embedding)
    YIELD node
    RETURN distinct 'done'
    """, {'data': chunks_from_json})


vector_search = """
WITH $embedding AS e
CALL db.index.vector.queryNodes('roles',$k, e) yield node, score
RETURN node.text AS result
"""

graphforApp = graph 
vectorforApp = vector_search   
