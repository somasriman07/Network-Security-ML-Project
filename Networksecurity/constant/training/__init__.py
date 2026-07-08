import os
import sys
import pandas as pd
import numpy as np


"""
DEFING common constant variables for training pipeline
"""
TARGET_COLUMN = "Result"
PIPELINE_NAME:str = "Network_Security"
ARTIFACT_DIR:str = "artifact"
FILE_NAME:str = "phising Data.csv"

TRAIN_FILE_NAME:str = "train.csv"
TEST_FILE_NAME:str = "test.csv"


"""
 Data Ingestion related constant start with Data_ingestion var name
"""
DATA_INGESTION_COLLECTION_NAME:str = "Network_Data"
DATA_INGESTION_DATABASE_NAME:str = "SRIMAN"
DATA_INGESTION_DIR_NAME:str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR:str = "feature_store"
DATA_INGESTION_INGESTED_DIR:str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO:float = 0.2
