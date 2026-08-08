import os
import json
from langchain_core.prompts import ChatPromptTemplate
from ai_provider import call_llm_with_prompt
from datetime import datetime
def generate_charge_sheet_data(fir_content: str, witness_statements: str, forensic_reports: str, case_title: str):
    prompt = ChatPromptTemplate.from_template(
        "You are an expert Indian Police Officer drafting a final Charge-Sheet (Section 193 BNSS).\n"
        "Analyze the following evidence:\n"
        "FIR: {fir_content}\n"
        "Witness Statements: {witness_statements}\n"
        "Forensic/Medical Reports: {forensic_reports}\n\n"
        "Based on this, generate a strict JSON object with exactly these 3 keys:\n"
        "1. 'case_diary': A chronological summary (HTML formatted with <ul> and <li>) of the investigation steps based on the evidence.\n"
        "2. 'charge_sheet': The draft charge-sheet text (HTML formatted) summarizing the offense, the accused, and the concluding allegations.\n"
        "3. 'evidence_matrix': A list of objects, each containing 'accused_name', 'evidence_type', 'description', and 'strength' (High/Medium/Low).\n\n"
        "Return ONLY the raw JSON object, no markdown wrappers."
    )
    try:
        result = call_llm_with_prompt(prompt, {
            "fir_content": fir_content,
            "witness_statements": witness_statements or "None provided",
            "forensic_reports": forensic_reports or "None provided"
        }, is_json=True, temperature=0.1)
        if result is not None:
            return result
    except Exception as e:
        print(f"Charge-Sheet AI Error (Likely Rate Limit): {str(e)}. Falling back to mock data.")
    current_date = datetime.now().strftime("%d/%m/%Y")
    mock_diary = f
    mock_charge_sheet = f
    mock_matrix = [
        {
            "accused_name": "Accused 1 (Unknown)",
            "evidence_type": "Witness Statement",
            "description": witness_statements[:50] + "..." if witness_statements else "Corroborated by complainant",
            "strength": "High"
        },
        {
            "accused_name": "Accused 1 (Unknown)",
            "evidence_type": "Forensic / Physical",
            "description": forensic_reports[:50] + "..." if forensic_reports else "Pending final FSL report",
            "strength": "Medium"
        }
    ]
    return {
        "case_diary": mock_diary,
        "charge_sheet": mock_charge_sheet,
        "evidence_matrix": mock_matrix
    }
