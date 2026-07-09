from Networksecurity.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from Networksecurity.entity.config_entity import DataValidationConfig
from Networksecurity.exception.exception import NetworkSecurityException
from Networksecurity.logging.logger import logging
from Networksecurity.constant.training import SCHEMA_FILE_PATH, TARGET_COLUMN
from scipy.stats import ks_2samp
import pandas as pd
import os,sys
from Networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file

class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,data_validation_config:DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
    
    @staticmethod
    def read_data(file_path:str)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
    
    def validation_number_of_columns(self,dataframe:pd.DataFrame)->bool:
        try:
            number_of_columns = len(self._schema_config['columns'])
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Dataframe has columns: {len(dataframe.columns)}")

            if len(dataframe.columns) == number_of_columns:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e,sys) from e
    
    def validate_numerical_columns(self, dataframe: pd.DataFrame) -> bool:
        """
        Check whether all numerical columns defined in schema are present
        in the given dataframe.
        """
        try:
            numerical_columns = self._schema_config["numerical_columns"]

            missing_columns = []

            for column in numerical_columns:
                if column not in dataframe.columns:
                    missing_columns.append(column)

            if len(missing_columns) > 0:
                logging.info(f"Missing numerical columns: {missing_columns}")
                return False

            logging.info("All numerical columns are present.")
            return True

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def detect_dataset_drift(self,base_df,current_df,threshold=0.05)->bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1,d2)
                if threshold <= is_same_dist.pvalue:
                    is_found = False
                else:
                    is_found = True
                    status = False
                report.update({column:{
                    "p_value":float(is_same_dist.pvalue),
                    "drift_status":is_found
                }})
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path,exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path,content = report)
            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
    
    def handle_imbalance_with_smote(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        try:
            logging.info("Checking if imblearn library is available for SMOTE...")
            try:
                from imblearn.over_sampling import SMOTE
                imblearn_available = True
            except ImportError:
                imblearn_available = False
                logging.info("imblearn library is not installed. Skipping SMOTE oversampling.")
                return dataframe

            if imblearn_available:
                if TARGET_COLUMN not in dataframe.columns:
                    logging.warning(f"Target column '{TARGET_COLUMN}' not found in dataframe. Skipping SMOTE.")
                    return dataframe

                # Check if there is actual imbalance in target column
                class_counts = dataframe[TARGET_COLUMN].value_counts()
                logging.info(f"Class distribution before SMOTE: {dict(class_counts)}")

                if len(class_counts) > 1 and class_counts.min() < class_counts.max():
                    logging.info("Applying SMOTE to balance target class distribution...")
                    X = dataframe.drop(columns=[TARGET_COLUMN])
                    y = dataframe[TARGET_COLUMN]

                    smote = SMOTE(random_state=42)
                    X_resampled, y_resampled = smote.fit_resample(X, y)

                    resampled_df = pd.DataFrame(X_resampled, columns=X.columns)
                    resampled_df[TARGET_COLUMN] = y_resampled
                    
                    logging.info(f"Class distribution after SMOTE: {dict(resampled_df[TARGET_COLUMN].value_counts())}")
                    return resampled_df
                else:
                    logging.info("Data is already balanced or has less than 2 classes. Skipping SMOTE.")
                    return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            # Read data
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)

            # Validate number of columns
            status = self.validation_number_of_columns(train_dataframe)
            if not status:
                raise Exception("Train dataframe does not contain all the required columns")

            status = self.validation_number_of_columns(test_dataframe)
            if not status:
                raise Exception("Test dataframe does not contain all the required columns")

            # Validate numerical columns
            status = self.validate_numerical_columns(train_dataframe)
            if not status:
                raise Exception("Train dataframe does not contain all required numerical columns")

            status = self.validate_numerical_columns(test_dataframe)
            if not status:
                raise Exception("Test dataframe does not contain all required numerical columns")
            
            # Let's check data drift

            status = self.detect_dataset_drift(base_df = train_dataframe,current_df = test_dataframe)

            # Apply SMOTE to handle imbalance on train data if imblearn exists
            train_dataframe = self.handle_imbalance_with_smote(train_dataframe)

            dir_path = os.path.dirname(self.data_validation_config.valid_test_file_path)
            os.makedirs(dir_path,exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path,index=False,header=True
            )
            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path,index=False,header=True
            )
            data_validation_artifact = DataValidationArtifact(
                validation_status = status,
                valid_train_file_path = self.data_validation_config.valid_train_file_path,
                valid_test_file_path = self.data_validation_config.valid_test_file_path,
                invalid_train_file_path = self.data_validation_config.invalid_train_file_path,
                invalid_test_file_path = self.data_validation_config.invalid_test_file_path,
                drift_report_file_path = self.data_validation_config.drift_report_file_path
            )
            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e