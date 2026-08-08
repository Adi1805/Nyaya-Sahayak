
import os
import json
import ssl
import httpx
from dotenv import load_dotenv
load_dotenv()
ssl._create_default_https_context = ssl._create_unverified_context
_original_httpx_client_init = httpx.Client.__init__
def _patched_httpx_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    _original_httpx_client_init(self, *args, **kwargs)
httpx.Client.__init__ = _patched_httpx_client_init
_original_httpx_async_init = httpx.AsyncClient.__init__
def _patched_httpx_async_init(self, *args, **kwargs):
    kwargs['verify'] = False
    _original_httpx_async_init(self, *args, **kwargs)
httpx.AsyncClient.__init__ = _patched_httpx_async_init
def _clean_json_response(content: str) -> str:
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()
def _extract_text(response) -> str:
    content = response.content
    if isinstance(content, list):
        content = " ".join([
            c.get("text", "") if isinstance(c, dict) else str(c) 
            for c in content
        ])
    elif not isinstance(content, str):
        content = str(content)
    return content
def _try_gemini(prompt_text: str, temperature: float = 0.2):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("[AI Provider] No GOOGLE_API_KEY set, skipping Gemini.")
        return None
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=temperature,
            google_api_key=api_key,
            max_retries=1,
            timeout=10
        )
        response = llm.invoke(prompt_text)
        text = _extract_text(response)
        print("[AI Provider] Gemini 2.0 Flash responded successfully.")
        return text
    except Exception as e:
        error_msg = str(e)
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            print(f"[AI Provider] Gemini rate-limited. Trying Groq fallback...")
        else:
            print(f"[AI Provider] Gemini error: {error_msg[:100]}. Trying Groq fallback...")
        return None
def _try_groq(prompt_text: str, temperature: float = 0.2):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("[AI Provider] No GROQ_API_KEY set, skipping Groq.")
        return None
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            groq_api_key=api_key,
            max_retries=1,
            timeout=15
        )
        response = llm.invoke(prompt_text)
        text = _extract_text(response)
        print("[AI Provider] Groq (Llama 3.3 70B) responded successfully.")
        return text
    except Exception as e:
        error_msg = str(e)
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            print(f"[AI Provider] Groq 70B rate-limited. Trying fallback...")
        else:
            print(f"[AI Provider] Groq 70B error: {error_msg[:200]}")
        return None
def _try_groq_8b(prompt_text: str, temperature: float = 0.2):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        from langchain_groq import ChatGroq
        adjusted_temp = max(temperature, 0.4) 
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=adjusted_temp,
            groq_api_key=api_key,
            max_retries=1,
            timeout=15
        )
        response = llm.invoke(prompt_text)
        text = _extract_text(response)
        print("[AI Provider] Groq (Llama 3.1 8B) responded successfully.")
        return text
    except Exception as e:
        error_msg = str(e)
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            print(f"[AI Provider] Groq 8B also rate-limited. Using fallback data.")
        else:
            print(f"[AI Provider] Groq 8B error: {error_msg[:200]}. Using fallback data.")
        return None
def call_llm(prompt_text: str, is_json: bool = False, temperature: float = 0.2):
    for provider_fn in [_try_groq, _try_groq_8b, _try_gemini]:
        result = provider_fn(prompt_text, temperature)
        if result is not None:
            if is_json:
                try:
                    cleaned = _clean_json_response(result)
                    return json.loads(cleaned)
                except json.JSONDecodeError as e:
                    print(f"[AI Provider] JSON parse error from provider: {e}. Trying next...")
                    continue
            return result
    print("[AI Provider] All providers exhausted. Returning None for fallback handling.")
    return None
def call_llm_with_prompt(prompt_template, variables: dict, is_json: bool = False, temperature: float = 0.2):
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            from langchain_groq import ChatGroq
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=temperature,
                groq_api_key=groq_key,
                max_retries=1,
                timeout=15
            )
            chain = prompt_template | llm
            response = chain.invoke(variables)
            text = _extract_text(response)
            print("[AI Provider] Groq (Llama 3.3 70B) responded instantly & successfully.")
            if is_json:
                return json.loads(_clean_json_response(text))
            return text
        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                print(f"[AI Provider] Groq 70B rate-limited. Falling back to Groq 8B...")
            else:
                print(f"[AI Provider] Groq 70B error: {error_msg[:100]}. Falling back to Groq 8B...")
        try:
            from langchain_groq import ChatGroq
            adjusted_temp = max(temperature, 0.4)
            llm_8b = ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=adjusted_temp,
                groq_api_key=groq_key,
                max_retries=1,
                timeout=15
            )
            chain = prompt_template | llm_8b
            response = chain.invoke(variables)
            text = _extract_text(response)
            print("[AI Provider] Groq (Llama 3.1 8B) responded instantly & successfully.")
            if is_json:
                return json.loads(_clean_json_response(text))
            return text
        except Exception as e:
            error_msg = str(e)
            print(f"[AI Provider] Groq 8B error/rate-limit: {error_msg[:100]}. Trying Gemini fallback...")
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=temperature,
                google_api_key=api_key,
                max_retries=1,
                timeout=10
            )
            chain = prompt_template | llm
            response = chain.invoke(variables)
            text = _extract_text(response)
            print("[AI Provider] Gemini 2.0 Flash responded successfully.")
            if is_json:
                return json.loads(_clean_json_response(text))
            return text
        except Exception as e:
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                print(f"[AI Provider] Gemini rate-limited.")
            else:
                print(f"[AI Provider] Gemini error: {error_msg[:100]}.")
    print("[AI Provider] All providers exhausted. Returning None for fallback handling.")
    return None
