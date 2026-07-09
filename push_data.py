import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL=os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)

import certifi # provides set of rules for validating the trustworthiness of SSL certificates while establishing secure connections over HTTPS.
ca = certifi.where()

import pandas as pd
import numpy as np
import pymongo
from Networksecurity.exception.exception import NetworkSecurityException
from Networksecurity.logging.logger import logging


class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    def csv_to_json_convertor(self,file_path:str)->json:
        try:
            df=pd.read_csv(file_path)
            df.reset_index(drop=True,inplace=True)
            records =  list(json.loads(df.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def insert_data_mongodb(self,records,database,collection):
        try:
            self.database = database
            self.connection = collection
            self.records = records

            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
            self.database = self.mongo_client[self.database]

            self.collection = self.database[self.connection]
            self.collection.insert_many(self.records)
            logging.info("Data inserted successfully into MongoDB")
            return (len(self.records))
        except Exception as e:
            raise NetworkSecurityException(e,sys)

if __name__=="__main__":
    FILE_PATH = "/Users/somasricharan/Network_Security/Network_Data/phisingData.csv"
    DATABASE = "SRIMAN"
    COLLECTION = "Network_Data"
    networkobj = NetworkDataExtract()
    records =networkobj.csv_to_json_convertor(FILE_PATH)
    print(records)
    no_of_records = networkobj.insert_data_mongodb(records,DATABASE,COLLECTION)
    print(no_of_records)




