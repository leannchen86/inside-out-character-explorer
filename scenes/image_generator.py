from langchain.document_loaders import PyPDFLoader
# Load PDF
loader = PyPDFLoader('INSIDE_OUT.pdf')
docs = loader.load()

new_docs = [docs[i].page_content for i in range(len(docs))]
new_docs = ' '.join(new_docs)

# Using Python's re.split with capturing groups to retain the separator in the output
import re

scene_pattern = r'(?:INT\.|EXT\.) [A-Za-z\s\.-]+ \d+'
split_text = re.split(scene_pattern, new_docs)
# The above will remove the separators (scene titles). To keep them, you can modify the regex to use capturing groups:
scene_pattern = r'((?:INT\.|EXT\.) [A-Za-z\s\.-]+ \d+)'
split_text_with_separators = re.split(scene_pattern, new_docs)

split_text_with_separators = split_text_with_separators[1:]

def join_elements(input_list, step=2):

    joined_list = []
    count = 0
    for i in range(0, len(input_list), step):
        combined = ''.join(input_list[i:i+step])
        joined_list.append(combined)
        
    return joined_list

splits = join_elements(split_text_with_separators)

characters = ["JOY", "SADNESS", "ANGER", "DISGUST", "FEAR"]

sample_scenes = []  

for scene_text in splits:
    scene_dict = {}
    scene_dict['text'] = scene_text
    scene_dict['characters'] = []

    for character in characters:
        if character in scene_text:
            scene_dict['characters'].append(character)

    sample_scenes.append(scene_dict)


from collections import defaultdict
from itertools import combinations
from textblob import TextBlob

# Initialize a dictionary to hold interaction counts and sentiment
interaction_data = defaultdict(lambda: {'count': 0, 'sentiment': 0})

# Loop through each scene
for scene in sample_scenes:
    chars = scene['characters']
    text = scene['text']
    
    # Compute sentiment using TextBlob
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    
    # Find all combinations of characters present in the scene
    char_combinations = combinations(chars, 2)
    
    for comb in char_combinations:
        interaction_data[frozenset(comb)]['count'] += 1
        interaction_data[frozenset(comb)]['sentiment'] += sentiment

# Calculate average sentiment for each interaction
for interaction, data in interaction_data.items():
    data['sentiment'] /= data['count']

# Print interaction data (for demonstration)
for interaction, data in interaction_data.items():
    print(f"{interaction}: {data}")

# Initialize a list to hold interaction data for all scenes
interaction_data_all_scenes = []

# Loop through each scene
for scene in sample_scenes:
    # Initialize a dictionary to hold interaction counts and sentiment for this scene
    interaction_data_scene = defaultdict(lambda: {'count': 0, 'sentiment': 0})
    
    chars = scene['characters']
    text = scene['text']
    
    # Compute sentiment using TextBlob
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    
    # Find all combinations of characters present in the scene
    char_combinations = combinations(chars, 2)
    
    for comb in char_combinations:
        interaction_data_scene[frozenset(comb)]['count'] += 1
        interaction_data_scene[frozenset(comb)]['sentiment'] += sentiment
    
    # Calculate average sentiment for each interaction in this scene
    for interaction, data in interaction_data_scene.items():
        data['sentiment'] /= data['count']
        
    # Append this scene's interaction data to the list
    interaction_data_all_scenes.append(interaction_data_scene)

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def map_sentiment_to_color(sentiment, vmin, vmax):
    # Create a colormap that goes from red to green
    cmap = plt.get_cmap("RdYlGn")
    
    # Normalize the sentiment score to be between vmin and vmax
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    
    # Get the RGBA color corresponding to this sentiment
    rgba_color = cmap(norm(sentiment))
    
    # Convert to a format that Pyvis will understand: an 8-digit hex string
    hex_color = mcolors.to_hex(rgba_color)
    
    return hex_color

from collections import defaultdict
from itertools import combinations
from textblob import TextBlob

# Initialize a list to hold interaction data for all scenes
interaction_data_all_scenes = []

# Loop through each scene
for scene in sample_scenes:
    # Initialize a dictionary to hold interaction counts and sentiment for this scene
    interaction_data_scene = defaultdict(lambda: {'count': 0, 'sentiment': 0})
    
    chars = scene['characters']
    text = scene['text']
    
    # Compute sentiment using TextBlob
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    
    # Find all combinations of characters present in the scene
    char_combinations = combinations(chars, 2)
    
    for comb in char_combinations:
        interaction_data_scene[frozenset(comb)]['count'] += 1
        interaction_data_scene[frozenset(comb)]['sentiment'] += sentiment
    
    # Calculate average sentiment for each interaction in this scene
    for interaction, data in interaction_data_scene.items():
        data['sentiment'] /= data['count']
        
    # Append this scene's interaction data to the list
    interaction_data_all_scenes.append(interaction_data_scene)

from pyvis.network import Network
import networkx as nx

import base64

def image_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def plot_network_snapshot_pyvis(interaction_data_all_scenes, scene_number, min_sentiment_all, max_sentiment_all):
    interaction_data = interaction_data_all_scenes[scene_number]
    net = Network(height='100%', width='100%', bgcolor='#ffffff', font_color='black', notebook=True)
    
    character_images_base64 = {
        'JOY': f"data:image/jpeg;base64,{image_to_base64('Joy.jpg')}",
        'SADNESS': f"data:image/jpeg;base64,{image_to_base64('Sadness.jpg')}",
        'ANGER': f"data:image/jpeg;base64,{image_to_base64('Anger.jpg')}",
        'DISGUST': f"data:image/jpeg;base64,{image_to_base64('Disgust.jpg')}",
        'FEAR': f"data:image/jpeg;base64,{image_to_base64('Fear.jpg')}"
    }

    for character, image_base64 in character_images_base64.items():
        net.add_node(character, label=character, shape='image', image=image_base64)
    
    if not interaction_data:
        print("No interactions to display for this scene.")
        return
    
    G = nx.Graph()
    
    for interaction, data in interaction_data.items():
        char1, char2 = list(interaction)
        count = data['count']
        sentiment = round(data['sentiment'],2)
        color = map_sentiment_to_color(sentiment, min_sentiment_all, max_sentiment_all)
        G.add_edge(char1, char2, weight=count)
        net.add_edge(char1, char2, value=count, color=color, title=f"Sentiment: {sentiment}")
    
    # Initialize centrality as 0 for all nodes
    centrality = {node: 0 for node in G.nodes()}

    if G.edges():
        try:
            centrality = nx.eigenvector_centrality_numpy(G, weight='weight')
            rnd_centrality = {node: round(value, 2) for node, value in centrality.items()}
            centrality = rnd_centrality
        except (nx.NetworkXError, TypeError):  # Catch the specific exceptions you're expecting
            centrality = {node: 1 for node in G.nodes()}  # Assign 1 if eigenvector centrality can't be calculated
    else:
        centrality = {node: 1 for node in G.nodes()}  # Assign 1 if the graph is empty
    
    # Re-add nodes with updated attributes
    for node_id in characters:
        net.add_node(node_id, 
                     # label=f"{node_id} Centrality: {centrality.get(node_id, 0)}", 
                     # title=f"Centrality: {centrality.get(node_id, 0)}", 
                     color=f"rgba(0,255,0,{centrality.get(node_id, 0)})", 
                     update=True)
        
    # Update existing nodes with the new centrality information
    for node in net.nodes:
        node_id = node['id']
        node['color'] = f"rgba(0,255,0,{centrality.get(node_id, 0)})"
        # node['title'] = f"Centrality: {centrality.get(node_id, 0)}"
        # node['label'] = f"{node_id} Centrality: {centrality.get(node_id, 0)}"
    
    # Update the attributes in the Pyvis network
    net.node_map[node_id].update(node)

    
    # Customize layout
    net.set_options("""
    var options = {
      "nodes": {
        "borderWidth": 2,
        "size": 30,
        "color": {
          "border": "transparent",
          "background": "#00F"
        },
        "font": {
          "color": "#FFFFFF"
        }
      },
      "edges": {
        "color": "transparent",
        "smooth": false
      },
      "physics": {
        "stabilization": false,
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      }
    }
    """)

    net.show(f"{scene_number}.html", notebook=True)
    return net  # Return the Network object, not the output of `show()`

def sentiment_values(interaction_data, is_all_scenes=False):
    if is_all_scenes:
        # Flatten all the sentiments across scenes into a single list
        sentiment_values = [data['sentiment'] for scene in interaction_data for data in scene.values()]
    else:
        sentiment_values = [data['sentiment'] for data in interaction_data.values()]

    if not sentiment_values:
        return None, None  # Handle empty list

    # Find the minimum and maximum sentiment values
    min_sentiment = min(sentiment_values)
    max_sentiment = max(sentiment_values)

    return min_sentiment, max_sentiment

# For a single scene (single dictionary)
min_sentiment, max_sentiment = sentiment_values(interaction_data)

# For all scenes (list of dictionaries)
min_sentiment_all, max_sentiment_all = sentiment_values(interaction_data_all_scenes, is_all_scenes=True)

# Generate an HTML file for each scene
for i in range(len(interaction_data_all_scenes)):
    plot_network_snapshot_pyvis(interaction_data_all_scenes, i,min_sentiment_all, max_sentiment_all)

