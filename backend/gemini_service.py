from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from backend.config import settings

class Citation(BaseModel):
    doc_name: str = Field(description="The filename of the source document")
    page_or_section: str = Field(description="The page number (e.g. Page 3) or section heading (e.g. Q3 Sales)")
    excerpt: str = Field(description="The exact text snippet from the document supporting the answer")

class ChartDataPoint(BaseModel):
    label: str = Field(description="The label for the data point (e.g., '2025', 'Product A', 'January')")
    value: float = Field(description="The numeric value for this label")

class ChartConfig(BaseModel):
    type: str = Field(description="The type of chart to render: 'bar', 'line', or 'pie'")
    title: str = Field(description="Descriptive title of the chart")
    data: List[ChartDataPoint] = Field(description="List of data points to plot")

class GeminiResponse(BaseModel):
    answer: str = Field(description="The markdown formatted detailed response synthesizing the context. Provide a rich and thorough answer.")
    citations: List[Citation] = Field(description="List of precise citations from the provided context")
    chart: Optional[ChartConfig] = Field(default=None, description="Populate this if the user asks for a chart/graph, or if the question involves quantitative/numeric data comparisons (like trends, rankings, budgets) that can be visualized as a bar chart, line chart, or pie chart.")

def generate_answer_from_context(query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate an answer from the retrieved document chunks.
    Extracts citations and optional chart configurations in a structured JSON response.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        # Fallback if no API key is provided
        return {
            "answer": "### Gemini API Key Missing\n\nPlease go to the **Settings** tab in the sidebar and enter your Gemini API key. Once set, the AI will synthesize responses and build interactive charts from your uploaded documents.\n\nIn the meantime, here are the most relevant document passages found for your query:",
            "citations": [
                {
                    "doc_name": chunk["filename"],
                    "page_or_section": chunk.get("page_number") or chunk.get("section_heading") or "N/A",
                    "excerpt": chunk["text"][:200] + "..."
                } for chunk in retrieved_chunks
            ],
            "chart": None
        }

    if not retrieved_chunks:
        # No context available
        return {
            "answer": "I couldn't find any relevant documents in the repository. Please upload documents in the **Documents** tab first, then ask questions about them.",
            "citations": [],
            "chart": None
        }

    # Construct the context prompt
    context_str = ""
    for idx, chunk in enumerate(retrieved_chunks):
        context_str += f"--- DOCUMENT CHUNK {idx + 1} ---\n"
        context_str += f"Source Document: {chunk['filename']}\n"
        context_str += f"Location: {chunk.get('page_number') or 'N/A'}\n"
        context_str += f"Section: {chunk.get('section_heading') or 'N/A'}\n"
        context_str += f"Content:\n{chunk['text']}\n\n"

    system_instruction = (
        "You are KnowledgeBot, an expert AI assistant that helps users understand and analyze organizational documents.\n"
        "You are provided with a set of document pages. Answer the user's query using the provided context.\n"
        "If the answer cannot be found or fully inferred from the context, state clearly what you do know, but NEVER mention 'retrieved context', 'retrieved information', or your internal search mechanisms. Speak naturally as if you are reading the document directly (e.g., say 'The document mentions X, but does not provide the specific steps' instead of 'The retrieved context does not provide...').\n"
        "EXCEPTION: If the user asks a general conversational question or greeting (e.g., 'hi', 'hello', 'help', 'who are you'), respond naturally as a friendly AI assistant offering to help them search their documents. Do not complain about lacking context for greetings.\n\n"
        "CRITICAL RULES:\n"
        "1. Prioritize accuracy and strictly ground your answer in the provided document chunks. If a document uses a placeholder like '[Member 1 Name]', try to cross-reference with other retrieved documents to find the actual name (e.g., the author of related documents).\n"
        "2. DO NOT GIVE SOURCE CITATIONS IN THE MIDDLE OF THE ANSWER! Write your answer naturally and beautifully using markdown (like bolding and bullet points). Then, provide all your citations at the VERY END of your entire answer in a dedicated 'Sources:' section.\n"
        "   Example format:\n"
        "   The author of the BRD is John Doe.\n\n"
        "   **Sources:**\n"
        "   - Project_Doc.pdf, Page 4\n"
        "   Also, ensure you populate the `citations` list in the JSON response.\n"
        "3. Look for numeric data. If the user asks for a chart/graph (e.g., 'plot', 'graph', 'chart'), or if the context contains numbers, percentages, budgets, or trends that would be much easier to understand visually, populate the `chart` object.\n"
        "   - Choose 'bar' for categories/rankings.\n"
        "   - Choose 'line' for time-series or trends.\n"
        "   - Choose 'pie' for proportions/shares.\n"
        "   - Ensure all data points have a text label and numeric value."
    )

    prompt = f"User Query: {query}\n\nRetrieved Context:\n{context_str}"

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=GeminiResponse,
                temperature=0.2
            )
        )
        
        # The response text is a structured JSON string matching GeminiResponse
        import json
        result = json.loads(response.text)
        return result

    except Exception as e:
        print(f"Error calling Gemini: {e}")
        # Fallback response in case of API error
        return {
            "answer": f"An error occurred while generating the response: {str(e)}\n\nHere are the raw passages found in your document store:",
            "citations": [
                {
                    "doc_name": chunk["filename"],
                    "page_or_section": chunk.get("page_number") or chunk.get("section_heading") or "N/A",
                    "excerpt": chunk["text"][:150] + "..."
                } for chunk in retrieved_chunks
            ],
            "chart": None
        }
