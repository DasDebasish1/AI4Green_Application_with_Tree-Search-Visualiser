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



