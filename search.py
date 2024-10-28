import math
import pickle
import json
import random
from FOON_class import Object
from math import sqrt, log

# -----------------------------------------------------------------------------------------------------------------------------#

class MCTSNode:
    def __init__(self, state, parent=None):
        self.state = state  # Object ID in FOON
        self.parent = parent
        self.children = []  # List of (FU_index, MCTSNode) tuples
        self.visits = 0
        self.wins = 0
        self.untried_FUs = []  # List of untried functional units

def search_MCTS(kitchen_items=[], goal_node=None, foon_object_nodes=None, foon_functional_units=None, 
                foon_object_to_FU_map=None, utensils=[], k=1000):
    """
    Monte Carlo Tree Search implementation for FOON
    k: number of simulations to run (default 1000)
    """
    
    # Initialize root node with goal object
    root = MCTSNode(goal_node.id)
    root.untried_FUs = list(foon_object_to_FU_map[goal_node.id])
    
    # Run k simulations
    for _ in range(k):
        node = root
        
        # Selection: Select best child until we reach a node with untried moves
        while node.untried_FUs == [] and node.children != []:
            node = select_child(node)
            
        # Expansion: Add a new child node if there are untried moves
        if node.untried_FUs != []:
            fu_index = random.choice(node.untried_FUs)
            node.untried_FUs.remove(fu_index)
            
            # Create new node for each input object of the selected functional unit
            for input_node in foon_functional_units[fu_index].input_nodes:
                child_state = input_node.id
                child = MCTSNode(child_state, parent=node)
                
                # Add untried FUs for the child node
                if child_state in foon_object_to_FU_map:
                    child.untried_FUs = list(foon_object_to_FU_map[child_state])
                
                node.children.append((fu_index, child))
        
        # Simulation: Perform random moves until we reach a terminal state
        success = simulate_execution(node, foon_object_nodes, foon_functional_units, 
                                  foon_object_to_FU_map, kitchen_items)
        
        # Backpropagation: Update statistics for all nodes in the path
        while node is not None:
            node.visits += 1
            if success:
                node.wins += 1
            node = node.parent
    
    # Build the final task tree using the most visited path
    return build_task_tree(root, foon_functional_units)

def select_child(node):
    """
    Select the best child node using UCT formula
    UCT = wins/visits + C * sqrt(ln(parent_visits)/visits)
    """
    C = sqrt(2)  # Exploration parameter
    
    best_score = float('-inf')
    best_child = None
    
    for _, child in node.children:
        if child.visits == 0:
            return child
        
        # Calculate UCT score
        exploitation = child.wins / child.visits
        exploration = C * sqrt(log(node.visits) / child.visits)
        uct_score = exploitation + exploration
        
        if uct_score > best_score:
            best_score = uct_score
            best_child = child
    
    return best_child

def simulate_execution(node, foon_object_nodes, foon_functional_units, foon_object_to_FU_map, kitchen_items):
    """
    Simulate random execution from current node state
    Returns True if simulation successful, False otherwise
    """
    current_state = node.state
    visited_states = set()
    
    while True:
        # Check if current object exists in kitchen
        current_object = foon_object_nodes[current_state]
        if check_if_exist_in_kitchen(kitchen_items, current_object):
            return True
            
        # Get available functional units for current state
        if current_state not in foon_object_to_FU_map:
            return False
            
        available_FUs = foon_object_to_FU_map[current_state]
        if not available_FUs:
            return False
            
        # Select random FU
        selected_FU = random.choice(available_FUs)
        
        # Get motion success rate and simulate success/failure
        motion_success_rate = get_motion_rate(foon_functional_units[selected_FU].motion_node)
        if motion_success_rate is None or random.random() > motion_success_rate:
            return False
            
        # Select random input object as next state
        input_nodes = foon_functional_units[selected_FU].input_nodes
        if not input_nodes:
            return False
            
        current_state = random.choice(input_nodes).id
        
        # Check for cycles
        if current_state in visited_states:
            return False
        visited_states.add(current_state)

def build_task_tree(root, foon_functional_units):
    """
    Build the final task tree by selecting the most visited paths
    """
    task_tree = []
    current = root
    
    while current.children:
        # Find child with most visits
        best_visits = -1
        best_fu_index = None
        best_child = None
        
        for fu_index, child in current.children:
            if child.visits > best_visits:
                best_visits = child.visits
                best_fu_index = fu_index
                best_child = child
        
        if best_fu_index is None:
            break
            
        task_tree.append(foon_functional_units[best_fu_index])
        current = best_child
    
    return task_tree

# Other search algorithms and functions below...


# Checks an ingredient exists in kitchen

def check_if_exist_in_kitchen(kitchen_items, ingredient):
    """
        parameters: a list of all kitchen items,
                    an ingredient to be searched in the kitchen
        returns: True if ingredient exists in the kitchen
    """

    for item in kitchen_items:
        if item["label"] == ingredient.label \
                and sorted(item["states"]) == sorted(ingredient.states) \
                and sorted(item["ingredients"]) == sorted(ingredient.ingredients) \
                and item["container"] == ingredient.container:
            return True

    return False


# -----------------------------------------------------------------------------------------------------------------------------#

def search_BFS(kitchen_items=[], goal_node=None, foon_object_nodes=None, foon_functional_units=None, foon_object_to_FU_map=None, utensils=[]):
    # list of indices of functional units
    reference_task_tree = []

    # list of object indices that need to be searched
    items_to_search = []

    # find the index of the goal node in object node list
    items_to_search.append(goal_node.id)

    # list of items already explored
    items_already_searched = []

    while len(items_to_search) > 0:
        current_item_index = items_to_search.pop(0)  # pop the first element
        if current_item_index in items_already_searched:
            continue
        else:
            items_already_searched.append(current_item_index)

        current_item = foon_object_nodes[current_item_index]

        if not check_if_exist_in_kitchen(kitchen_items, current_item):
            candidate_units = foon_object_to_FU_map[current_item_index]

            # Selecting the first path
            selected_candidate_idx = candidate_units[0]

            # If an FU is already taken, do not process it again
            if selected_candidate_idx in reference_task_tree:
                continue

            reference_task_tree.append(selected_candidate_idx)

            # All inputs of the selected FU need to be explored
            for node in foon_functional_units[selected_candidate_idx].input_nodes:
                node_idx = node.id
                if node_idx not in items_to_search:
                    flag = True
                    if node.label in utensils and len(node.ingredients) == 1:
                        for node2 in foon_functional_units[selected_candidate_idx].input_nodes:
                            if node2.label == node.ingredients[0] and node2.container == node.label:
                                flag = False
                                break
                    if flag:
                        items_to_search.append(node_idx)

    # Reverse the task tree
    reference_task_tree.reverse()

    # Create a list of functional units from the indices of reference_task_tree
    task_tree_units = []
    for i in reference_task_tree:
        task_tree_units.append(foon_functional_units[i])

    return task_tree_units



def save_paths_to_file(task_tree, path):

    print('writing generated task tree to ', path)
    _file = open(path, 'w')

    _file.write('//\n')
    for FU in task_tree:
        _file.write(FU.get_FU_as_text() + "\n")
    _file.close()


# -----------------------------------------------------------------------------------------------------------------------------#
def search_IDS(kitchen_items=[], goal_node=None, max_depth=1, foon_object_nodes=None, foon_functional_units=None, foon_object_to_FU_map=None, utensils=[]):
    reference_task_tree = []
    items_to_search = [goal_node.id]
    items_already_searched = []
    
    while max_depth > 0:
        while len(items_to_search) > 0:
            current_item_index = items_to_search.pop(0)
            if current_item_index in items_already_searched:
                continue
            else:
                items_already_searched.append(current_item_index)

            current_item = foon_object_nodes[current_item_index]

            if not check_if_exist_in_kitchen(kitchen_items, current_item):
                candidate_units = foon_object_to_FU_map[current_item_index]

                selected_candidate_idx = candidate_units[0]

                if selected_candidate_idx in reference_task_tree:
                    continue

                reference_task_tree.append(selected_candidate_idx)

                for node in foon_functional_units[selected_candidate_idx].input_nodes:
                    node_idx = node.id
                    if node_idx not in items_to_search:
                        flag = True
                        if node.label in utensils and len(node.ingredients) == 1:
                            for node2 in foon_functional_units[selected_candidate_idx].input_nodes:
                                if node2.label == node.ingredients[0] and node2.container == node.label:
                                    flag = False
                                    break
                        if flag:
                            items_to_search.append(node_idx)

        # Increment depth and reset items_already_searched for the next iteration
        max_depth -= 1
        items_already_searched = []

    reference_task_tree.reverse()
    task_tree_units = []
    for i in reference_task_tree:
        task_tree_units.append(foon_functional_units[i])
    
    return task_tree_units
#----------------------------------------------------------------------



def get_motion_rate(node):
    with open("motion.txt", "r") as motion_file:
        flag = 0
        for line in motion_file:
            motion, success_rate = line.strip().split("\t")
            if motion == node:
                flag = 1
                motion_rate = float(success_rate)  # Convert to float
        if flag == 0:
            print("Error: no motion with this motion name")
            return None  # Handle case where motion is not found
    return motion_rate


def get_motion_successrate(candidate_units, foon_functional_units):
    success_rates = []
    for candidate in candidate_units:
        result_node = foon_functional_units[candidate]
        motion_node = result_node.motion_node
        success_rate = get_motion_rate(motion_node)
        if success_rate is not None:
            success_rates.append(success_rate)
        else:
            success_rates.append(0)  # Assign a default low rate if no success rate is found
    return success_rates


def calculate_a_star_score(success_rate, input_nodes_count):
    # A* combines cost (inverse success rate) and heuristic (number of input nodes)
    cost = 1 / success_rate  # Cost is the inverse of the success rate
    heuristic = input_nodes_count  # Heuristic is the number of input nodes
    return cost + heuristic


def search_a_star(kitchen_items=[], goal_node=None, foon_object_nodes=None, foon_functional_units=None, foon_object_to_FU_map=None, utensils=[]):
    """
    A* search algorithm to find the optimal task tree for a given goal node,
    using both the cost function (inverse success rate) and heuristic function 
    (number of input objects).
    """
    reference_task_tree = []  # Stores the selected functional units in the task tree
    items_to_search = [goal_node.id]  # List of goal node's input items to be explored
    items_already_searched = []  # List to avoid re-exploring nodes

    while len(items_to_search) > 0:
        current_item_index = items_to_search.pop(0)  # Get the next item to search

        if current_item_index in items_already_searched:
            continue
        else:
            items_already_searched.append(current_item_index)

        # Get the current object from FOON's object nodes
        current_item = foon_object_nodes[current_item_index]

        # Check if this item already exists in the kitchen
        if not check_if_exist_in_kitchen(kitchen_items, current_item):
            # Get the candidate functional units for this item
            candidate_units = foon_object_to_FU_map[current_item_index]
            
            # List to store (functional unit index, A* score) for each candidate
            candidate_scores = []

            # Calculate A* scores for all candidate functional units
            for candidate in candidate_units:
                result_node = foon_functional_units[candidate]
                motion_node = result_node.motion_node
                
                # Get the success rate for the motion node
                success_rate = get_motion_rate(motion_node)
                
                # Count the number of input nodes and ingredients
                input_nodes = result_node.input_nodes
                ingredients_count = sum(len(node.ingredients) for node in input_nodes)
                input_nodes_count = len(input_nodes) + ingredients_count
                
                # Calculate the A* score using the combined cost and heuristic
                score = calculate_a_star_score(success_rate, input_nodes_count)
                candidate_scores.append((candidate, score))

            # Select the candidate functional unit with the lowest A* score
            selected_candidate_idx = min(candidate_scores, key=lambda x: x[1])[0]

            # If this functional unit is already in the task tree, skip it
            if selected_candidate_idx in reference_task_tree:
                continue

            # Add the selected functional unit to the task tree
            reference_task_tree.append(selected_candidate_idx)

            # Explore the inputs of the selected functional unit
            for node in foon_functional_units[selected_candidate_idx].input_nodes:
                node_idx = node.id
                if node_idx not in items_to_search:
                    # Check if the node is a utensil containing ingredients
                    flag = True
                    if node.label in utensils and len(node.ingredients) == 1:
                        # Ensure not to add redundant container-ingredient pairs
                        for node2 in foon_functional_units[selected_candidate_idx].input_nodes:
                            if node2.label == node.ingredients[0] and node2.container == node.label:
                                flag = False
                                break
                    if flag:
                        items_to_search.append(node_idx)

    # Reverse the task tree to get the correct order
    reference_task_tree.reverse()

    # Create a list of functional units from the indices of reference_task_tree
    task_tree_units = [foon_functional_units[i] for i in reference_task_tree]
    
    return task_tree_units


# creates the graph using adjacency list
# each object has a list of functional list where it is an output

def read_universal_foon(filepath='FOON.pkl'):
    """
        parameters: path of universal foon (pickle file)
        returns: a map. key = object, value = list of functional units
    """
    pickle_data = pickle.load(open(filepath, 'rb'))
    functional_units = pickle_data["functional_units"]
    object_nodes = pickle_data["object_nodes"]
    object_to_FU_map = pickle_data["object_to_FU_map"]

    return functional_units, object_nodes, object_to_FU_map


# -----------------------------------------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    foon_functional_units, foon_object_nodes, foon_object_to_FU_map = read_universal_foon(
    )

    utensils = []
    with open('utensils.txt', 'r') as f:
        for line in f:
            utensils.append(line.rstrip())

    kitchen_items = json.load(open('kitchen.json'))

    goal_nodes = json.load(open("goal_nodes.json"))

    for node in goal_nodes:
        node_object = Object(node["label"])
        node_object.states = node["states"]
        node_object.ingredients = node["ingredients"]
        node_object.container = node["container"]

        for object in foon_object_nodes:
            if object.check_object_equal(node_object):
                # output_task_tree = search_BFS(kitchen_items, object)
                # save_paths_to_file(output_task_tree,
                #                    'output_BFS_{}.txt'.format(node["label"]))
                # output_task_tree = search_IDS(kitchen_items, object, 1)
                # #print("Output Task Tree:", output_task_tree)
                # save_paths_to_file(output_task_tree,
                #                    'output_IDS_{}.txt'.format(node["label"]))
                # output_task_tree1 = search_a_star(kitchen_items, object)
                # save_paths_to_file(output_task_tree1,
                #                    'output_AStar_{}.txt'.format(node["label"]))
                output_task_tree = search_mcts(kitchen_items, object, foon_object_nodes, foon_functional_units, foon_object_to_FU_map, utensils, k=1000)
                save_paths_to_file(output_task_tree, 'output_MCTS_{}.txt'.format(node["label"]))
                break
