import pickle
import json
from FOON_class import Object

# -----------------------------------------------------------------------------------------------------------------------------#

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
                output_task_tree = search_IDS(kitchen_items, object, 1)
                #print("Output Task Tree:", output_task_tree)
                save_paths_to_file(output_task_tree,
                                   'output_IDS_{}.txt'.format(node["label"]))
                output_task_tree1 = search_a_star(kitchen_items, object)
                save_paths_to_file(output_task_tree1,
                                   'output_AStar_{}.txt'.format(node["label"]))
                break
