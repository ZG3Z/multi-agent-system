"""
Unit tests for CrewAI Agent Logic (Gemini)
Tests business logic without Docker containers or real API calls
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

# Add agent path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../agents/crewai-agent'))

# Mock environment before imports
with patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake-test-key'}):
    from agent_logic import CrewAILogic
    from models import TaskType

class TestCrewAILogic:
    """Test CrewAI business logic without external dependencies"""
    
    @pytest.fixture
    def mock_gemini_response(self):
        """Mock Gemini API response"""
        mock_response = Mock()
        mock_response.text = "Mock Gemini response: Task completed successfully"
        return mock_response
    
    @pytest.fixture
    def crewai_logic(self, mock_gemini_response):
        """Create CrewAI logic instance with mocked Gemini"""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel') as mock_model:
            
            # Mock the model and its generate_content method
            mock_instance = Mock()
            mock_instance.generate_content.return_value = mock_gemini_response
            mock_model.return_value = mock_instance
            
            logic = CrewAILogic()
            return logic
    
    def test_capabilities_loading(self, crewai_logic):
        """Test that capabilities are loaded correctly"""
        capabilities = crewai_logic.get_capabilities()
        
        assert len(capabilities) == 2  # research and analysis (from your code)
        capability_names = [cap.name for cap in capabilities]
        
        assert "research" in capability_names
        assert "analysis" in capability_names
        
        # Check capability structure
        for cap in capabilities:
            assert hasattr(cap, 'name')
            assert hasattr(cap, 'description')
            assert hasattr(cap, 'estimated_duration')
            assert cap.estimated_duration > 0

class TestResearchTask:
    """Test research task logic"""
    
    @pytest.fixture
    def crewai_logic(self):
        """Create CrewAI logic with mocked dependencies"""
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'):
            return CrewAILogic()
    
    @pytest.mark.asyncio
    async def test_research_task_basic(self, crewai_logic):
        """Test basic research task"""
        
        # Mock the Gemini API call
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Research findings: AI trends show significant growth in 2024"
            mock_generate.return_value = mock_response
            
            result = await crewai_logic.execute_task(
                TaskType.RESEARCH, 
                "Research AI trends in 2024",
                {"focus": "enterprise adoption"}
            )
            
            assert result["success"] is True
            assert "result" in result
            assert "findings" in result["result"]
            assert "summary" in result["result"]
            assert "sources" in result["result"]
            assert result["result"]["sources"] == ["Gemini AI Research"]
    
    @pytest.mark.asyncio
    async def test_research_task_with_context(self, crewai_logic):
        """Test research task with specific context"""
        
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Enterprise AI adoption shows 300% growth"
            mock_generate.return_value = mock_response
            
            context = {"focus": "enterprise", "industry": "finance"}
            
            result = await crewai_logic.execute_task(
                TaskType.RESEARCH,
                "Research enterprise AI adoption",
                context
            )
            
            assert result["success"] is True
            assert "findings" in result["result"]
            assert len(result["result"]["findings"]) > 0
            
            # Check that prompt included context
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args[0][0]
            assert "enterprise" in call_args.lower()
            assert "finance" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_research_task_no_context(self, crewai_logic):
        """Test research task without context"""
        
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Research completed without specific context"
            mock_generate.return_value = mock_response
            
            result = await crewai_logic.execute_task(
                TaskType.RESEARCH,
                "General research task"
            )
            
            assert result["success"] is True
            assert "raw_output" in result["result"]
            
            # Check that prompt handled missing context
            call_args = mock_generate.call_args[0][0]
            assert "No additional context provided" in call_args

class TestAnalysisTask:
    """Test analysis task logic"""
    
    @pytest.fixture
    def crewai_logic(self):
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'), \
             patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake-key'}):
            return CrewAILogic()
    
    @pytest.mark.asyncio
    async def test_analysis_task_basic(self, crewai_logic):
        """Test basic analysis task"""
        
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Analysis shows strong correlation between variables"
            mock_generate.return_value = mock_response
            
            result = await crewai_logic.execute_task(
                TaskType.ANALYSIS,
                "Analyze market trends",
                {"data_source": "quarterly_reports"}
            )
            
            assert result["success"] is True
            assert "analysis" in result["result"]
            assert "insights" in result["result"]
            assert "recommendations" in result["result"]
            assert result["result"]["insights"] == ["Analysis completed using Gemini AI"]
    
    @pytest.mark.asyncio
    async def test_analysis_task_comprehensive(self, crewai_logic):
        """Test comprehensive analysis with detailed context"""
        
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Detailed analysis reveals three key insights: 1) Growth trend, 2) Market shift, 3) Opportunity areas"
            mock_generate.return_value = mock_response
            
            context = {
                "timeframe": "Q1-Q4 2024",
                "metrics": ["revenue", "user_growth", "retention"],
                "competitors": ["CompanyA", "CompanyB"]
            }
            
            result = await crewai_logic.execute_task(
                TaskType.ANALYSIS,
                "Comprehensive market analysis",
                context
            )
            
            assert result["success"] is True
            assert "raw_output" in result["result"]
            
            # Verify context was used in prompt
            call_args = mock_generate.call_args[0][0]
            assert "Q1-Q4 2024" in call_args
            assert "revenue" in call_args

class TestPlanningTask:
    """Test planning task logic"""
    
    @pytest.fixture
    def crewai_logic(self):
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'), \
             patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake-key'}):
            return CrewAILogic()
    
    @pytest.mark.asyncio
    async def test_planning_task_basic(self, crewai_logic):
        """Test basic planning task"""
        
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Strategic plan: Phase 1 - Analysis, Phase 2 - Implementation, Phase 3 - Review"
            mock_generate.return_value = mock_response
            
            result = await crewai_logic.execute_task(
                TaskType.PLANNING,
                "Create product launch plan",
                {"timeline": "6 months", "budget": "100k"}
            )
            
            assert result["success"] is True
            assert "plan" in result["result"]
            assert "action_items" in result["result"]
            assert "timeline" in result["result"]
            assert result["result"]["timeline"] == "See plan for timeline details"
    
    @pytest.mark.asyncio
    async def test_planning_task_strategic(self, crewai_logic):
        """Test strategic planning with complex requirements"""
        
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Strategic roadmap includes resource allocation, risk mitigation, and success metrics"
            mock_generate.return_value = mock_response
            
            context = {
                "scope": "enterprise_deployment",
                "stakeholders": ["engineering", "marketing", "sales"],
                "constraints": ["budget", "timeline", "resources"]
            }
            
            result = await crewai_logic.execute_task(
                TaskType.PLANNING,
                "Enterprise deployment strategy",
                context
            )
            
            assert result["success"] is True
            assert "raw_output" in result["result"]
            
            # Check context usage
            call_args = mock_generate.call_args[0][0]
            assert "enterprise_deployment" in call_args
            assert "engineering" in call_args

class TestWritingTask:
    """Test writing task logic"""
    
    @pytest.fixture
    def crewai_logic(self):
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'), \
             patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake-key'}):
            return CrewAILogic()
    
    @pytest.mark.asyncio
    async def test_writing_task_basic(self, crewai_logic):
        """Test basic writing task"""
        
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "This is a well-structured article about artificial intelligence and its impact on modern business."
            mock_generate.return_value = mock_response
            
            result = await crewai_logic.execute_task(
                TaskType.WRITING,
                "Write article about AI in business",
                {"tone": "professional", "length": "medium"}
            )
            
            assert result["success"] is True
            assert "content" in result["result"]
            assert "word_count" in result["result"]
            assert "type" in result["result"]
            assert result["result"]["type"] == "written_content"
            assert result["result"]["word_count"] > 0
    
    @pytest.mark.asyncio
    async def test_writing_task_with_requirements(self, crewai_logic):
        """Test writing task with specific requirements"""
        
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Executive summary: Key findings and strategic recommendations for Q4 planning."
            mock_generate.return_value = mock_response
            
            context = {
                "audience": "executives",
                "format": "executive_summary",
                "key_points": ["growth", "efficiency", "innovation"]
            }
            
            result = await crewai_logic.execute_task(
                TaskType.WRITING,
                "Executive summary for board meeting",
                context
            )
            
            assert result["success"] is True
            assert result["result"]["word_count"] > 0
            
            # Verify requirements were included
            call_args = mock_generate.call_args[0][0]
            assert "executives" in call_args
            assert "growth" in call_args

class TestErrorHandling:
    """Test error handling in CrewAI logic"""
    
    @pytest.fixture
    def crewai_logic(self):
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'), \
             patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake-key'}):
            return CrewAILogic()
    
    @pytest.mark.asyncio
    async def test_invalid_task_type(self, crewai_logic):
        """Test handling of invalid task type"""
        
        # Mock TaskType with invalid value
        class MockTaskType:
            value = "invalid_task"
            
        mock_task_type = MockTaskType()
        
        result = await crewai_logic.execute_task(mock_task_type, "test")
        
        assert result["success"] is False
        assert "error" in result
        assert "Unsupported task type" in result["error"]
    
    @pytest.mark.asyncio
    async def test_gemini_api_error(self, crewai_logic):
        """Test handling of Gemini API errors"""
        
        # Mock API to raise exception
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_generate.side_effect = Exception("Gemini API Error")
            
            result = await crewai_logic.execute_task(
                TaskType.RESEARCH,
                "Test with API error"
            )
            
            assert result["success"] is False
            assert "error" in result
            assert "Gemini API Error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_empty_response_handling(self, crewai_logic):
        """Test handling of empty API responses"""
        
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = None  # Empty response
            mock_generate.return_value = mock_response
            
            result = await crewai_logic.execute_task(
                TaskType.RESEARCH,
                "Test with empty response"
            )
            
            assert result["success"] is True
            # Should handle empty response gracefully
            assert "findings" in result["result"]

class TestPromptGeneration:
    """Test prompt generation for different tasks"""
    
    @pytest.fixture
    def crewai_logic(self):
        with patch('google.generativeai.configure'), \
             patch('google.generativeai.GenerativeModel'), \
             patch.dict(os.environ, {'GOOGLE_API_KEY': 'fake-key'}):
            return CrewAILogic()
    
    @pytest.mark.asyncio
    async def test_research_prompt_structure(self, crewai_logic):
        """Test that research prompts have correct structure"""
        
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Research response"
            mock_generate.return_value = mock_response
            
            await crewai_logic.execute_task(
                TaskType.RESEARCH,
                "Test research",
                {"focus": "AI trends"}
            )
            
            # Check prompt structure
            call_args = mock_generate.call_args[0][0]
            assert "Act as a senior researcher" in call_args
            assert "Test research" in call_args
            assert "AI trends" in call_args
            assert "Key findings and insights" in call_args
    
    @pytest.mark.asyncio
    async def test_analysis_prompt_structure(self, crewai_logic):
        """Test that analysis prompts have correct structure"""
        
        with patch.object(crewai_logic.model, 'generate_content') as mock_generate:
            mock_response = Mock()
            mock_response.text = "Analysis response"
            mock_generate.return_value = mock_response
            
            await crewai_logic.execute_task(
                TaskType.ANALYSIS,
                "Test analysis",
                {"data": "sample"}
            )
            
            call_args = mock_generate.call_args[0][0]
            assert "Act as a senior data analyst" in call_args
            assert "Test analysis" in call_args
            assert "Detailed analysis" in call_args
            assert "Actionable recommendations" in call_args

if __name__ == "__main__":
    pytest.main([__file__, "-v"])