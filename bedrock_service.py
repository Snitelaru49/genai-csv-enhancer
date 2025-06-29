import boto3
import json
import logging
from typing import Dict, List, Tuple
import pandas as pd
from config import AWS_REGION, BEDROCK_MODEL_ID

logger = logging.getLogger(__name__)

class BedrockService:
    def __init__(self, region_name: str = AWS_REGION):
        """Initialize Bedrock client"""
        try:
            self.bedrock_runtime = boto3.client(
                service_name='bedrock-runtime',
                region_name=region_name
            )
            self.model_id = BEDROCK_MODEL_ID
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.bedrock_runtime = None
    
    def generate_csv_rows(self, df: pd.DataFrame, num_rows: int = 5) -> Tuple[List[Dict], str]:
        """
        Generate new CSV rows based on existing data schema and sample
        
        Args:
            df: Pandas DataFrame with existing data
            num_rows: Number of new rows to generate
            
        Returns:
            Tuple of (generated_rows, explanation)
        """
        if not self.bedrock_runtime:
            return [], "Bedrock client not available"
        
        try:
            # Prepare prompt with schema and sample data
            prompt = self._create_prompt(df, num_rows)
            
            # Call Bedrock API
            response = self._call_bedrock_api(prompt)
            
            # Parse response
            generated_rows, explanation = self._parse_response(response, df.columns.tolist())
            
            return generated_rows, explanation
            
        except Exception as e:
            logger.error(f"Error generating rows: {e}")
            return [], f"Error generating rows: {str(e)}"
    
    def _create_prompt(self, df: pd.DataFrame, num_rows: int) -> str:
        """Create prompt for the LLM"""
        # Get basic statistics
        schema_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            unique_count = df[col].nunique()
            sample_values = df[col].dropna().head(5).tolist()
            
            schema_info.append(f"- {col} ({dtype}): {unique_count} unique values, examples: {sample_values}")
        
        schema_text = "\n".join(schema_info)
        
        # Get sample rows
        sample_rows = df.head(5).to_dict('records')
        
        prompt = f"""You are a data analyst helping to expand a dataset. Given the following CSV schema and sample data, generate {num_rows} new realistic rows that follow the same patterns and distributions.

DATASET SCHEMA:
{schema_text}

SAMPLE DATA (first 5 rows):
{json.dumps(sample_rows, indent=2, default=str)}

TASK: Generate exactly {num_rows} new rows that:
1. Follow the same data types and patterns
2. Have realistic values that fit the distribution
3. Maintain logical relationships between columns
4. Add diversity while staying consistent with the dataset

RESPONSE FORMAT:
Please respond with a JSON object containing:
1. "rows": Array of {num_rows} new row objects with the same column structure
2. "explanation": Brief explanation of your reasoning and what patterns you followed
3. "bias_flags": Array of any potential biases you noticed or filled

Example response format:
{{
    "rows": [
        {{"column1": "value1", "column2": "value2", ...}},
        ...
    ],
    "explanation": "I generated rows following the observed patterns...",
    "bias_flags": ["Added more diversity in age groups", "Balanced gender representation"]
}}

Generate the response now:"""

        return prompt
    
    def _call_bedrock_api(self, prompt: str) -> str:
        """Call Bedrock API with the prompt"""
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        }
        
        response = self.bedrock_runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']

    def _parse_response(self, response: str, columns: List[str]) -> Tuple[List[Dict], str]:
        """Parse the LLM response to extract rows and explanation"""
        try:
            parsed = self._try_parse_json(response, columns)
            if parsed is not None:
                return parsed

            parsed = self._try_parse_json_blocks(response, columns)
            if parsed is not None:
                return parsed

            parsed = self._try_parse_json_object(response, columns)
            if parsed is not None:
                return parsed

            return self._create_fallback_response(response, columns)
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return [], f"Error parsing AI response: {str(e)}"

    def _try_parse_json(self, response: str, columns: List[str]):
        """Try to parse the entire response as JSON"""
        try:
            parsed = json.loads(response.strip())
            return self._extract_data_from_json(parsed, columns)
        except json.JSONDecodeError:
            return None

    def _try_parse_json_blocks(self, response: str, columns: List[str]):
        """Try to parse JSON code blocks in the response"""
        json_blocks = self._extract_json_blocks(response)
        for json_block in json_blocks:
            try:
                parsed = json.loads(json_block)
                return self._extract_data_from_json(parsed, columns)
            except json.JSONDecodeError:
                continue
        return None

    def _try_parse_json_object(self, response: str, columns: List[str]):
        """Try to find and parse the first JSON object in the response"""
        json_obj = self._find_json_object(response)
        if json_obj:
            try:
                parsed = json.loads(json_obj)
                return self._extract_data_from_json(parsed, columns)
            except json.JSONDecodeError:
                return None
        return None
    
    def _extract_json_blocks(self, text: str) -> List[str]:
        """Extract JSON from code blocks"""
        import re
        patterns = [
            r'```json\s*\n(.*?)\n```',
            r'```\s*\n({.*?})\s*\n```',
            r'```({.*?})```'
        ]
        
        json_blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            json_blocks.extend(matches)
        
        return json_blocks
    
    def _find_json_object(self, text: str) -> str:
        """Find the first valid JSON object in text"""
        stack = []
        start_idx = None
        for i, char in enumerate(text):
            if char == '{':
                if start_idx is None:
                    start_idx = i
                stack.append('{')
            elif char == '}' and stack:
                stack.pop()
                if not stack and start_idx is not None:
                    candidate = text[start_idx:i + 1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except json.JSONDecodeError:
                        start_idx = None
                        stack = []
        return ""
    
    def _extract_data_from_json(self, parsed: dict, columns: List[str]) -> Tuple[List[Dict], str]:
        """Extract rows and explanation from parsed JSON"""
        rows = parsed.get('rows', [])
        explanation = parsed.get('explanation', 'AI generated new rows based on existing patterns')
        bias_flags = parsed.get('bias_flags', [])
        
        if bias_flags:
            explanation += f"\n\nBias considerations: {', '.join(bias_flags)}"
        
        # Clean and validate rows
        valid_rows = []
        for row in rows:
            if isinstance(row, dict):
                clean_row = {}
                for col in columns:
                    clean_row[col] = row.get(col, "Unknown")
                valid_rows.append(clean_row)
        
        return valid_rows, explanation
    
    def _create_fallback_response(self, response: str, columns: List[str]) -> Tuple[List[Dict], str]:
        """Create fallback response when parsing fails"""
        explanation = f"AI response parsing failed. Creating default row. Raw response: {response[:100]}..."
        
        # Create one default row
        fallback_row = {}
        for col in columns:
            col_lower = col.lower()
            if any(word in col_lower for word in ['name', 'title']):
                fallback_row[col] = "Sample Name"
            elif any(word in col_lower for word in ['age', 'count', 'number']):
                fallback_row[col] = 25
            elif any(word in col_lower for word in ['city', 'location']):
                fallback_row[col] = "Sample City"
            elif any(word in col_lower for word in ['salary', 'price', 'cost']):
                fallback_row[col] = 50000
            else:
                fallback_row[col] = "Sample Value"
        
        return [fallback_row], explanation

# Create a global instance
bedrock_service = BedrockService()
