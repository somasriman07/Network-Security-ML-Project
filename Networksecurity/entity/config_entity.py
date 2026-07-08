from datetime import datetime
import os
from Networksecurity.constant import training

print(training.PIPELINE_NAME)
print(training.ARTIFACT_DIR)

class TrainingPipelineConfig:
    def __init__(self,timestamp=datetime.now()):
        timestamp = timestamp.strftime("%m_%d_%Y_%H_%M_%S")
        self.pipeline_name = training.PIPELINE_NAME
        self.artifact_name = training.ARTIFACT_DIR
        self.artifact_dir = os.path.join(self.artifact_name,timestamp)
        self.timestamp = timestamp


class DataIngestionConfig:
    def __init__(self,training_pipeline_config:TrainingPipelineConfig):
        self.database_name = training.DATA_INGESTION_DATABASE_NAME
        self.collection_name = training.DATA_INGESTION_COLLECTION_NAME
        self.data_ingestion_dir = os.path.join(training_pipeline_config.artifact_dir,training.DATA_INGESTION_DIR_NAME)
        self.feature_store_file_path = os.path.join(self.data_ingestion_dir,training.DATA_INGESTION_FEATURE_STORE_DIR,training.FILE_NAME)
        self.ingested_dir = os.path.join(self.data_ingestion_dir,training.DATA_INGESTION_INGESTED_DIR)
        self.train_file_path = os.path.join(self.ingested_dir,training.TRAIN_FILE_NAME)
        self.test_file_path = os.path.join(self.ingested_dir,training.TEST_FILE_NAME)
        self.train_test_split_ratio = training.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO


class DataValidationConfig:
    def __init__(self,training_pipeline_config:TrainingPipelineConfig):
        self.data_validation_dir = os.path.join(training_pipeline_config.artifact_dir,training.DATA_VALIDATION_DIR_NAME)
        self.valid_data_dir = os.path.join(self.data_validation_dir,training.DATA_VALIDATION_VALID_DIR)
        self.invalid_data_dir = os.path.join(self.data_validation_dir,training.DATA_VALIDATION_INVALID_DIR)
        self.valid_train_file_path = os.path.join(self.valid_data_dir,training.TRAIN_FILE_NAME)
        self.valid_test_file_path = os.path.join(self.valid_data_dir,training.TEST_FILE_NAME)
        self.invalid_train_file_path = os.path.join(self.invalid_data_dir,training.TRAIN_FILE_NAME)
        self.invalid_test_file_path = os.path.join(self.invalid_data_dir,training.TEST_FILE_NAME)
        self.drift_report_file_path = os.path.join(self.data_validation_dir,training.DATA_VALIDATION_DRIFT_REPORT_DIR,training.DATA_VALIDATION_DRIFT_REPORT_FILE_NAME)
        
