# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 15:05:27 2022

data handler for Unified Medical Language System (UMLS)
https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.

--- record example ---
C0001041|ENG|P|L0001041|PF|S0414245|N|A31756755|12252053|194||RXNORM|IN|194|acetylcholine|0|N|4352|

  Col.	    Description
- CUI	    Unique identifier for concept
- LAT	    Language of term
- TS	    Term status
- LUI	    Unique identifier for term
- STT	    String type
- SUI	    Unique identifier for string
- ISPREF	Atom status - preferred (Y) or not (N) for this string within this concept
- AUI	    Unique identifier for atom - variable length field, 8 or 9 characters
- SAUI	    Source asserted atom identifier [optional]
- SCUI	    Source asserted concept identifier [optional]
- SDUI	    Source asserted descriptor identifier [optional]
- SAB	    Abbreviated source name (SAB). Official source names, RSABs, and VSABs are included on the UMLS Source Vocabulary Documentation page.
- TTY	    Abbreviation for term type in source vocabulary. Possible values are listed on the Abbreviations Used in Data Elements page.
- CODE	    Most useful source asserted identifier (if the source vocabulary has more than one identifier), or a Metathesaurus-generated source entry identifier
- STR	    String
- SRL	    Source restriction level
- SUPPRESS	Suppressible flag. Values = O, E, Y, or N
- CVF	    Content View Flag. Bit field used to flag rows included in Content View. This field is a varchar field to maximize the number of bits available for use.

@author: I.Azuma
"""
import pandas as pd
from tqdm import tqdm
import codecs
from collections import defaultdict

class Target2CUI():
    def __init__(self,mrconso_path='D:/GdriveSymbol/datasource/UMLS/rrf/MRCONSO.RRF'):
        self.mrconso_path = mrconso_path # The most widely used UMLS file
    
    def set_target(self,name="RXNORM",candi_path='./data/target_candi.pkl',target_check=True):
        if target_check:
            target_candi = pd.read_pickle(candi_path)
            if name in target_candi:
                self.target_name = name
                print("Nice ! ^^")
            else:
                print(target_candi)
                raise ValueError("!! Inappropriate target SAB ; Choose from above list !!")
        else:
            print("Could not set correctly ^^;")
            self.target_name = name
        print("Target name:",self.target_name)
    
    def narrow_lines(self,host="localhost",port=27017,dbname="umls"):
        #client = MongoClient(host=host, port=port)
        #db = client.get_database(dbname)
        
        self.target_records = []
        self.num_lines = 0
        for record in tqdm(codecs.open(self.mrconso_path,'r','utf-8','ignore')):
            #print(record)
            split = record.strip().split("|")
            if self.target_name in split:
                self.target_records.append(record)
            self.num_lines += 1
        print("--- extract target records ---")
        print(len(self.target_records),"/",self.num_lines,"records were extracted")

    def create_dic(self):
        """
        creat dictionary for name identifier
        name2cui : {"C0000473":{'4-aminobenzoic acid', 'aminobenzoic acid'},...} e.g. compound name in RxNorm to UMLS CUI
        code2cui : {"C0000473":{'74'},...} e.g. RxNorm CUI to UMLS CUI
        """
        self.cui = []
        self.name = []
        self.code = []
        self.name2cui = defaultdict(set)
        self.code2cui = defaultdict(set)
        for t in tqdm(self.target_records):
            split = t.strip().split("|")
            self.cui.append(split[0])
            self.name.append(split[14])
            self.code.append(split[13])
            self.name2cui[split[0]].add(split[14])
            self.code2cui[split[0]].add(split[13])
        #self.name2cui = dict(zip(self.name,self.cui))
        #self.code2cui = dict(zip(self.code,self.cui))
    
    def get_codeinfo(self,codeID="'D008103'"):
        tmp = list(self.code2cui.items())
        target_CUI = []
        for i in range(len(tmp)):
            if codeID in  tmp[i][1]:
                print(tmp[i])
                target_CUI.append(tmp[i][0])
        target_name = [self.name2cui.get(k) for k in target_CUI]
        print("--- Result ---")
        print("query =",codeID)
        print("UMLS CUI:",target_CUI)
        print("name:",target_name)
        
