# Integrated Retrosynthesis and Sustainability Assessment Documentation

# Table of Contents

1. [Introduction](#introduction)
2. [Workflow](#workflow)
3. [Retrosynthesis](#retrosynthesis)
   1. [SMILES Validation](#smiles-validation)
   2. [API Request](#api-request)
   3. [Data Structure](#data-structure)
   4. [Cytoscape Visualisation](#cytoscape-visualisation)
4. [Conditions](#conditions)
   1. [API Request](#conditions-api-request)
   2. [Response Handler](#response-handler)
   3. [Data Structure](#conditions-data-structure)
5. [Sustainability Assessment](#sustainability-assessment)
   1. [Assess Metrics](#assess-metrics)
   2. [Weighted Medians](#weighted-medians)
   3. [Data Structure](#sustainability-data-structure)
6. [Database Save](#database-save)
   1. [Data Structure](#database-object-structure)
   2. [Reload](#reload)
7. [Export to Reaction](#export-to-reaction)
8. [Tables](#tables)
   1. [Conditions](#conditions-table)
   2. [Route](#route-table)
      1. [General](#general)
      2. [Sustainability](#sustainability)
   3. [Compounds](#compounds-table)

## 1. <a id="introduction"> Introduction </a>
This module is an addition to the core of the AI4Green Electronic Laboratory Notebook Web Application.

The module contains code to produce a web page that provides an interactive environment for chemists to use the 
retrosynthesis tool, AiZynthFinder. Conditions are predicted using a module of ASKCOS. Sustainability assessments are
 performed using metrics from CHEM21 and median values are weighted by the value of the sliders.

There are also features to export a reaction to the sketcher and save a retrosynthesis to the database.

This code is implemented using many Plotly-Dash components. Including the fusion of the dash app object into the
main Flask web application.

## 2. <a id="workflow"> Workflow </a>
The workflow for this module reads as follows:
1) Submit SMILES string to retrosynthesis API
2) Retrosynthesis API processes the results to return a list of routes
3) These routes are stored in '<i>computed-retrosynthesis-routes</i>'
4) For every reaction step, in every route, 10 condition sets are predicted: temperature, catalyst, reagent, solvent, likelihood score.
5) These predictions are stored in '<i>computed-conditions-data</i>'
6) For each condition set, a sustainability assessment is performed.
7) The sustainability assessment data is stored in '<i>computed-sustainability-data</i>'
8) A weighted median is calculated for 1) Each route. 2) Each reaction step.
9) The weights of each sustainability metric are determined by the sliders on the frontend.
10) The weighted sustainability assessment is stored in '<i>weighted-sustainability-data</i>'

## 3. <a id="retrosynthesis"> Retrosynthesis </a>
Retrosynthesis takes a SMILES string from the user, validates it, and then sends it to the retrosynthesis API which uses
AiZynthFinder, a template-based multi-step retrosynthetic planner trained on USPTO data, to generate up to 10
retrosynthetic routes, of no more than 7 steps each.

The resultant list is converted into a series of nodes connected by edges in a tree-layout with the target molecule at 
the top. Dash-cytoscape is used to perform this.

### 3.1. <a id="smiles-validation"> SMILES Validation </a>
Content for the SMILES Validation goes here.

### 3.2. <a id="api-request"> API Request </a>
Content for the API Request goes here.

### 3.3. <a id="data-structure"> Data Structure </a>

The retrosynthesis routes are received and stored as a dictionary where Route X is one key in a dictionary.
```
{"Route X":
   {
       "score": float,
       "steps": list,
         [
            {
               "node_id": string,
               "smiles": string,
               "node": dict,
               "depth": int,
               "parent": dict,
               "parent_smiles": string,
               "child_smiles": list,
               "reaction_class": list
            },
         ]
    },    
```


### 3.4. <a id="cytoscape-visualisation"> Cytoscape Visualisation </a>
Content for the Cytoscape Visualisation goes here.

## 4. <a id="conditions"> Conditions </a>
Content for the Conditions goes here.

### 4.1. <a id="conditions-api-request"> API Request </a>
Content for the API Request goes here.

### 4.2. <a id="response-handler"> Response Handler </a>
Content for the Response Handler goes here.

### 4.3. <a id="conditions-data-structure"> Data Structure </a>
The conditions data are received and stored as a list of ten items, where an example item is shown below. Each item in the list is 
a dictionary. Smiles strings use a '.' delimiter. 

```
['Route-X:
   [
      {'node-0': 
         [
            {
                "score": float,
                "temperature": float,
                "solvent": smiles_string
                "catalyst": smiles_string
                "reagents": smiles_string
             },    
         ]
      }
   ]
]
```

## 5. <a id="sustainability-assessment"> Sustainability Assessment </a>
Content for the Sustainability Assessment goes here.

### 5.1. <a id="assess-metrics"> Assess Metrics </a>
Content for the Assess Metrics goes here.

### 5.2. <a id="weighted-medians"> Weighted Medians </a>
Content for the Weighted Medians goes here.

### 5.3. <a id="sustainability-data-structure"> Data Structure </a>
The retrosynthesis routes are received and stored as a dictionary where Route X is one key in a dictionary.
```
{"Route X":
   {
       "steps": list,
       "average_sustainability": dict
    },    
```

## 6. <a id="database-save"> Database Save </a>
Content for the Database Save goes here.

### 6.1. <a id="database-object-structure"> Data Structure </a>
Content for the Data Structure goes here.

### 6.2. <a id="reload"> Reload </a>
Content for the Reload goes here.

## 7. <a id="export-to-reaction"> Export to Reaction </a>
Content for the Export to Reaction goes here.

## 8. <a id="tables"> Tables </a>
Content for the Tables goes here.

### 8.1. <a id="conditions-table"> Conditions </a>
Content for the Conditions Table goes here.

### 8.2. <a id="route-table"> Route </a>
Content for the Route Table goes here.

#### 8.2.1. <a id="general"> General </a>
Content for the General Route Table goes here.

#### 8.2.2. <a id="sustainability"> Sustainability </a>
Content for the Sustainability Route Table goes here.

### 8.3. <a id="compounds-table"> Compounds </a>
Content for the Compounds Table goes here.
