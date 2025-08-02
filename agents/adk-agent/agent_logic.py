import asyncio
import time
import json
import pandas as pd
import numpy as np
from scipy import stats
import google.generativeai as genai
from typing import Dict, Any, List
from models import TaskType, AgentCapability
from config import Config

class ADKLogic:
    def __init__(self):
        try:
            if not Config.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
            # Configure Gemini for insights
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
            
            self.capabilities = self._define_capabilities()
            
            print(f"ADK agent initialized with Gemini model: {Config.GEMINI_MODEL}")
            
        except Exception as e:
            print(f"ADK initialization failed: {e}")
            raise
    
    def _define_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="data_transformation",
                description="Transform data between formats and structures",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_type": {"type": "string", "enum": ["data_transformation"]},
                        "description": {"type": "string"},
                        "data": {"type": "object"},
                        "target_format": {"type": "string"},
                        "transformations": {"type": "array"}
                    },
                    "required": ["task_type", "description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "transformed_data": {"type": "object"},
                        "transformation_summary": {"type": "string"},
                        "data_shape": {"type": "object"}
                    }
                },
                estimated_duration=60
            ),
            AgentCapability(
                name="data_analysis",
                description="Perform statistical analysis and generate insights",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_type": {"type": "string", "enum": ["data_analysis"]},
                        "description": {"type": "string"},
                        "data": {"type": "object"},
                        "analysis_type": {"type": "string"}
                    },
                    "required": ["task_type", "description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "statistics": {"type": "object"},
                        "insights": {"type": "string"},
                        "visualizations": {"type": "array"}
                    }
                },
                estimated_duration=120
            ),
            AgentCapability(
                name="data_validation",
                description="Validate data quality, integrity, and completeness",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_type": {"type": "string", "enum": ["data_validation"]},
                        "description": {"type": "string"},
                        "data": {"type": "object"},
                        "validation_rules": {"type": "object"}
                    },
                    "required": ["task_type", "description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "validation_results": {"type": "object"},
                        "quality_score": {"type": "number"},
                        "issues_found": {"type": "array"}
                    }
                },
                estimated_duration=90
            ),
            AgentCapability(
                name="data_aggregation",
                description="Aggregate and summarize datasets",
                input_schema={
                    "type": "object",
                    "properties": {
                        "task_type": {"type": "string", "enum": ["data_aggregation"]},
                        "description": {"type": "string"},
                        "data": {"type": "object"},
                        "groupby_columns": {"type": "array"},
                        "aggregation_functions": {"type": "object"}
                    },
                    "required": ["task_type", "description"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "aggregated_data": {"type": "object"},
                        "summary_stats": {"type": "object"},
                        "group_insights": {"type": "string"}
                    }
                },
                estimated_duration=75
            )
        ]
    
    async def execute_task(self, task_type: TaskType, description: str, 
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            print(f"Executing {task_type.value} task: {description[:100]}...")
            
            if task_type == TaskType.DATA_TRANSFORMATION:
                result = await self._data_transformation_task(description, context)
            elif task_type == TaskType.DATA_ANALYSIS:
                result = await self._data_analysis_task(description, context)
            elif task_type == TaskType.DATA_VALIDATION:
                result = await self._data_validation_task(description, context)
            elif task_type == TaskType.DATA_AGGREGATION:
                result = await self._data_aggregation_task(description, context)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
            
            execution_time = time.time() - start_time
            print(f"Task completed in {execution_time:.2f}s")
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "task_type": task_type.value
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            print(f"Task failed after {execution_time:.2f}s: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "execution_time": execution_time,
                "task_type": task_type.value,
                "result": {}
            }
    
    async def _data_transformation_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Transform data between formats"""
        
        try:
            data = context.get("data", {}) if context else {}
            target_format = context.get("target_format", "json") if context else "json"
            transformations = context.get("transformations", []) if context else []
            
            # Create sample data if none provided
            if not data:
                data = {
                    "records": [
                        {"id": 1, "name": "Alice", "age": 30, "score": 85.5},
                        {"id": 2, "name": "Bob", "age": 25, "score": 92.3},
                        {"id": 3, "name": "Charlie", "age": 35, "score": 78.9}
                    ]
                }
            
            # Convert to DataFrame for processing
            if "records" in data:
                df = pd.DataFrame(data["records"])
            else:
                df = pd.DataFrame([data])
            
            original_shape = df.shape
            
            # Apply transformations
            for transformation in transformations:
                if transformation == "normalize_columns":
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].mean()) / df[numeric_cols].std()
                elif transformation == "remove_nulls":
                    df = df.dropna()
                elif transformation == "uppercase_strings":
                    string_cols = df.select_dtypes(include=['object']).columns
                    df[string_cols] = df[string_cols].astype(str).apply(lambda x: x.str.upper())
            
            # Transform to target format
            if target_format == "json":
                transformed_data = df.to_dict('records')
            elif target_format == "csv":
                transformed_data = df.to_csv(index=False)
            elif target_format == "summary":
                transformed_data = {
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.to_dict(),
                    "sample": df.head().to_dict('records')
                }
            else:
                transformed_data = df.to_dict('records')
            
            # Generate AI insights about transformation
            prompt = f"""
            Data Transformation Analysis:
            
            Task: {description}
            Original shape: {original_shape}
            Final shape: {df.shape}
            Transformations applied: {transformations}
            Target format: {target_format}
            
            Provide insights about this data transformation including:
            1. What transformations were successful
            2. Impact on data quality
            3. Recommendations for further processing
            """
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            insights = response.text if response.text else "Transformation completed successfully"
            
            return {
                "transformed_data": transformed_data,
                "transformation_summary": insights,
                "data_shape": {
                    "original": list(original_shape),
                    "final": list(df.shape)
                },
                "transformations_applied": transformations,
                "target_format": target_format
            }
            
        except Exception as e:
            return {
                "transformed_data": {},
                "transformation_summary": f"Transformation failed: {str(e)}",
                "data_shape": {"original": [0, 0], "final": [0, 0]},
                "error": str(e)
            }
    
    async def _data_analysis_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform statistical analysis"""
        
        try:
            data = context.get("data", {}) if context else {}
            analysis_type = context.get("analysis_type", "descriptive") if context else "descriptive"
            
            # Create sample data if none provided
            if not data:
                np.random.seed(42)
                data = {
                    "values": np.random.normal(100, 15, 1000).tolist(),
                    "categories": (np.random.choice(['A', 'B', 'C'], 1000)).tolist(),
                    "timestamps": pd.date_range('2024-01-01', periods=1000, freq='H').strftime('%Y-%m-%d %H:%M:%S').tolist()
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Perform statistical analysis
            statistics = {}
            
            # Basic statistics
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                statistics["descriptive"] = df[numeric_cols].describe().to_dict()
                statistics["correlation"] = df[numeric_cols].corr().to_dict() if len(numeric_cols) > 1 else {}
            
            # Advanced analysis based on type
            if analysis_type == "hypothesis_testing" and len(numeric_cols) > 0:
                col = numeric_cols[0]
                t_stat, p_value = stats.ttest_1samp(df[col].dropna(), df[col].mean())
                statistics["t_test"] = {"t_statistic": t_stat, "p_value": p_value}
            
            elif analysis_type == "distribution" and len(numeric_cols) > 0:
                col = numeric_cols[0]
                data_values = df[col].dropna()
                statistics["distribution"] = {
                    "skewness": stats.skew(data_values),
                    "kurtosis": stats.kurtosis(data_values),
                    "normality_test": stats.normaltest(data_values)._asdict()
                }
            
            # Generate AI insights
            prompt = f"""
            Data Analysis Results:
            
            Task: {description}
            Analysis type: {analysis_type}
            Dataset shape: {df.shape}
            Statistics: {json.dumps(statistics, default=str)}
            
            Provide insights including:
            1. Key findings from the analysis
            2. Statistical significance of results
            3. Business implications
            4. Recommendations for action
            """
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            insights = response.text if response.text else "Analysis completed successfully"
            
            return {
                "statistics": statistics,
                "insights": insights,
                "data_shape": list(df.shape),
                "analysis_type": analysis_type,
                "visualizations": ["histogram", "correlation_matrix", "box_plot"]  # Placeholder for viz recommendations
            }
            
        except Exception as e:
            return {
                "statistics": {},
                "insights": f"Analysis failed: {str(e)}",
                "data_shape": [0, 0],
                "error": str(e)
            }
    
    async def _data_validation_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate data quality"""
        
        try:
            data = context.get("data", {}) if context else {}
            validation_rules = context.get("validation_rules", {}) if context else {}
            
            # Create sample data if none provided
            if not data:
                data = {
                    "records": [
                        {"id": 1, "email": "alice@example.com", "age": 30, "score": 85.5},
                        {"id": 2, "email": "invalid-email", "age": -5, "score": 150.0},
                        {"id": None, "email": "charlie@example.com", "age": 35, "score": None}
                    ]
                }
            
            # Convert to DataFrame
            try:
                if "records" in data:
                    df = pd.DataFrame(data["records"])
                else:
                    df = pd.DataFrame([data])
            except Exception as e:
                return {
                    "validation_results": {},
                    "quality_score": 0.0,
                    "issues_found": [f"Failed to create DataFrame: {str(e)}"],
                    "error": str(e)
                }
            
            # Validation results
            issues_found = []
            validation_results = {}
            
            try:
                # Check for missing values
                missing_counts = df.isnull().sum()
                validation_results["missing_values"] = {str(k): int(v) for k, v in missing_counts.items()}
                if missing_counts.sum() > 0:
                    issues_found.append(f"Found {int(missing_counts.sum())} missing values")
            except Exception as e:
                issues_found.append(f"Missing values check failed: {str(e)}")
            
            try:
                # Check for duplicates
                duplicate_count = df.duplicated().sum()
                validation_results["duplicates"] = int(duplicate_count)
                if duplicate_count > 0:
                    issues_found.append(f"Found {duplicate_count} duplicate rows")
            except Exception as e:
                issues_found.append(f"Duplicate check failed: {str(e)}")
            
            try:
                # Data type validation
                validation_results["data_types"] = {str(k): str(v) for k, v in df.dtypes.items()}
            except Exception as e:
                issues_found.append(f"Data type check failed: {str(e)}")
            
            # Custom validation rules - with better error handling
            try:
                for rule_name, rule_config in validation_rules.items():
                    if rule_name == "email_format" and "email" in df.columns:
                        try:
                            # Handle NaN values in email column
                            email_series = df["email"].fillna("").astype(str)
                            invalid_emails = ~email_series.str.contains("@", na=False)
                            invalid_count = int(invalid_emails.sum())
                            validation_results["email_validation"] = {
                                "invalid_count": invalid_count,
                                "invalid_emails": email_series[invalid_emails].tolist()
                            }
                            if invalid_count > 0:
                                issues_found.append(f"Found {invalid_count} invalid email formats")
                        except Exception as e:
                            issues_found.append(f"Email validation failed: {str(e)}")
                    
                    elif rule_name == "age_range" and "age" in df.columns:
                        try:
                            min_age = rule_config.get("min", 0)
                            max_age = rule_config.get("max", 120)
                            # Handle NaN values in age column
                            age_series = df["age"].fillna(-999)  # Use sentinel value for NaN
                            invalid_ages = (age_series < min_age) | (age_series > max_age)
                            invalid_count = int(invalid_ages.sum())
                            validation_results["age_validation"] = {
                                "invalid_count": invalid_count,
                                "out_of_range_ages": [float(x) if pd.notna(x) else None for x in age_series[invalid_ages].tolist()]
                            }
                            if invalid_count > 0:
                                issues_found.append(f"Found {invalid_count} ages outside valid range")
                        except Exception as e:
                            issues_found.append(f"Age validation failed: {str(e)}")
            except Exception as e:
                issues_found.append(f"Custom validation failed: {str(e)}")
            
            # Calculate quality score
            try:
                total_cells = df.size
                missing_sum = sum(validation_results.get("missing_values", {}).values())
                duplicate_count = validation_results.get("duplicates", 0)
                quality_score = max(0, (total_cells - missing_sum - duplicate_count) / total_cells) if total_cells > 0 else 0
            except Exception as e:
                quality_score = 0.0
                issues_found.append(f"Quality score calculation failed: {str(e)}")
            
            # Generate AI insights
            try:
                prompt = f"""
                Data Validation Report:
                
                Task: {description}
                Dataset shape: {df.shape}
                Issues found: {issues_found}
                Quality score: {quality_score:.2f}
                
                Provide recommendations for:
                1. Data quality improvements
                2. How to fix identified issues
                3. Prevention strategies
                4. Impact assessment
                """
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(prompt)
                )
                
                insights = response.text if response.text else "Validation completed successfully"
            except Exception as e:
                insights = f"AI insights generation failed: {str(e)}"
            
            return {
                "validation_results": validation_results,
                "quality_score": round(float(quality_score), 3),
                "issues_found": issues_found,
                "recommendations": insights,
                "data_shape": list(df.shape)
            }
            
        except Exception as e:
            print(f"Validation task error: {str(e)}")  # Server-side logging
            return {
                "validation_results": {},
                "quality_score": 0.0,
                "issues_found": [f"Validation failed: {str(e)}"],
                "error": str(e)
            }
    
    async def _data_aggregation_task(self, description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Aggregate and summarize data"""
        
        try:
            data = context.get("data", {}) if context else {}
            groupby_columns = context.get("groupby_columns", []) if context else []
            aggregation_functions = context.get("aggregation_functions", {}) if context else {}
            
            # Create sample data if none provided
            if not data:
                np.random.seed(42)
                categories = ["Electronics", "Clothing", "Books"]
                regions = ["North", "South", "East", "West"]
                records = []
                for i in range(100):  # Create 100 sample records
                    records.append({
                        "category": np.random.choice(categories),
                        "region": np.random.choice(regions),
                        "sales": np.random.randint(100, 1000),
                        "quantity": np.random.randint(1, 50)
                    })
                data = {"records": records}
            
            # Convert to DataFrame
            if "records" in data:
                df = pd.DataFrame(data["records"])
            else:
                df = pd.DataFrame([data])
            
            # Default groupby and aggregation if not specified
            if not groupby_columns and len(df.columns) > 0:
                # Use categorical columns for grouping
                categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
                groupby_columns = categorical_cols[:2] if categorical_cols else []
            
            if not aggregation_functions and len(df.columns) > 0:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    aggregation_functions = {col: ['sum', 'mean', 'count'] for col in numeric_cols}
            
            # Perform aggregation
            aggregated_data = {}
            summary_stats = {}
            
            if groupby_columns and any(col in df.columns for col in groupby_columns):
                # Filter valid groupby columns
                valid_groupby = [col for col in groupby_columns if col in df.columns]
                
                if valid_groupby:
                    grouped = df.groupby(valid_groupby)
                    
                    # Apply aggregation functions
                    for col, funcs in aggregation_functions.items():
                        if col in df.columns:
                            if isinstance(funcs, list):
                                for func in funcs:
                                    agg_result = getattr(grouped[col], func)()
                                    aggregated_data[f"{col}_{func}"] = agg_result.to_dict()
                            else:
                                agg_result = getattr(grouped[col], funcs)()
                                aggregated_data[f"{col}_{funcs}"] = agg_result.to_dict()
                    
                    # Summary statistics
                    summary_stats = {
                        "group_count": grouped.size().to_dict(),
                        "total_records": len(df),
                        "groups": len(grouped)
                    }
            else:
                # Overall aggregation without grouping
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    aggregated_data[col] = {
                        "sum": df[col].sum(),
                        "mean": df[col].mean(),
                        "count": df[col].count(),
                        "min": df[col].min(),
                        "max": df[col].max()
                    }
                
                summary_stats = {
                    "total_records": len(df),
                    "numeric_columns": len(numeric_cols)
                }
            
            # Generate AI insights
            prompt = f"""
            Data Aggregation Results:
            
            Task: {description}
            Dataset shape: {df.shape}
            Groupby columns: {groupby_columns}
            Aggregation functions: {aggregation_functions}
            Summary stats: {json.dumps(summary_stats, default=str)}
            
            Provide insights about:
            1. Key patterns in the aggregated data
            2. Notable trends or outliers
            3. Business insights from the groupings
            4. Recommendations for further analysis
            """
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            insights = response.text if response.text else "Aggregation completed successfully"
            
            return {
                "aggregated_data": aggregated_data,
                "summary_stats": summary_stats,
                "group_insights": insights,
                "groupby_columns": groupby_columns,
                "data_shape": list(df.shape)
            }
            
        except Exception as e:
            return {
                "aggregated_data": {},
                "summary_stats": {},
                "group_insights": f"Aggregation failed: {str(e)}",
                "error": str(e)
            }
    
    def get_capabilities(self) -> List[AgentCapability]:
        return self.capabilities