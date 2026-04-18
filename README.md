# 💳 AI Financial Assistant

A production-grade multimodal AI assistant that analyzes financial
documents (credit card statements, invoices, receipts) and answers
questions about charges and transactions using RAG + Vision + Guardrails.

---

## What it does

- Upload a **PDF or image** of any financial document
- Ask natural language questions: _"Why was this charge deducted?"_
- Get grounded, cited answers streamed token by token
- Unknown merchants are searched via DuckDuckGo automatically
- All answers verified against the document — hallucinated numbers flagged
- PII (card numbers, SSNs) automatically masked in responses

---

## Architecture

```
PDF/Image Upload
      ↓
[Extractor]  pdfplumber (PDF) or Groq Vision LLM (Image)
      ↓
[Agent]      LangChain AgentExecutor + Groq Llama 3.3 70B
      ↓
[Tools]      DuckDuckGo search for unknown merchants
      ↓
[Guardrails] Math verification + PII sanitization + Scope check
      ↓
[UI]         Streamlit with streaming token output
```

---

## Tech Stack

| Component       | Technology           | Why                      |
| --------------- | -------------------- | ------------------------ |
| LLM             | Groq + Llama 3.3 70B | Free, fast inference     |
| Vision          | Groq Llama 4 Scout   | Multimodal image parsing |
| Agent Framework | LangChain LCEL       | Tool calling + memory    |
| PDF Extraction  | pdfplumber           | Table-aware extraction   |
| Search Tool     | DuckDuckGo           | No API key required      |
| Frontend        | Streamlit            | Rapid Python-native UI   |
| Monitoring      | LangSmith            | Agent trace visibility   |
| Deployment      | Docker + AWS EC2     | Production container     |

---

## Project Structure

```
financial_assistant/
├── app.py                  ← Streamlit UI
├── core/
│   ├── extractor.py        ← PDF + image extraction
│   ├── agent.py            ← LLM reasoning + streaming
│   ├── tools.py            ← DuckDuckGo search tool
│   ├── vision.py           ← Groq vision model
│   └── guardrails.py       ← Math check + PII + scope
├── utils/
│   ├── helpers.py          ← File validation + utilities
│   └── logger.py           ← Structured logging
├── Dockerfile
└── requirements.txt
```

---

## Run Locally

```bash
# Clone repo
git clone https://github.com/yourusername/financial_assistant
cd financial_assistant

# Install dependencies
pip install -r requirements.txt

# Add environment variables
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# Run
streamlit run app.py
```

---

## Run with Docker

```bash
docker build -t financial-assistant .

docker run -d \
  -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  financial-assistant
```

---

## Key Design Decisions

**Why pdfplumber over PyPDF2?**
pdfplumber preserves table structure. PyPDF2 returns tables
as a single unstructured string — LLM loses column context.

**Why EC2 over Lambda?**
Cold start + model initialization time makes Lambda impractical
for interactive chat. EC2 keeps the agent warm between requests.

**Why DuckDuckGo over Tavily?**
No API key needed — removes a dependency for portfolio demos.
Tavily would be the production upgrade path.

**Why word-level streaming over character-level?**
Character streaming looks jittery in Streamlit. Word-level
streaming is smoother while still feeling real-time.

---

## What I'd improve in production

- Add ChromaDB vector store for multi-document retrieval
- Replace DuckDuckGo with Tavily for reliable production search
- Add user authentication (currently single-user)
- Add Ragas evaluation pipeline for answer quality scoring
- Move secrets to AWS Secrets Manager

---

## Live Demo

http://YOUR_EC2_IP:8501
