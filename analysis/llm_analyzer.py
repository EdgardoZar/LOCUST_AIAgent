"""
LLM-based analyzer for intelligent test result analysis.
"""
import json
import logging
import os
from typing import Dict, List, Any, Optional
import requests
from dataclasses import asdict


class LLMAnalyzer:
    """
    LLM-based analyzer for intelligent test result analysis.
    
    This class provides intelligent analysis of test results using LLM APIs
    to generate human-readable insights and recommendations.
    """
    
    def __init__(self, api_key: str = None, api_endpoint: str = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM analyzer.
        
        Args:
            api_key: API key for the LLM service (OpenAI, Azure, etc.)
            api_endpoint: API endpoint URL
            model: Model name to use for analysis
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.api_endpoint = api_endpoint or "https://api.openai.com/v1/chat/completions"
        self.model = model
        
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key:
            self.logger.warning("No API key provided. LLM analysis will be disabled.")
    
    def analyze_test_results(self, test_result: Dict[str, Any], html_report_path: str = None) -> Dict[str, Any]:
        """
        Analyze test results using LLM.
        
        Args:
            test_result: Test result data
            html_report_path: Path to HTML report file
            
        Returns:
            Dictionary with LLM analysis
        """
        if not self.api_key:
            return self._fallback_analysis(test_result)
        
        try:
            # Prepare context for LLM
            context = self._prepare_context(test_result, html_report_path)
            
            # Generate prompt
            prompt = self._generate_analysis_prompt(context)
            
            # Call LLM
            response = self._call_llm(prompt)
            
            # Parse response
            analysis = self._parse_llm_response(response)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"LLM analysis failed: {e}")
            return self._fallback_analysis(test_result)
    
    def _prepare_context(self, test_result: Dict[str, Any], html_report_path: str = None) -> Dict[str, Any]:
        """Prepare context for LLM analysis."""
        context = {
            "scenario_name": test_result.get("scenario_name", "Unknown"),
            "success": test_result.get("success", False),
            "execution_time": test_result.get("execution_time", 0),
            "total_requests": test_result.get("total_requests", 0),
            "failed_requests": test_result.get("failed_requests", 0),
            "avg_response_time": test_result.get("avg_response_time", 0),
            "requests_per_sec": test_result.get("requests_per_sec", 0),
            "error_message": test_result.get("error_message", ""),
            "log_output": test_result.get("log_output", [])
        }
        
        # Add HTML report content if available
        if html_report_path:
            try:
                with open(html_report_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    # Extract key metrics from HTML
                    context["html_metrics"] = self._extract_html_metrics(html_content)
            except Exception as e:
                self.logger.warning(f"Could not read HTML report: {e}")
        
        return context
    
    def _extract_html_metrics(self, html_content: str) -> Dict[str, Any]:
        """Extract key metrics from HTML report."""
        metrics = {}
        
        try:
            # Look for common patterns in Locust HTML reports
            import re
            
            # Extract response time percentiles
            percentile_pattern = r'"response_time_percentile_0\.(\d+)":\s*(\d+\.?\d*)'
            percentiles = re.findall(percentile_pattern, html_content)
            if percentiles:
                metrics["percentiles"] = {f"p{int(p)*10}": float(v) for p, v in percentiles}
            
            # Extract request statistics
            stats_pattern = r'"avg_response_time":\s*(\d+\.?\d*)'
            match = re.search(stats_pattern, html_content)
            if match:
                metrics["avg_response_time"] = float(match.group(1))
            
            # Extract failure rate
            failure_pattern = r'"num_failures":\s*(\d+)'
            match = re.search(failure_pattern, html_content)
            if match:
                metrics["failures"] = int(match.group(1))
            
        except Exception as e:
            self.logger.warning(f"Error extracting HTML metrics: {e}")
        
        return metrics
    
    def _generate_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Generate analysis prompt for LLM."""
        prompt = f"""
You are a performance testing expert analyzing the results of a Locust load test. Please provide a comprehensive analysis of the following test results:

Test Scenario: {context['scenario_name']}
Test Success: {context['success']}
Execution Time: {context['execution_time']:.2f} seconds
Total Requests: {context['total_requests']}
Failed Requests: {context['failed_requests']}
Average Response Time: {context['avg_response_time']:.2f} ms
Requests per Second: {context['requests_per_sec']:.2f}

Error Message: {context['error_message']}

Please provide:
1. A summary of the test results
2. Performance assessment (Excellent/Good/Acceptable/Poor)
3. Key insights about the system's performance
4. Specific recommendations for improvement
5. Any potential issues or concerns
6. Business impact assessment

Format your response as JSON with the following structure:
{{
    "summary": "Brief summary of test results",
    "performance_grade": "EXCELLENT|GOOD|ACCEPTABLE|POOR",
    "key_insights": ["insight1", "insight2", ...],
    "recommendations": ["recommendation1", "recommendation2", ...],
    "issues": ["issue1", "issue2", ...],
    "business_impact": "Assessment of business impact",
    "next_steps": ["step1", "step2", ...]
}}
"""
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a performance testing expert."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        response = requests.post(self.api_endpoint, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback: create structured response from text
                return {
                    "summary": response,
                    "performance_grade": "UNKNOWN",
                    "key_insights": [],
                    "recommendations": [],
                    "issues": [],
                    "business_impact": "Unable to assess",
                    "next_steps": []
                }
        except Exception as e:
            self.logger.error(f"Error parsing LLM response: {e}")
            return {
                "summary": response,
                "performance_grade": "UNKNOWN",
                "key_insights": [],
                "recommendations": [],
                "issues": [],
                "business_impact": "Unable to assess",
                "next_steps": []
            }
    
    def _fallback_analysis(self, test_result: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when LLM is not available."""
        success_rate = 0.0
        if test_result.get("total_requests", 0) > 0:
            success_rate = ((test_result["total_requests"] - test_result.get("failed_requests", 0)) / test_result["total_requests"]) * 100
        
        # Determine performance grade
        if test_result.get("success", False):
            if success_rate >= 99.5 and test_result.get("avg_response_time", 0) < 200:
                grade = "EXCELLENT"
            elif success_rate >= 99.0 and test_result.get("avg_response_time", 0) < 500:
                grade = "GOOD"
            elif success_rate >= 95.0:
                grade = "ACCEPTABLE"
            else:
                grade = "POOR"
        else:
            grade = "FAILED"
        
        return {
            "summary": f"Test {'completed successfully' if test_result.get('success') else 'failed'}. "
                      f"Success rate: {success_rate:.1f}%, "
                      f"Avg response time: {test_result.get('avg_response_time', 0):.2f}ms",
            "performance_grade": grade,
            "key_insights": [
                f"Success rate: {success_rate:.1f}%",
                f"Average response time: {test_result.get('avg_response_time', 0):.2f}ms",
                f"Throughput: {test_result.get('requests_per_sec', 0):.2f} req/s"
            ],
            "recommendations": self._generate_fallback_recommendations(test_result),
            "issues": self._identify_fallback_issues(test_result),
            "business_impact": "Standard performance assessment",
            "next_steps": ["Review detailed logs", "Analyze failure patterns", "Consider performance optimization"]
        }
    
    def _generate_fallback_recommendations(self, test_result: Dict[str, Any]) -> List[str]:
        """Generate fallback recommendations."""
        recommendations = []
        
        if test_result.get("failed_requests", 0) > 0:
            recommendations.append("Investigate failed requests to improve reliability")
        
        if test_result.get("avg_response_time", 0) > 1000:
            recommendations.append("Response times are high - consider optimization")
        
        if test_result.get("requests_per_sec", 0) < 1.0:
            recommendations.append("Throughput is low - check system capacity")
        
        if not test_result.get("success", False):
            recommendations.append("Test execution failed - check configuration and environment")
        
        return recommendations
    
    def _identify_fallback_issues(self, test_result: Dict[str, Any]) -> List[str]:
        """Identify potential issues from test results."""
        issues = []
        
        if test_result.get("failed_requests", 0) > 0:
            issues.append(f"{test_result['failed_requests']} requests failed")
        
        if test_result.get("avg_response_time", 0) > 2000:
            issues.append("Very high response times detected")
        
        if test_result.get("requests_per_sec", 0) < 0.5:
            issues.append("Very low throughput detected")
        
        if not test_result.get("success", False):
            issues.append("Test execution failed")
        
        return issues


class MockLLMAnalyzer(LLMAnalyzer):
    """
    Mock LLM analyzer for testing and development.
    """
    
    def _call_llm(self, prompt: str) -> str:
        """Mock LLM response for testing."""
        return '''
{
    "summary": "Test completed successfully with good performance metrics. The system handled the load well with minimal failures.",
    "performance_grade": "GOOD",
    "key_insights": [
        "99.2% success rate indicates reliable system performance",
        "Average response time of 245ms is within acceptable limits",
        "Throughput of 2.3 req/s shows adequate system capacity"
    ],
    "recommendations": [
        "Monitor response times during peak usage",
        "Consider implementing caching for frequently accessed endpoints",
        "Review error logs for the 0.8% failed requests"
    ],
    "issues": [
        "0.8% failure rate should be investigated",
        "Some response time spikes detected"
    ],
    "business_impact": "System performance is acceptable for current business needs",
    "next_steps": [
        "Implement monitoring alerts for response time thresholds",
        "Schedule performance optimization review",
        "Document test results for future reference"
    ]
}
''' 