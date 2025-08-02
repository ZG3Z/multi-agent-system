"""
Integration tests for CI pipeline
These tests run against the Docker Compose setup
"""
import pytest
import httpx
import asyncio

BASE_URLS = {
    "gemini": "http://localhost:8080",
    "langraph": "http://localhost:8082", 
    "adk": "http://localhost:8083"
}

@pytest.mark.integration
class TestServiceHealth:
    """Test that all services are healthy"""
    
    @pytest.mark.parametrize("service_name,base_url", BASE_URLS.items())
    async def test_service_health(self, service_name, base_url):
        """Test individual service health endpoints"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert "uptime" in data
            assert data["uptime"] >= 0

@pytest.mark.integration  
class TestServiceCapabilities:
    """Test service capabilities endpoints"""
    
    @pytest.mark.parametrize("service_name,base_url", BASE_URLS.items())
    async def test_capabilities_endpoint(self, service_name, base_url):
        """Test that capabilities endpoint returns valid data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/capabilities")
            assert response.status_code == 200
            
            capabilities = response.json()
            assert isinstance(capabilities, list)
            assert len(capabilities) > 0
            
            # Check capability structure
            for cap in capabilities:
                assert "name" in cap
                assert "description" in cap
                assert "estimated_duration" in cap

@pytest.mark.integration
class TestServiceSpecs:
    """Test service specification endpoints"""
    
    @pytest.mark.parametrize("service_name,base_url", BASE_URLS.items())
    async def test_spec_endpoint(self, service_name, base_url):
        """Test that spec endpoint returns valid data"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/spec")
            assert response.status_code == 200
            
            spec = response.json()
            assert "agent_id" in spec
            assert "agent_type" in spec
            assert "version" in spec
            assert "endpoints" in spec
            assert "supported_task_types" in spec

@pytest.mark.integration
class TestBasicTaskExecution:
    """Test basic task execution without real API keys"""
    
    async def test_gemini_agent_task_fails_gracefully(self):
        """Test that Gemini agent fails gracefully with fake API key"""
        task_request = {
            "task_type": "research",
            "description": "Test research task",
            "context": {"test": True}
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{BASE_URLS['gemini']}/execute", json=task_request)
            # Should return 200 but with error in response due to fake API key
            assert response.status_code == 200
            
            result = response.json()
            # With fake API key, should fail but handle gracefully
            assert "success" in result
            assert "execution_time" in result
    
    async def test_langraph_agent_task_fails_gracefully(self):
        """Test that LangGraph agent fails gracefully with fake API key"""
        task_request = {
            "task_type": "decision_making",
            "description": "Test decision task",
            "context": {
                "options": ["A", "B"],
                "criteria": {"test": "test"}
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{BASE_URLS['langraph']}/execute", json=task_request)
            assert response.status_code == 200
            
            result = response.json()
            assert "success" in result
            assert "execution_time" in result
    
    async def test_adk_agent_task_fails_gracefully(self):
        """Test that ADK agent fails gracefully with fake API key"""
        task_request = {
            "task_type": "data_transformation",
            "description": "Test data transformation",
            "context": {
                "data": {"test": [1, 2, 3]},
                "target_format": "json"
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{BASE_URLS['adk']}/execute", json=task_request)
            assert response.status_code == 200
            
            result = response.json()
            assert "success" in result
            assert "execution_time" in result

@pytest.mark.integration
class TestA2AEndpoints:
    """Test A2A communication endpoints exist"""
    
    @pytest.mark.parametrize("service_name,base_url", BASE_URLS.items())
    async def test_a2a_endpoint_exists(self, service_name, base_url):
        """Test that A2A endpoint exists (should return 422 for missing body)"""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/a2a/message")
            # Should return 422 (validation error) not 404
            assert response.status_code == 422

@pytest.mark.integration
@pytest.mark.slow
class TestServiceCommunication:
    """Test communication between services"""
    
    async def test_all_services_can_communicate(self):
        """Test that all services can reach each other's health endpoints"""
        # This is a basic connectivity test
        all_services_healthy = True
        
        for service_name, base_url in BASE_URLS.items():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{base_url}/health")
                    if response.status_code != 200:
                        all_services_healthy = False
                        break
            except Exception:
                all_services_healthy = False
                break
        
        assert all_services_healthy, "Not all services are reachable"