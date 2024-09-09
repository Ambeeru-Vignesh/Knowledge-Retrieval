import json
from FOON_class import Object
from preprocess import create_graph
from search import read_universal_foon, save_paths_to_file, search_BFS

if __name__ == '__main__':
  
    # Prompt the user for file paths
    foon_file = input("Enter the path to the FOON file (e.g., 'FOON.txt'): ")
    # Create the graph from the FOON file
    create_graph(foon_file=foon_file)
    goal_name = input("Enter the goal object name: ")
    goal_state = input("Enter the goal object state (comma-separated if multiple): ").split(',')
    ingredients_file = input("Enter the path to the ingredients items file ")

    # Read the universal FOON data
    foon_functional_units, foon_object_nodes, foon_object_to_FU_map = read_universal_foon()
    print(f"FOON data loaded. Functional units: {len(foon_functional_units)}, Object nodes: {len(foon_object_nodes)}")

    # Load utensils
    utensils = []
    with open('utensils.txt', 'r') as f:
        utensils = [line.strip() for line in f]

    # Load kitchen items
    kitchen_items = json.load(open('kitchen.json'))

    # Load ingredients
    ingredients = list();
    with open(ingredients_file, 'r') as f:
        for line in f:
            ingredients.append(line.rstrip())


    container = input("Enter the container: ")
    # Create the goal object
    goal_object = Object(goal_name)
    goal_object.states = goal_state
    goal_object.ingredients = ingredients
    goal_object.container = container

    # Search for the goal object in the FOON nodes
    for object in foon_object_nodes:
        if object.check_object_equal(goal_object):
            output_task_tree = search_BFS(
                kitchen_items,
                object,
                foon_object_nodes,
                foon_functional_units,
                foon_object_to_FU_map,
                utensils
            )
            save_paths_to_file(output_task_tree, 'output_BFS_{}.txt'.format(goal_name))
            break
