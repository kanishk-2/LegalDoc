import os
import json
import logging
from typing import Dict, List, Optional
from google import genai
from google.genai import types

class GeminiAnalyzer:
    """Handles legal document analysis using Google Gemini AI."""
    
    def __init__(self):
        """Initialize the Gemini client."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not found")
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"
    
    def analyze_document(self, text: str, analysis_type: str, complexity_level: str) -> Dict:
        """Perform comprehensive legal document analysis."""
        try:
            # Create analysis prompt based on type and complexity
            prompt = self._create_analysis_prompt(text, analysis_type, complexity_level)
            
            # Generate analysis
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if not response.text:
                raise Exception("Empty response from Gemini API")
            
            # Parse the response and structure the results
            analysis_result = self._parse_analysis_response(response.text, text)
            
            return analysis_result
            
        except Exception as e:
            logging.error(f"Error in document analysis: {e}")
            return {
                "error": str(e),
                "summary": "Analysis failed due to an error.",
                "key_points": [],
                "insights": {},
                "recommendations": []
            }
    
    def _create_analysis_prompt(self, text: str, analysis_type: str, complexity_level: str) -> str:
        """Create a detailed prompt for legal document analysis."""
        
        base_prompt = f"""
        You are an expert legal analyst. Please analyze the following legal document text thoroughly.
        
        Analysis Type: {analysis_type}
        Detail Level: {complexity_level}
        
        Document Text:
        {text[:8000]}  # Limit text to avoid token limits
        
        Please provide a comprehensive analysis including:
        
        1. DOCUMENT SUMMARY: A clear, concise summary of the document's purpose and main content
        
        2. KEY POINTS: Extract and list the most important points, clauses, or provisions
        
        3. LEGAL INSIGHTS: Provide insights about:
           - Document complexity (score 1-10)
           - Legal areas involved
           - Potential risks or concerns
           - Document tone/sentiment
           - Important dates or deadlines mentioned
        
        4. SIMPLIFIED EXPLANATION: Explain the document in plain English for non-lawyers
        
        5. RECOMMENDATIONS: Suggest actions or considerations for the reader
        
        Please format your response clearly with headers and bullet points where appropriate.
        Make sure your analysis is practical and actionable.
        """
        
        if analysis_type == "Risk Assessment":
            base_prompt += """
            
            SPECIAL FOCUS: Pay particular attention to:
            - Potential legal risks
            - Liability issues
            - Compliance requirements
            - Financial obligations
            - Termination clauses
            """
        
        elif analysis_type == "Key Points Extraction":
            base_prompt += """
            
            SPECIAL FOCUS: Emphasize:
            - Critical clauses and provisions
            - Rights and obligations
            - Important definitions
            - Performance requirements
            """
        
        return base_prompt
    
    def _parse_analysis_response(self, response_text: str, original_text: str) -> Dict:
        """Parse and structure the Gemini response into organized data."""
        
        # Initialize result structure
        result = {
            "summary": "",
            "key_points": [],
            "insights": {},
            "simplified_explanation": "",
            "recommendations": [],
            "raw_analysis": response_text
        }
        
        # Extract different sections from the response
        lines = response_text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            # Identify section headers
            if any(header in line.upper() for header in ['SUMMARY', 'DOCUMENT SUMMARY']):
                if current_section and current_content:
                    self._process_section(result, current_section, current_content)
                current_section = "summary"
                current_content = []
            elif any(header in line.upper() for header in ['KEY POINTS', 'MAIN POINTS']):
                if current_section and current_content:
                    self._process_section(result, current_section, current_content)
                current_section = "key_points"
                current_content = []
            elif any(header in line.upper() for header in ['INSIGHTS', 'LEGAL INSIGHTS']):
                if current_section and current_content:
                    self._process_section(result, current_section, current_content)
                current_section = "insights"
                current_content = []
            elif any(header in line.upper() for header in ['SIMPLIFIED', 'PLAIN ENGLISH']):
                if current_section and current_content:
                    self._process_section(result, current_section, current_content)
                current_section = "simplified"
                current_content = []
            elif any(header in line.upper() for header in ['RECOMMENDATIONS', 'SUGGESTIONS']):
                if current_section and current_content:
                    self._process_section(result, current_section, current_content)
                current_section = "recommendations"
                current_content = []
            elif line and not line.startswith('#'):
                current_content.append(line)
        
        # Process the last section
        if current_section and current_content:
            self._process_section(result, current_section, current_content)
        
        # Add basic insights if not extracted
        if not result["insights"]:
            result["insights"] = self._generate_basic_insights(original_text)
        
        return result
    
    def _process_section(self, result: Dict, section: str, content: List[str]) -> None:
        """Process a specific section of the analysis."""
        content_text = '\n'.join(content).strip()
        
        if section == "summary":
            result["summary"] = content_text
        
        elif section == "key_points":
            # Extract bullet points
            points = []
            for line in content:
                if line.startswith(('-', '•', '*')) or line[0].isdigit():
                    points.append(line.lstrip('-•* 0123456789.'))
                elif line.strip():
                    points.append(line)
            result["key_points"] = [p.strip() for p in points if p.strip()]
        
        elif section == "insights":
            # Parse insights for structured data
            insights = {}
            for line in content:
                if 'complexity' in line.lower() and any(char.isdigit() for char in line):
                    # Extract complexity score
                    for char in line:
                        if char.isdigit():
                            insights["complexity_score"] = int(char)
                            break
                
                if 'legal area' in line.lower() or 'area' in line.lower():
                    areas = [area.strip() for area in line.split(',') if area.strip()]
                    insights["legal_areas"] = areas
                
                if 'sentiment' in line.lower() or 'tone' in line.lower():
                    insights["sentiment"] = line.split(':')[-1].strip() if ':' in line else "Neutral"
            
            result["insights"] = insights
        
        elif section == "simplified":
            result["simplified_explanation"] = content_text
        
        elif section == "recommendations":
            # Extract recommendations as list
            recommendations = []
            for line in content:
                if line.startswith(('-', '•', '*')) or line[0].isdigit():
                    recommendations.append(line.lstrip('-•* 0123456789.'))
                elif line.strip():
                    recommendations.append(line)
            result["recommendations"] = [r.strip() for r in recommendations if r.strip()]
    
    def _generate_basic_insights(self, text: str) -> Dict:
        """Generate basic insights about the document."""
        word_count = len(text.split())
        char_count = len(text)
        
        # Simple complexity estimation
        complexity_score = min(10, max(1, word_count // 500 + len([c for c in text if c.isupper()]) // 100))
        
        return {
            "word_count": word_count,
            "character_count": char_count,
            "complexity_score": complexity_score,
            "complexity_level": "Low" if complexity_score <= 3 else "Medium" if complexity_score <= 7 else "High",
            "estimated_reading_time": f"{word_count // 200 + 1} minutes"
        }
    
    def get_document_summary(self, text: str) -> str:
        """Get a quick summary of the document."""
        try:
            prompt = f"""
            Please provide a concise summary of this legal document in 2-3 sentences:
            
            {text[:4000]}
            
            Focus on the document's main purpose and key provisions.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            return response.text or "Summary not available"
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def extract_key_entities(self, text: str) -> List[str]:
        """Extract key legal entities and terms from the document."""
        try:
            prompt = f"""
            Extract the key legal entities, important dates, and critical terms from this legal document.
            Return them as a simple list:
            
            {text[:4000]}
            
            Focus on: parties involved, important dates, key legal terms, amounts, deadlines.
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            if response.text:
                # Parse the response into a list
                entities = [line.strip().lstrip('-•* ') for line in response.text.split('\n') if line.strip()]
                return entities[:20]  # Limit to 20 entities
            
            return []
            
        except Exception as e:
            logging.error(f"Error extracting entities: {e}")
            return []
