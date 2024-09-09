# Project 1: Knowledge Retrieval (part - 1)

## Introduction

This project is a **Functional Object-Oriented Network (FOON)** based recipe planner. It allows users to input goal objects, such as dishes they want to create, and searches for a sequence of actions to achieve that goal using predefined kitchen items, utensils, and a list of ingredients. The program generates an output that outlines the task sequence required to reach the desired goal, saved in a `.txt` file.

## Features

- Load and process a FOON graph from a text file.
- Specify goal objects (e.g., dishes or foods), their states, ingredients, and containers.
- Perform a breadth-first search (BFS) through FOON nodes to find a sequence of steps required to achieve the goal.
- Save the generated task tree to an output file.

## Ensure the following files are present in the working directory:

- **FOON.txt**: A file that contains the FOON graph.
- **ingredients.txt**: A file containing the list of ingredients for the goal object.
- **utensils.txt**: A file listing the available kitchen utensils.
- **kitchen.json**: A JSON file containing the kitchen items.

## Usage

To run the program, follow these steps:

1. **Run the main script**:
   ```bash
   python test_script.py
   ```

### Follow the prompts:

1. Enter the path to the FOON file - i.e, FOON.txt
2. Enter the goal object’s name - i.e, greek salad
3. Enter the goal object’s state(s) (comma-separated if multiple) - i.e, mixed
4. Enter the path to the ingredients file - i.e, `ingredients.txt`
5. Enter the name of the container required for the goal object - i.e, mixing bowl

Once the process is completed, the system will search for the goal object and its matching sequence in the FOON graph. It generates an output task tree saved in a `.txt` file containing the recipe steps.
