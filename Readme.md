## Ai4green Tree Search Visualiser

Ai4green is an electronic laboratory notebook cloud-hosted web-based application that is an open-source, free-to-use tool that fosters environmentally sustainable chemistry practices using Artificial intelligence. It is developed using **Python, Flask, JavaScript, HTML, and CSS**, featuring a **Postgres database** integrated with chemistry libraries like **RDKit for backend operations**. It provides a user-friendly front end where data is inputted through **MarvinJS or SMILES**, dynamically updates sustainability metrics via AJAX, and generates detailed reports which can be exported. It integrates digital technology with ecological responsibility, aiming to reduce the environmental footprint of chemical processes and encourage safer, more sustainable laboratory practices. It has full core functionality for synthetic organic chemistry. 
The core feature of AI4Green is the reaction builder, where users can build reactions by navigating to the workgroup and selecting ‘new reaction’. Users can then sketch the reaction using the available tools. Once components are added, the application automatically calculates sustainability metrics and health and safety information, displaying these in a Summary Table that can be exported as a PDF or printed form.

Url of AI4Green --> https://ai4green.app/

**This project was developed as part of my thesis work at the University of Nottingham. Due to the nature of the code and its academic context, the full working of the code is not available here. My contributions are specifically implemented in the file** [reaction-tree.html](https://github.com/DasDebasish1/AI4Green_Application_with_Tree-Search-Visualiser/blob/main/Ai4Green_Api/Webapp/sources/templates/reaction_tree.html), **where I worked on as mentioned below in the implementation section.**

## Implementation

### Application Overview of the Ai4green Tree Search Viewer

The ai4green app has been implemented as part of this project with an advanced feature of a retrosynthesis tree search. This powerful tool allows users to view how the target molecule is reached from the initial stage for a specified iteration. The features developed and explained below will surely help chemists and developers by giving them a comprehensive understanding of the chemical processes. 
Upon entering the AI4green Application, log in using your unique login credentials. Once you are logged in, select the Retrosynthesis tab. On the retrosynthesis page, the user needs to input the smile in the area as highlighted in green (Figure 1) and press the ‘new retrosynthesis’ button to process the smile. Additionally, the user can change the number of iterations highlighted in red below. By default, it is set to 100. Once the retrosynthesis button is clicked, the process begins. 

![Project Screenshot](https://github.com/DasDebasish1/AI4Green_Application_with_Tree-Search-Visualiser/blob/main/Picture1.png)
<p align="center">Figure 1</p>

Once the process is completed, the user can see the Tree button on the retrosynthesis page at the right-side corner, highlighted in red in Figure 2 When clicked, the Tree visualiser will open, allowing the user to view the tree search.

![Project Screenshot](https://github.com/DasDebasish1/AI4Green_Application_with_Tree-Search-Visualiser/blob/main/Picture2.png)
<p align="center">Figure 2</p>

On the tree search viewer, at the edge of each node of the tree, the reaction name is added if found in the metadata of the database or else shown as unassigned. This reaction name allows the user to identify the chemical composition quickly. The reaction name of a particular node is shown in Figure 3, highlighted in sky blue. The reaction process name is followed by pictures of chemicals ‘in stock’ and ‘not in stock’ processed using RDKit.’

![Project Screenshot](https://github.com/DasDebasish1/AI4Green_Application_with_Tree-Search-Visualiser/blob/main/Picture3.png)
<p align="center">Figure 3</p>

The retrosynthesis tree search viewer is integrated with zoom functionality to increase and decrease the canvas's zoom where the tree search is viewed. The user needs to first click on the canvas and then use the scroll of the mouse to zoom in and out of the canvas, and in case of touch, the user needs a finger touch on the canvas to zoom in and out. If the user doesn’t click on the canvas but scrolls the mouse, then the web page size will change instead of the canvas. 

The retrosynthesis tree search viewer has a slider to change the iteration. This helps the user check how MCTS expands to reach the target chemical on each iteration, as highlighted in sky blue colour in Figure 4. 
The user can also change the colour of the ‘Best solved node’, ‘Solved route node’, ’Solved Node’, ‘Unsolved Node’, and ‘Selected Node’ colour, respectively, as per requirement, using a colour picker as shown in Figure 4, highlighted in yellow.  

![Project Screenshot](https://github.com/DasDebasish1/AI4Green_Application_with_Tree-Search-Visualiser/blob/main/Picture4.png)
<p align="center">Figure 4</p>

The user can click any node of the tree viewed on the canvas. If the user selects a node from the tree, then the route from the root node to the selected node, highlighting the selected node and hiding other nodes, will be shown to the viewer. The details of the selected node’s compounds will be displayed in the upper-left side corner of the canvas with details like the Name of the compound, Molecular weight, CAS Number, and Hazard Code, as shown in Figure 5, highlighted in green. 

![Project Screenshot](https://github.com/DasDebasish1/AI4Green_Application_with_Tree-Search-Visualiser/blob/main/Picture5.png)
<p align="center">Figure 5</p>

On the right-side corner, the Condition set drop-down allows the user to pick 10 different experimental conditions. The details are in the top right corner of the Condition & Sustainability table in Figure 5. This table is followed by the step analysis table (highlighted in blue), which shows the steps of the selected route with flag colours. For instance, step 1 shows the flag colour of the last node as highlighted in red.

Details on the compounds, step analysis, condition, and sustainability tables will depend on the data availability in the database. If not available, then ‘unknown’ will be shown. For the compounds table, it will show that ‘’Compound with SMILES ‘SMILE’ is not in the database’’, as shown in the figure highlighted in orange. For the step analysis, it will show the default colour, which is ‘white’.

Users can return to the tree search main page by double-clicking on the empty area of the canvas. Additionally, it has touch capability, meaning the user can interact entirely with the Tree visualiser/viewer using a touchscreen. External hardware like a mouse or keyboard is not required.

On selecting a node, it shows three tables to view the details of the node, as seen in Figure 5, which are the following:

1.	Condition and sustainability:
In the "Condition Set" drop-down list, the user can choose (and compare up to 10 different) experimental conditions. Each condition set shows different parameters, including temperature, solvent, reagents, catalysts, and other factors.
Details of the elements in the table: -
	Likelihood Score: - This score indicates the probability or observed frequency of success for the reaction under the given conditions.
	Temperature(C): - This is the temperature at which the reaction is carried out.
	Solvents: - These are materials used to dissolve reactants. A solvent is typically a liquid substance which, when added to the reactants, the reactants, goes from being dry solids to forming solutions.
	Reagents: Each reagent is a substance required for the chemical reaction.
	Catalyst: It does not consume reagent participation but instead accelerates the rate of chemical reaction.
	Element sustainability: - Refer to the element's availability.
	Safety: - These are hazard statements according to the Globally Harmonized System. Reagents or solvents in the reaction pose various health and safety risks, such as flammability, eye and respiratory irritation, and potential carcinogenicity.
