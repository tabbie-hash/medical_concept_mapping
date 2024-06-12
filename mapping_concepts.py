#LIBRARIES
import urllib.request, urllib.error, urllib.parse
import json
import csv
import os
import pandas as pd
import regex as re
pd.options.mode.chained_assignment = None

#USING THIS OPEN-SOURCE LIBRARY AS IT'S WAS QUICK WITH REGISTRATION UNLIKE UMLS 
BIO_URL = "http://data.bioontology.org"    
#you may replace this with your api key from the bioportal account        
BIO_API_KEY = "48f59bb6-62d2-4fe6-b7df-b293e4d79a70"        
RX_URL = 'https://rxnav.nlm.nih.gov/REST/'
directory = os.path.dirname(os.path.abspath(__file__))

#MAPPING DIAGNOSIS CONCEPTS:

#THIS FUCTION FETCHES JSON FORMAT DATA FROM BIO URL USING BIO API KEY
def get_api_json(url):        
    req = urllib.request.build_opener()
    req.addheaders = [('Authorization', 'apikey token=' + BIO_API_KEY)]
    return json.loads(req.open(url).read())

# Get list of search terms
ddf = pd.read_csv(directory+'/diagnosis_concepts.csv')
dtm = list(ddf['source_display'])
dterms =[]
for x in dtm:
    #MAKING SEARCH TERMS URL READABLE FORMAT
    s = x.replace(' ','%20')   
    dterms.append(s)

# Do a search for every term and add results to the dataframe
tg_dp = []
tg_cd=[]
tg_tp=[]
prnt_dp=[]
prnt_cd=[]
prnt_tp =[]
for term in dterms:
    #MAPPING DIAGNOSIS TERMS TO IT'S SNOMEDCT ONTOLOGY
    dg_dict = get_api_json(BIO_URL + "/search?q=" +term+'&ontologies=SNOMEDCT')["collection"]   
    d = dg_dict[0]
    # print(d)            #uncomment this to print the json data fetched in dg_dict
    tg_dp.append(d['prefLabel'])     #TARGET NAME
    tg_cd.append(d['@id'].split('/')[-1])   #TARGET CODE
    tg_tp.append(d['@id'].split('/')[-2])   #TARGET CODE TYPE

    #FILTERING OUT JSON URLS OF THE PARENTS OF THE TERMS
    prnt = d['links']['parents']   
    #FETCHING JSON DATA ON THE PARENTS    
    prnt_jsn = get_api_json(prnt) 
    #FIRST PARENT (HEIRARCIAL BROADER TERM) ROLLING UP    
    prnt_sub_dict =prnt_jsn[0]        
    # print(prnt_sub_dict)            #uncomment this to print the json data fetched in prnt_sub_dict
    prnt_dp.append(prnt_sub_dict['prefLabel'])    #PARENT NAME
    prnt_cd.append(prnt_sub_dict['@id'].split('/')[-1])   #PARENT CODE
    prnt_tp.append(prnt_sub_dict['@id'].split('/')[-2])   #PARENT CODE TYPE

ddf['target_system'] = tg_tp
ddf['target_code'] = tg_cd
ddf['target_display'] = tg_dp
ddf['rollup_system'] = prnt_tp
ddf['rollup_code'] = prnt_cd
ddf['rollup_display'] = prnt_dp
   
ddf.to_csv(directory+'/answer_diagnosis_concepts.csv', index=False)    #ANSWER FILE

#MAPPING MEDICATION CONCEPTS:

#THIS FUNCTION GETS DATA IN JSON DICTIONARY FORM USING REST API URL NOT REQUIRING AUTHORIZATION
def get_rest_json(url):        
    req = urllib.request.build_opener()
    return json.loads(req.open(url).read())

# Get list of search terms
mdf = pd.read_csv(directory+'/medications_concepts.csv')
cln_mdf = mdf[['source_system','source_code','source_display']]    #FILTERING DESIRED DATA
mtm = list(cln_mdf['source_display'])
mterms =[]
for term in mtm:
    #REMOVING THE STUFF BETWEEN BRACKETS (TEXT CLEANING)
    cln = re.sub('\[[^\]]*\]','', term) 
    #MAKING THE TERMS IN URL READABLE FORMAT 
    srch = cln.replace(' ', '%20')       
    mterms.append(srch)

ing_dp=[]
ing_cd =[]
ing_tp=[]
drg_cls_dp=[]
drg_cls_cd=[]
drg_cls_tp=[]
for strm in mterms:
    #FETCHING JSON DATA USING MEDICATION NAMES THROUGH APPROXIMATE TERM MATCHING 
    rx_dict = get_rest_json(RX_URL+'approximateTerm.json?term='+strm)     
    # print(rx_dict)           #uncomment this to print the json data fetched in rx_dict
    #FETCHING THE RXCUI CODES OF THE MEDICATIONS
    rxcui = rx_dict['approximateGroup']['candidate'][0]['rxcui'] 
    #MAPPING TO THE INGREDIENTS OF THE MEDICATIONS THROUGH THEIR RXCUI CODES   
    his_dict = get_rest_json(RX_URL+'rxcui/'+rxcui+'/historystatus.json')        
    # print(his_dict)         #uncomment this to print the json data fetched in his_dict
    ing_lbl_lst = his_dict['rxcuiStatusHistory']['derivedConcepts']['ingredientConcept']
     #MAPPING TO VA CLASS(ONCOLOGY RELEVANT CLASS) OF THE MEDICATIONS USING THEIR RXCUI CODES    
    drg_cls_dict = get_rest_json(RX_URL+'rxclass/class/byRxcui.json?rxcui='+rxcui+'&relaSource=VA&relas=has_VAClass')   
    # print(drg_cls_dict)     #uncomment this to print the json data fetched in dg_cls_dict
    drg_cls_lst = drg_cls_dict['rxclassDrugInfoList']['rxclassDrugInfo'][0]['rxclassMinConceptItem']
    for i in ing_lbl_lst:
        ing_dp.append(i['ingredientName'])    #INGREDIENT NAME
        ing_cd.append(i['ingredientRxcui'])     #INGREDIENT CODE
    ing_tp.append(his_dict['rxcuiStatusHistory']['metaData']['source'])   #INGREDIENT CODE TYPE

    drg_cls_dp.append(drg_cls_lst['className'])   #MEDICATION CLASS NAME
    drg_cls_cd.append(drg_cls_lst['classId'])     #MEDICATION CLASS CODE
    drg_cls_tp.append(drg_cls_lst['classType'])   #MEDICATION CLASS CODE TYPE

cln_mdf['target_system'] = ing_tp
cln_mdf['target_code'] = ing_cd
cln_mdf['target_display'] = ing_dp
cln_mdf['drug_class_system'] = drg_cls_tp
cln_mdf['drug_class_code'] = drg_cls_cd
cln_mdf['drug_class_display'] = drg_cls_dp

cln_mdf.to_csv(directory+'/answer_medication_concepts.csv', index=False)  #ANSWER FILE

#MAPPING CLINICAL CONCEPTS TO STANDARD CODES:
cdf = pd.read_csv(directory+'/clinical_concepts_names.csv')
ctm = list(cdf['source_display'])
cterms =[]
for c in ctm:
    #MAKING THE SEARCH TERMS IN THE URL READABLE FORMAT
    a = c.replace(' ','%20')     
    cterms.append(a)

cc_dp=[]
cc_cd=[]
cc_tp =[]
for ccm in cterms:
    #FETCHING THE DATA IN JSON DICTIONARY FORM BASED ON SEARCH TERMS FROM INPUT DATA
    cc_dict = get_api_json(BIO_URL + "/search?q=" +ccm)["collection"]  
    #CHOOSING THE TOP RESULT/FIRST RESULT    
    cc_st = cc_dict[0]                          
    # print(cc_st)   #uncomment this to print the json data fetched in cc_dict
    cc_dp.append(cc_st['prefLabel'])            #TARGET DISPLAY NAME
    if cc_st['@id'].split('/')[-2] == 'EVS':
        cc_cd.append(cc_st['@id'].split('#')[-1])   #TARGET CODE NUMBER
        cc_tp.append('NCI EVS')                     #TARGET CODE SYSTEM
    else:
        cc_cd.append(cc_st['@id'].split('/')[-1])    #TARGET CODE NUMBER
        cc_tp.append(cc_st['@id'].split('/')[-2])    #TARGET CODE SYSTEM

cdf['target_system'] = cc_tp
cdf['target_code'] = cc_cd
cdf['target_display'] = cc_dp

cdf.to_csv(directory+'/answer_clinical_concepts_names.csv', index=False)   #ANSWER FILE
    