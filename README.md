# Overview
This project maps diagnosis, medication, and clinical concepts to standard codes using open-source libraries and APIs. The code processes input data from CSV files and retrieves corresponding standard codes and labels from BioPortal and RxNav APIs. The results are saved into new CSV files.

## Prerequisites
- Python 3.x
- Required libraries: `urllib`, `json`, `csv`, `os`, `pandas`, `regex`
To install the required libraries, run:

`pip install pandas regex`

## API Information
BioPortal API: Used for mapping diagnosis and clinical concepts to SNOMEDCT and other ontologies.
Base URL: `http://data.bioontology.org`
RxNav API: Used for mapping medication concepts to RXCUI codes and their related drug classes.
Base URL: `https://rxnav.nlm.nih.gov/REST/`
Files (Data Source is private)
- Input Files:
`diagnosis_concepts.csv`: Contains diagnosis concepts.
`medications_concepts.csv`: Contains medication concepts.
`clinical_concepts_names.csv`: Contains clinical concepts.
- Output Files:
`answer_diagnosis_concepts.csv`: Contains mapped diagnosis concepts.
`answer_medication_concepts.csv`: Contains mapped medication concepts.
`answer_clinical_concepts_names.csv`: Contains mapped clinical concepts.

## Usage
Step 1: Setup
Ensure that the input CSV files (diagnosis_concepts.csv, medications_concepts.csv, clinical_concepts_names.csv) are in the same directory as the script.

Step 2: Execute the Script
Run the script to process the input data and generate the output files with mapped concepts.

Step 3: Output
The output files (answer_diagnosis_concepts.csv, answer_medication_concepts.csv, answer_clinical_concepts_names.csv) will be created in the same directory.

## Code Explanation
### Libraries
`urllib`: For making HTTP requests.
`json`: For parsing JSON data.
`csv`: For handling CSV files.
`os`: For directory operations.
`pandas`: For data manipulation.
`regex`: For regular expressions.

### Functions
`get_api_json(url)`: Fetches JSON data from the BioPortal API using the provided URL.
`get_rest_json(url)`: Fetches JSON data from the RxNav API using the provided URL.

### Diagnosis Concepts Mapping
Read the diagnosis concepts from `diagnosis_concepts.csv`.
Prepare search terms.
Fetch and map each term to its SNOMEDCT ontology.
Retrieve parent terms for hierarchical mapping.
Save the results to answer_diagnosis_concepts.csv.

### Medication Concepts Mapping
Read the medication concepts from `medications_concepts.csv`.
Clean and prepare search terms.
Fetch and map each term to its RXCUI code.
Retrieve ingredient and drug class information.
Save the results to answer_medication_concepts.csv.

### Clinical Concepts Mapping
Read the clinical concepts from `clinical_concepts_names.csv`.
Prepare search terms.
Fetch and map each term to the corresponding ontology.
Save the results to answer_clinical_concepts_names.csv.


## Notes
Ensure you have a valid API key for BioPortal.
The script assumes that the input CSV files are correctly formatted and present in the same directory.
Uncomment print statements for debugging if needed.
For further details or issues, refer to the official documentation of BioPortal API and RxNav API.
