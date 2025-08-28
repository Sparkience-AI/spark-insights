from smolagents import Tool
import pandas as pd
import os
import chardet

class FileHandlerTool(Tool):
    name = "file_handler"
    description = "Load, validate, and preprocess data files (CSV/Excel). Detect encoding, validate format, and prepare data for analysis."
    inputs = {
        "file_path": {
            "type": "string",
            "description": "Path to the data file (CSV/Excel) to load and process"
        }
    }
    output_type = "object"

    def forward(self, file_path: str):
        """Load and preprocess data file, returning the DataFrame"""
        try:
            # Detect file extension
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.csv':
                df = self._load_csv_with_encoding_detection(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")

            # Basic data validation and cleaning
            print(f"✅ Data loaded successfully from {file_path}")
            print(f"   Shape: {df.shape[0]} rows, {df.shape[1]} columns")
            print(f"   Columns: {list(df.columns)}")
            print(f"   Data types: {df.dtypes.to_dict()}")

            # Handle missing values
            if df.isnull().sum().sum() > 0:
                print(f"   Missing values found: {df.isnull().sum().sum()} total")
                # Fill numeric columns with mean, categorical with mode
                for col in df.columns:
                    if df[col].dtype in ['int64', 'float64']:
                        df[col].fillna(df[col].mean(), inplace=True)
                    else:
                        df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown', inplace=True)
                print("   Missing values handled")

            # Convert date columns if they exist
            for col in df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        print(f"   Converted {col} to datetime")
                    except:
                        pass

            return df

        except Exception as e:
            print(f"❌ Error loading file: {str(e)}")
            raise e

    def _load_csv_with_encoding_detection(self, file_path: str) -> pd.DataFrame:
        """Load CSV file with automatic encoding detection"""
        # List of encodings to try in order of preference
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']

        # First, try to detect encoding using chardet
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                detected = chardet.detect(raw_data)
                if detected['encoding'] and detected['confidence'] > 0.7:
                    encodings_to_try.insert(0, detected['encoding'])
                    print(f"   Detected encoding: {detected['encoding']} (confidence: {detected['confidence']:.2f})")
        except Exception as e:
            print(f"   Encoding detection failed: {e}")

        # Try each encoding until one works
        for encoding in encodings_to_try:
            try:
                print(f"   Trying encoding: {encoding}")
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"   ✅ Successfully loaded with {encoding} encoding")
                return df
            except UnicodeDecodeError:
                print(f"   ❌ Failed with {encoding} encoding")
                continue
            except Exception as e:
                print(f"   ❌ Error with {encoding}: {e}")
                continue

        # If all encodings fail, try with error handling
        try:
            print("   Trying with error handling (errors='ignore')")
            df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
            print("   ✅ Loaded with error handling")
            return df
        except Exception as e:
            print(f"   ❌ All encoding attempts failed: {e}")
            raise ValueError(f"Unable to read CSV file with any encoding. Last error: {e}")
