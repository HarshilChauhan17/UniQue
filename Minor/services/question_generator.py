"""
Question Generator Service
Faculty tools for creating assignments, MCQs, and viva questions
"""

from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import List, Dict
import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionGenerator:
    def __init__(self):
        self.llm_model = "mistralai/Mistral-7B-Instruct-v0.2"
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize HuggingFace LLM"""
        api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not api_token:
            raise ValueError("HUGGINGFACEHUB_API_TOKEN not found")
        
        return HuggingFaceEndpoint(
            repo_id=self.llm_model,
            temperature=0.5,
            max_new_tokens=2048,
            huggingfacehub_api_token=api_token
        )
    
    async def generate_assignment(
        self, 
        context: str, 
        num_questions: int = 5, 
        difficulty: str = "medium"
    ) -> List[Dict]:
        """
        Generate structured assignment questions
        
        Returns:
            List of questions with marks, type, and solution
        """
        try:
            prompt_template = """You are an expert educator creating an assignment. Using the provided content, generate {num_questions} assignment questions.

Difficulty Level: {difficulty}

Guidelines:
- Create a mix of question types: theory, numerical, analytical, application-based
- Assign appropriate marks: 2-mark, 5-mark, 10-mark questions
- Include marking scheme for each question
- Ensure questions test different aspects and depth levels

Content:
{context}

Generate {num_questions} well-structured assignment questions in this JSON format:
[
  {{
    "question_number": 1,
    "question": "Question text here",
    "type": "theory/numerical/analytical/application",
    "marks": 5,
    "marking_scheme": "Point 1 (2 marks), Point 2 (2 marks), Point 3 (1 mark)",
    "sample_answer": "Brief outline of expected answer"
  }}
]

Generate the assignment now:"""

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["num_questions", "difficulty", "context"]
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(
                num_questions=num_questions,
                difficulty=difficulty,
                context=context[:3000]  # Limit context size
            )
            
            # Parse JSON response
            questions = self._parse_json_response(result)
            
            # If parsing fails, return structured fallback
            if not questions:
                questions = self._generate_fallback_assignment(context, num_questions)
            
            logger.info(f"Generated {len(questions)} assignment questions")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating assignment: {str(e)}")
            raise
    
    async def generate_mcqs(
        self, 
        context: str, 
        num_questions: int = 10, 
        difficulty: str = "medium"
    ) -> List[Dict]:
        """
        Generate multiple choice questions with 4 options
        """
        try:
            prompt_template = """Create {num_questions} multiple choice questions from the given content.

Difficulty: {difficulty}

Requirements:
- 4 options (A, B, C, D) for each question
- Only ONE correct answer
- Distractors should be plausible but clearly incorrect
- Cover different topics from the content
- Mix factual recall, conceptual, and application-based questions

Content:
{context}

Generate MCQs in this JSON format:
[
  {{
    "question_number": 1,
    "question": "What is...?",
    "options": {{
      "A": "Option A text",
      "B": "Option B text",
      "C": "Option C text",
      "D": "Option D text"
    }},
    "correct_answer": "B",
    "explanation": "Brief explanation of why B is correct"
  }}
]

Generate the MCQs now:"""

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["num_questions", "difficulty", "context"]
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(
                num_questions=num_questions,
                difficulty=difficulty,
                context=context[:3000]
            )
            
            questions = self._parse_json_response(result)
            
            if not questions:
                questions = self._generate_fallback_mcqs(context, num_questions)
            
            logger.info(f"Generated {len(questions)} MCQs")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating MCQs: {str(e)}")
            raise
    
    async def generate_viva_questions(
        self, 
        context: str, 
        num_questions: int = 10
    ) -> List[Dict]:
        """
        Generate viva/oral examination questions
        Focused on conceptual understanding and quick thinking
        """
        try:
            prompt_template = """Generate {num_questions} viva (oral examination) questions from the content.

Viva questions should:
- Test conceptual understanding
- Be brief and direct
- Allow for elaborate verbal answers
- Cover fundamental and advanced concepts
- Include some "why" and "how" questions

Content:
{context}

Generate questions in this JSON format:
[
  {{
    "question_number": 1,
    "question": "Explain the significance of...",
    "type": "conceptual/definition/comparison/application",
    "key_points": ["Point 1 expected in answer", "Point 2", "Point 3"],
    "difficulty": "easy/medium/hard"
  }}
]

Generate the viva questions now:"""

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["num_questions", "context"]
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(
                num_questions=num_questions,
                context=context[:3000]
            )
            
            questions = self._parse_json_response(result)
            
            if not questions:
                questions = self._generate_fallback_viva(context, num_questions)
            
            logger.info(f"Generated {len(questions)} viva questions")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating viva questions: {str(e)}")
            raise
    
    def _parse_json_response(self, response: str) -> List[Dict]:
        """
        Parse JSON from LLM response
        Handles various formats and cleans up response
        """
        try:
            # Try to find JSON array in response
            start = response.find('[')
            end = response.rfind(']') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                questions = json.loads(json_str)
                return questions
            
            return []
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {str(e)}")
            return []
    
    def _generate_fallback_assignment(self, context: str, num_questions: int) -> List[Dict]:
        """Fallback assignment structure if JSON parsing fails"""
        return [
            {
                "question_number": i + 1,
                "question": f"Question {i+1}: Based on the provided content, explain [topic] with relevant examples.",
                "type": "theory" if i % 2 == 0 else "analytical",
                "marks": 5 if i < num_questions // 2 else 10,
                "marking_scheme": "Refer to content for detailed marking",
                "sample_answer": "Answer should cover key concepts from the provided material"
            }
            for i in range(num_questions)
        ]
    
    def _generate_fallback_mcqs(self, context: str, num_questions: int) -> List[Dict]:
        """Fallback MCQ structure"""
        return [
            {
                "question_number": i + 1,
                "question": f"Question {i+1} from content",
                "options": {
                    "A": "Option A",
                    "B": "Option B",
                    "C": "Option C",
                    "D": "Option D"
                },
                "correct_answer": "A",
                "explanation": "Refer to content for explanation"
            }
            for i in range(num_questions)
        ]
    
    def _generate_fallback_viva(self, context: str, num_questions: int) -> List[Dict]:
        """Fallback viva questions structure"""
        return [
            {
                "question_number": i + 1,
                "question": f"Explain the concept discussed in the provided content.",
                "type": "conceptual",
                "key_points": ["Key point 1", "Key point 2", "Key point 3"],
                "difficulty": "medium"
            }
            for i in range(num_questions)
        ]