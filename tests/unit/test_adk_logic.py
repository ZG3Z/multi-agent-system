"""
Unit tests for ADK Agent Logic
Tests business logic without Docker containers or real API calls
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
import pandas as pd
import numpy as np

# Add agent path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../agents/adk-agent'))

from agent_logic import ADKLogic
from models import TaskType

class TestADKLogic:
    """Test ADK business logic without external dependencies"""
    
    @pytest.fixture
    def mock_gemini_response(self):
        """Mock Gemini API response"""
        mock_response = Mock()
        mock_response.text = "Mock AI insight: Data transformation completed successfully"
        return mock_response
    
    @pytest.fixture
    def adk_logic(self, mock_gemini_response):
        """Create ADK logic instance with mocked Gemini"""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel') as mock_model:
            
            # Mock the model and its generate_content method
            mock_instance = Mock()
            mock_instance.generate_content.return_value = mock_gemini_response
            mock_model.return_value = mock_instance
            
            # Mock environment variables
            with patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake-key'}):
                logic = ADKLogic()
                return logic
    
    def test_capabilities_loading(self, adk_logic):
        """Test that capabilities are loaded correctly"""
        capabilities = adk_logic.get_capabilities()
        
        assert len(capabilities) == 4
        capability_names = [cap.name for cap in capabilities]
        
        assert "data_transformation" in capability_names
        assert "data_analysis" in capability_names
        assert "data_validation" in capability_names
        assert "data_aggregation" in capability_names
        
        # Check capability structure
        for cap in capabilities:
            assert hasattr(cap, 'name')
            assert hasattr(cap, 'description')
            assert hasattr(cap, 'estimated_duration')
            assert cap.estimated_duration > 0

class TestDataTransformation:
    """Test data transformation logic"""
    
    @pytest.fixture
    def adk_logic(self):
        """Create ADK logic with mocked dependencies"""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'), \
             patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake-key'}):
            return ADKLogic()
    
    @pytest.mark.asyncio
    async def test_data_transformation_basic(self, adk_logic):
        """Test basic data transformation without API calls"""
        
        # Mock the Gemini API call
        with patch.object(adk_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Transformation completed successfully"
            mock_generate.return_value = mock_response
            
            # Test data
            context = {
                "data": {
                    "records": [
                        {"id": 1, "name": "Alice", "score": 85.5},
                        {"id": 2, "name": "Bob", "score": 92.3}
                    ]
                },
                "target_format": "json",
                "transformations": ["normalize_columns"]
            }
            
            result = await adk_logic.execute_task(
                TaskType.DATA_TRANSFORMATION, 
                "Transform test data", 
                context
            )
            
            assert result["success"] is True
            assert "result" in result
            assert "transformed_data" in result["result"]
            assert "data_shape" in result["result"]
            assert result["result"]["target_format"] == "json"
    
    @pytest.mark.asyncio
    async def test_data_transformation_with_sample_data(self, adk_logic):
        """Test transformation when no data provided (uses sample data)"""
        
        with patch.object(adk_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Sample data transformation completed"
            mock_generate.return_value = mock_response
            
            result = await adk_logic.execute_task(
                TaskType.DATA_TRANSFORMATION, 
                "Transform sample data"
            )
            
            assert result["success"] is True
            assert "transformed_data" in result["result"]
            # Should use sample data with Alice, Bob, Charlie
            assert len(result["result"]["transformed_data"]) == 3

class TestDataAnalysis:
    """Test data analysis logic"""
    
    @pytest.fixture
    def adk_logic(self):
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'), \
             patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake-key'}):
            return ADKLogic()
    
    @pytest.mark.asyncio
    async def test_data_analysis_with_numeric_data(self, adk_logic):
        """Test statistical analysis with numeric data"""
        
        with patch.object(adk_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Statistical analysis shows normal distribution"
            mock_generate.return_value = mock_response
            
            # Test with controlled data
            context = {
                "data": {
                    "values": [1, 2, 3, 4, 5],
                    "categories": ["A", "A", "B", "B", "C"]
                },
                "analysis_type": "descriptive"
            }
            
            result = await adk_logic.execute_task(
                TaskType.DATA_ANALYSIS,
                "Analyze test data",
                context
            )
            
            assert result["success"] is True
            assert "statistics" in result["result"]
            assert "descriptive" in result["result"]["statistics"]
            
            # Check that basic stats are calculated
            descriptive_stats = result["result"]["statistics"]["descriptive"]
            assert "values" in descriptive_stats
            assert "count" in descriptive_stats["values"]
            assert "mean" in descriptive_stats["values"]

class TestDataValidation:
    """Test data validation logic"""
    
    @pytest.fixture
    def adk_logic(self):
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'), \
             patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake-key'}):
            return ADKLogic()
    
    @pytest.mark.asyncio
    async def test_data_validation_missing_values(self, adk_logic):
        """Test detection of missing values"""
        
        with patch.object(adk_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Data quality issues detected"
            mock_generate.return_value = mock_response
            
            # Data with missing values
            context = {
                "data": {
                    "records": [
                        {"id": 1, "name": "Alice", "score": 85},
                        {"id": None, "name": "Bob", "score": None},  # Missing values
                        {"id": 3, "name": None, "score": 92}
                    ]
                }
            }
            
            result = await adk_logic.execute_task(
                TaskType.DATA_VALIDATION,
                "Validate data quality",
                context
            )
            
            assert result["success"] is True
            assert "validation_results" in result["result"]
            assert "missing_values" in result["result"]["validation_results"]
            assert "quality_score" in result["result"]
            
            # Should detect missing values
            missing_values = result["result"]["validation_results"]["missing_values"]
            assert any(count > 0 for count in missing_values.values())
    
    @pytest.mark.asyncio 
    async def test_data_validation_custom_rules(self, adk_logic):
        """Test custom validation rules"""
        
        with patch.object(adk_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Validation completed with custom rules"
            mock_generate.return_value = mock_response
            
            context = {
                "data": {
                    "records": [
                        {"email": "valid@example.com", "age": 25},
                        {"email": "invalid-email", "age": -5},  # Invalid data
                        {"email": "also@valid.com", "age": 35}
                    ]
                },
                "validation_rules": {
                    "email_format": True,
                    "age_range": {"min": 0, "max": 120}
                }
            }
            
            result = await adk_logic.execute_task(
                TaskType.DATA_VALIDATION,
                "Validate with custom rules",
                context
            )
            
            assert result["success"] is True
            validation_results = result["result"]["validation_results"]
            
            # Should detect email validation issues
            if "email_validation" in validation_results:
                assert "invalid_count" in validation_results["email_validation"]
            
            # Should detect age validation issues  
            if "age_validation" in validation_results:
                assert "invalid_count" in validation_results["age_validation"]

class TestDataAggregation:
    """Test data aggregation logic"""
    
    @pytest.fixture
    def adk_logic(self):
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'), \
             patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake-key'}):
            return ADKLogic()
    
    @pytest.mark.asyncio
    async def test_data_aggregation_groupby(self, adk_logic):
        """Test groupby aggregation"""
        
        with patch.object(adk_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Aggregation completed successfully"
            mock_generate.return_value = mock_response
            
            context = {
                "data": {
                    "records": [
                        {"category": "A", "sales": 100, "quantity": 10},
                        {"category": "A", "sales": 150, "quantity": 15},
                        {"category": "B", "sales": 200, "quantity": 20}
                    ]
                },
                "groupby_columns": ["category"],
                "aggregation_functions": {
                    "sales": ["sum", "mean"],
                    "quantity": ["sum"]
                }
            }
            
            result = await adk_logic.execute_task(
                TaskType.DATA_AGGREGATION,
                "Aggregate by category",
                context
            )
            
            assert result["success"] is True
            assert "aggregated_data" in result["result"]
            assert "summary_stats" in result["result"]
            
            # Check that aggregations were performed
            aggregated_data = result["result"]["aggregated_data"]
            assert "sales_sum" in aggregated_data
            assert "sales_mean" in aggregated_data
            assert "quantity_sum" in aggregated_data

class TestErrorHandling:
    """Test error handling in ADK logic"""
    
    @pytest.fixture
    def adk_logic(self):
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'), \
             patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake-key'}):
            return ADKLogic()
    
    @pytest.mark.asyncio
    async def test_invalid_task_type(self, adk_logic):
        """Test handling of invalid task type"""
        
        # Mock TaskType with invalid value to test the else branch
        class MockTaskType:
            value = "invalid_task"
            
        mock_task_type = MockTaskType()
        
        result = await adk_logic.execute_task(mock_task_type, "test")
        
        assert result["success"] is False
        assert "error" in result
        assert "Unsupported task type" in result["error"]
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, adk_logic):
        """Test handling of API errors"""
        
        # Mock API to raise exception during the _data_transformation_task
        with patch.object(adk_logic, '_data_transformation_task') as mock_task:
            mock_task.side_effect = Exception("API Error")
            
            result = await adk_logic.execute_task(
                TaskType.DATA_TRANSFORMATION,
                "Test with API error"
            )
            
            assert result["success"] is False
            assert "error" in result
            assert "API Error" in result["error"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])