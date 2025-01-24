import torch
from collections import defaultdict
import faiss
import numpy as np

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Set the pad_token_id for the model explicitly to avoid the warning
model.generation_config.pad_token_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id

tokenizer.pad_token = tokenizer.eos_token
model.pad_token_id = model.config.eos_token_id

def generate_text(prompt, max_length=512):
  """
  Generates text using the 4-bit quantized Phi-4 model.
  """
  inputs = tokenizer(prompt, return_tensors="pt").to(device)
  outputs = model.generate(**inputs, max_length=max_length, pad_token_id=tokenizer.pad_token_id) #added pad token id here
  generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
  return generated_text

# Function to create embeddings for recipes (using Phi-4)
def create_recipe_embeddings(recipes):
    """
    Creates embeddings for each recipe using Phi-4.
    """
    embeddings = []
    for recipe in recipes:
        prompt = f"Recipe: {recipe[0]}\nIngredients: {', '.join(recipe[1])}"
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        # The Key change is calling the model directly
        outputs = model(**inputs, output_hidden_states=True)
        # Extract the last hidden state, convert to float, and mean across all tokens (corrected)
        embedding = outputs.hidden_states[-1].float().mean(dim=1).cpu().detach().numpy()
        embeddings.append(embedding)
    return np.array(embeddings).squeeze(1)



# Sample recipe data (replace with your actual recipe data)
recipes = [
    ("Chicken and Broccoli Stir-Fry", ["chicken", "broccoli", "soy sauce", "ginger"]),
    ("Spaghetti with Tomato Sauce", ["pasta", "tomatoes", "garlic", "onion"]),
    ("Kung Pao Chicken",["chicken", "peanuts", "garlic","peppercorns"]),
    ("Tuscan Chicken Skillet", ["chicken", "bacon", "cream", "parmesan"]),
    ("Chicken Florentine",["chicken", "spinach", "garlic", "cream"])
    # ... add more recipes here
]

# Create recipe embeddings
recipe_embeddings = create_recipe_embeddings(recipes)

# Build a FAISS index
dimension = recipe_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)  # Using a simple L2 distance index
index.add(recipe_embeddings)

# Function to search for similar recipes using FAISS

def search_recipes(ingredients, top_k=3):
    """
    Searches for similar recipes in the FAISS index based on ingredient embeddings.
    """
    prompt = f"Ingredients: {', '.join(ingredients)}"
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    # Remove the generate and call the model directly to obtain hidden_states
    outputs = model(**inputs, output_hidden_states=True)
    # Extract the last hidden state, convert to float, mean across all tokens, and reshape (corrected)
    query_embedding = outputs.hidden_states[-1].float().mean(dim=1).cpu().detach().numpy() # Access hidden states directly
    query_embedding = query_embedding.reshape(1, -1)  # Reshape to (1, embedding_dimension)
    D, I = index.search(query_embedding, top_k)  # Search for top_k similar recipes
    similar_recipe_indices = I[0]
    return [recipes[i][0] for i in similar_recipe_indices]  # Return recipe names



# Simple NLU (replace with a more sophisticated NLU component)
def extract_ingredients(user_input):
  """
  Extracts ingredients from the user input (very basic example).
  """
  ingredients = []
  if "chicken" in user_input:
    ingredients.append("chicken")
  if "broccoli" in user_input:
    ingredients.append("broccoli")
  if "pasta" in user_input:
    ingredients.append("pasta")
  if "tomatoes" in user_input:
    ingredients.append("tomatoes")
  if "peanuts" in user_input:
    ingredients.append("peanuts")
  if "bacon" in user_input:
    ingredients.append("bacon")
  if "spinach" in user_input:
    ingredients.append("spinach")

  # Add more ingredient extraction logic here...
  return tuple(ingredients)

# Agent State (to remember past interactions and goals)
agent_state = defaultdict(lambda: {
    "ingredients": [],
    "last_recipe": None,
    "goal": None,
    "goal_completed": False,
    "rejected_recipes": []  # Keep track of rejected recipes
})

# Agent interaction loop
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    # Extract ingredients and potential goal (simplified example)
    ingredients = extract_ingredients(user_input)
    if "make a meal with" in user_input:
        goal = "suggest a recipe"
    elif "what else can I make" in user_input:
        goal = "suggest another recipe"
    elif "I don't like that" in user_input:
        goal = "reject suggestion"
    else:
        goal = None

    # Update agent state
    user_state = agent_state[user_input]
    user_state["ingredients"].extend(ingredients)
    if goal:
        user_state["goal"] = goal

    # Construct the prompt with state and goal (no knowledge base in the prompt)
    prompt = f"I have {', '.join(user_state['ingredients'])}. "
    if user_state["last_recipe"]:
        prompt += f"I already suggested {user_state['last_recipe']}. "
    if user_state["rejected_recipes"]:
        prompt += f"The user didn't like these recipes: {', '.join(user_state['rejected_recipes'])}. "
    if user_state["goal"]:
        prompt += f"My goal is to {user_state['goal']}. "
    prompt += "What should I do?\n"  # Ask the agent what to do

    response = generate_text(prompt)

    # Extract suggestions or actions from the response (simplified example)
    suggestions = []
    for line in response.splitlines():
        if "- " in line:
            suggestions.append(line.split("- ")[1])

    # If no suggestions from Phi-4, use FAISS
    if not suggestions:
        suggestions = search_recipes(user_state["ingredients"])

    # Update agent state and determine if goal is completed
    if suggestions and user_state["goal"] == "suggest a recipe":
        user_state["last_recipe"] = suggestions[0]
        user_state["goal_completed"] = True
    elif suggestions and user_state["goal"] == "suggest another recipe":
        # Ensure it's not the same as the last recipe or a rejected recipe
        if suggestions[0] != user_state["last_recipe"] and suggestions[0] not in user_state["rejected_recipes"]:
            user_state["last_recipe"] = suggestions[0]
            user_state["goal_completed"] = True
    elif user_state["goal"] == "reject suggestion" and user_state["last_recipe"]:
        user_state["rejected_recipes"].append(user_state["last_recipe"])
        user_state["last_recipe"] = None
        user_state["goal_completed"] = True

    print("Agent: Here are some recipe suggestions:")
    for suggestion in suggestions:
        print(f"- {suggestion}")

    if user_state["goal_completed"]:
        print("Agent: I have completed my goal.")
        user_state["goal"] = None
        user_state["goal_completed"] = False