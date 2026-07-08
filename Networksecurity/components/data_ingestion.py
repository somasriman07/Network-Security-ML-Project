from Networksecurity.exception.exception import NetworkSecurityException
from Networksecurity.logging.logger import logging


from Networksecurity.entity.config_entity import DataIngestionConfig

import os
import sys
import pymongo
import pandas as pd
import numpy as np
from typing import List
from sklearn.model_selection import train_test_split
from Networksecurity.entity.artifact_entity import DataIngestionArtifact

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            logging.info(f"{'>>'*20} Data Ingestion {'<<'*20}")
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def export_collection_as_dataframe(self)->pd.DataFrame:
        """
        Export entire collection as dataframe
        return: pd.DataFrame
        """
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            logging.info(f"Exporting collection: {collection_name} from database: {database_name}")
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection = self.mongo_client[database_name][collection_name]

            df = pd.DataFrame(list(collection.find()))
            if "_id" in df.columns:
                df = df.drop("_id",axis=1)
            logging.info(f"Rows and columns in df: {df.shape}")

            df.replace({'na':np.nan},inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e,sys) 
    
    def export_data_into_feature_store(self,df:pd.DataFrame)->str:
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            logging.info(f"Exporting data into feature store: {feature_store_file_path}")
            df.to_csv(feature_store_file_path,index=False,header=True)
            return feature_store_file_path
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def split_data_as_train_test(self,df:pd.DataFrame)->None:
        try:
            train_set,test_set = train_test_split(df,test_size=self.data_ingestion_config.train_test_split_ratio,random_state=42)
            logging.info(f"Performed train test split on the dataframe")

            logging.info(
                "Exited split_data_as_train_test method of DataIngestion class"
            )
            
            dir_path = os.path.dirname(self.data_ingestion_config.train_file_path)
            os.makedirs(dir_path,exist_ok=True)
            logging.info(f"Exporting train and test file path.")

            train_set.to_csv(
                self.data_ingestion_config.train_file_path, index=False, header=True
            )
            test_set.to_csv(
                self.data_ingestion_config.test_file_path, index=False, header=True
            )
            
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def initiate_data_ingestion(self)->DataIngestionArtifact:
        try:
            dataframe = self.export_collection_as_dataframe()
            file_path = self.export_data_into_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            dataingestionartifact = DataIngestionArtifact(feature_store_file_path=file_path,
                                                          train_file_path=self.data_ingestion_config.train_file_path,
                                                          test_file_path=self.data_ingestion_config.test_file_path)
            return dataingestionartifact
        except Exception as e:
            raise NetworkSecurityException(e,sys) 

