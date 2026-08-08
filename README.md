# LinkedIn Post — Nyaya Sahayak

---

**🚀 I Built a Multi-Agent AI Platform for Indian Law Enforcement — Here's the Full Technical Breakdown**

For the past few weeks, I've been building something I'm genuinely proud of: **Nyaya Sahayak** — an Agentic AI co-pilot designed to help Indian police officers navigate the massive transition from the legacy IPC to the new Bharatiya Nyaya Sanhita (BNS).

But I didn't want to build another ChatGPT wrapper. When it comes to law, a hallucinated penal code is unacceptable. So I engineered a system where deterministic rules override the LLM whenever it gets creative with the law.

Here's the full technical architecture:

---

**📝 1. Autonomous FIR Drafting — Multi-Agent Pipeline**

Officers can speak or type an incident narrative. From there, a LangGraph State Graph orchestrates three autonomous agents:

🔹 **Investigator Agent** — Parses raw, unstructured narratives using Named Entity Recognition and zero-shot prompting to extract 10 structured legal fields (weapons, injuries, suspects, motives, stolen items).

🔹 **Magistrate Agent** — Runs Multi-Query Semantic Retrieval: 4+ distinct query vectors are generated per incident and fired against a ChromaDB vector database containing all 358 BNS sections, encoded into 384-dimensional dense vectors using a local BERT model (SentenceTransformers: all-MiniLM-L6-v2).

🔹 **Clerk Agent** — Takes the validated sections and autonomously drafts a court-ready FIR under Section 173 BNSS.

But here's what makes it different: between the Magistrate and the Clerk sits a **Crime Pattern Engine** — a fully deterministic, rule-based legal expert system I wrote from scratch. It scans the narrative for 19 crime topologies, injects mandatory companion sections (with exact subsection precision — e.g., Section 308(4), not generic 308), and appends Special Acts (Arms Act, IT Act, POCSO, NDPS). A **Universal Validator** then acts as the final guardrail — if the LLM tries to hallucinate a section outside our verified candidate pool, or drops a mandatory section, the Validator ruthlessly overrides it.

The result: **zero hallucinations in legal section mapping.**

---

**🤖 2. AI Legal Chatbot — RAG Conversational Agent**

I built a slide-out chat assistant where officers can ask any legal question in natural language — "What is the punishment for kidnapping under BNS?", "Can I arrest without warrant for robbery?"

**How it works under the hood:**
🔹 **Hybrid RAG:** The system first regex-scans the query for section numbers (e.g., "Section 304") and fetches exact metadata matches from ChromaDB. Then it augments those results with dense semantic vector search for broader context.
🔹 **Conversational Memory:** Session history is maintained, allowing contextual follow-ups ("What about Section 127?").
🔹 **Grounding & Citation:** Strict prompt engineering forces the model to cite exact BNS section numbers in every answer. No citation = no answer.

---

**🕵️ 3. AI Witness Analyzer — Multi-Modal Intelligence**

This is my favorite feature. It combines Speech Recognition, Digital Signal Processing, and Agentic AI reasoning into a single pipeline:

🔹 **Local Speech-to-Text:** Witness audio is transcribed locally using OpenAI Whisper. I also built an automatic Urdu-to-Devanagari script correction pipeline for Hindi witnesses (Whisper sometimes outputs Hindi in Perso-Arabic script).

🔹 **Voice Stress Analysis:** Using librosa, the system analyzes fundamental frequency (pitch mean & std dev via pYIN), RMS energy for silence/pause detection, and speech rate (words-per-second). It computes a composite stress score, classifies stress level (LOW/MEDIUM/HIGH), and outputs a coercion probability percentage.

🔹 **Contradiction Detection:** When multiple statements from the same witness are recorded over time, the system performs field-by-field comparison and flags inconsistencies — automatically detecting changing stories.

🔹 **AI Interrogation Assistant (Chain-of-Thought Reasoning):** The agent analyzes the statement, identifies investigative gaps, and generates 6–8 strategic follow-up questions categorized by priority (CRITICAL / IMPORTANT / SUPPLEMENTARY) and type (Identification, Timeline, Evidence, Visibility, Escape Route, Corroboration). It even factors in the stress analysis results to probe areas of potential coercion.

---

**⚖️ 4. Charge-Sheet & Case Diary Generator**

After the investigation, the system generates a prosecution-ready Charge-Sheet (Sec 193 BNSS), a Chronological Case Diary, and an Evidence Strength Matrix — all from the accumulated FIR data, witness statements, and forensic reports.

---

**🛡️ Under the Hood — Engineering Resilience**

🔹 **3-Tier LLM Fallback Chain:** Groq Llama 3.3 70B → Groq Llama 3.1 8B → Google Gemini 2.0 Flash → Deterministic local fallback. If every API is down, the Crime Pattern Engine + Validator still produces accurate output.

🔹 **Hybrid Symbolic-Connectionist Architecture:** Rule engines (deterministic) + Vector embeddings (connectionist) + LLMs (generative) working together. The best of all three AI paradigms.

---

**Core Gen AI & Agentic AI Concepts Used:**

⚙️ Multi-Agent State Graph Orchestration (LangGraph)
⚙️ Hybrid RAG (Semantic Vector Search + Exact Regex Retrieval + Rule Engine)
⚙️ Dense Vector Embeddings (BERT / SentenceTransformers, 384-dim, ChromaDB)
⚙️ Multi-Modal AI (Audio Transcription + NLP + Signal Processing)
⚙️ Chain-of-Thought (CoT) Prompting & Zero-Shot Reasoning
⚙️ Conversational Memory & Grounded Citation
⚙️ Deterministic AI Guardrails & Universal Validator
⚙️ Voice Stress Analysis (Pitch, RMS Energy, Speech Rate — librosa)
⚙️ Multi-Provider Fallback & Resilience Engineering

---

Building this taught me that the future of Legal Tech isn't about throwing an LLM at a prompt. It's about building autonomous, goal-directed agents constrained by deterministic guardrails — systems that are accurate enough to be trusted by the people who enforce the law.

Would love to connect with anyone building at the intersection of Agentic AI, Machine Learning, and Legal Tech.

**#AgenticAI #GenerativeAI #LegalTech #MachineLearning #BNS #Python #LangGraph #FastAPI #ChromaDB #BuildInPublic**
