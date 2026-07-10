from Networksecurity.components.data_ingestion import DataIngestion
from Networksecurity.components.data_validation import DataValidation
from Networksecurity.components.data_transformation import DataTransformation
from Networksecurity.components.model_trainer import ModelTrainer
from Networksecurity.exception.exception import NetworkSecurityException
from Networksecurity.logging.logger import logging
import sys
from Networksecurity.entity.config_entity import DataIngestionConfig,TrainingPipelineConfig,DataValidationConfig,DataTransformationConfig
from Networksecurity.entity.config_entity import ModelTrainerConfig

if __name__=='__main__': 
    try:
        training_pipeline_config = TrainingPipelineConfig()
        dataingestionconfig = DataIngestionConfig(training_pipeline_config=training_pipeline_config)
        data_ingestion = DataIngestion(dataingestionconfig)
        logging.info("Initiate the data ingestion")
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data Initiation Completed ")
        print(data_ingestion_artifact)
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact ,data_validation_config)
        logging.info("Initiate the data validation")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("data validation Completed")
        print(data_validation_artifact)
        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        logging.info("Data Transformation Started")
        data_transformation = DataTransformation(data_validation_artifact,data_transformation_config)
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info("Data Transformation Completed")

        logging.info("Model Training started")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config)
        model_trainer = ModelTrainer(model_trainer_config=model_trainer_config,data_transformation_artifact=data_transformation_artifact)
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logging.info("Model Training artifacr created")

        # Syncing local artifacts and final model to S3
        from Networksecurity.constant.training import TRAINING_BUCKET_NAME
        from Networksecurity.cloud.s3_syncer import S3Sync
        
        logging.info("Syncing artifacts and models to S3 bucket...")
        s3_sync = S3Sync()
        
        # Sync artifacts
        aws_bucket_url_artifact = f"s3://{TRAINING_BUCKET_NAME}/artifact/{training_pipeline_config.timestamp}"
        s3_sync.sync_folder_to_s3(folder=training_pipeline_config.artifact_dir, aws_bucket_url=aws_bucket_url_artifact)
        
        # Sync final model
        aws_bucket_url_model = f"s3://{TRAINING_BUCKET_NAME}/final_model/{training_pipeline_config.timestamp}"
        s3_sync.sync_folder_to_s3(folder=training_pipeline_config.model_dir, aws_bucket_url=aws_bucket_url_model)
        logging.info("S3 sync completed successfully!")


     

        
    except Exception as e:
           raise NetworkSecurityException(e,sys)