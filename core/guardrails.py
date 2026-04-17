import re
from utils.logger import logger

FINANCIAL_KEYWORDS = [
    "charge", "payment", "amount", "balance", "total", "due",
    "transaction", "statement", "invoice", "receipt", "bill",
    "credit", "debit", "fee", "tax", "subscription", "purchase",
    "merchant", "vendor", "cost", "price", "refund", "pending",
    "date", "why", "what", "how much", "explain", "show", "list"
]

PII_PATTERNS = [
    (r'\b(\d{4})[\s\-](\d{4})[\s\-](\d{4})[\s\-](\d{4})\b',r'XXXX-XXXX-XXXX-\4'),
    (r'\b(\d{4})(\d{4})(\d{4})(\d{4})\b',r'XXXX-XXXX-XXXX-\4'),
    (r'\b\d{3}-\d{2}-\d{4}\b', r'XXX-XX-XXXX'),
    (r'\b(\d{4,8})(\d{4})\b',r'XXXX\2'),
]

def check_scope(user_question: str)->tuple[bool,str]:
    question_lower = user_question.lower().strip()
    # Example: "Why?" or "How?" as follow-ups
    if len(question_lower.split()) <= 3:
        return True, ""
    is_finance = any(
        keyword in question_lower for keyword in FINANCIAL_KEYWORDS
    )
    if not is_finance:
        logger.info(f"Out of scope question blocked: {user_question[:50]}")
        return False, (
            "I can only help with questions about your financial document. "
            "Please ask about charges, transactions, balances, or other "
            "details from your uploaded statement."
        )

    return True, ""

def sanitize_pii(text: str) -> str:
    if not text:
        return text
    sanitized = text
    pii_found = False
    for pattern , replacement in PII_PATTERNS:
        new_text = re.sub(pattern, replacement, sanitized)
        if new_text!= sanitized:
            pii_found = True
            sanitized = new_text
    if pii_found:
        logger.warning("PII detected and masked in agent output")

    return sanitized

def extract_amounts(text: str) -> list[float]:
    pattern = r'\$[\d,]+\.?\d*'
    matches = re.findall(pattern,text)
    amounts = []
    for match in matches:
        clean = match.replace("$","").replace(",","") .replace("/-","")
        try:
            amounts.append(float(clean))
        except ValueError:
            # Skip malformed matches
            continue
    return amounts

def verify_math(agent_answer: str, document_context: str)->dict:
    answer_amounts= set(extract_amounts(agent_answer))
    document_amounts = set(extract_amounts(document_context))

    if not answer_amounts:
        return {
            "is_verified": True,
            "flagged_amounts": [],
            "message": "No specific amounts to verify."
        }
    flagged = answer_amounts - document_amounts
    if flagged:
        flagged_formatted = [f"${amt:.2f}" for amt in sorted(flagged)]
        logger.warning(f"Math verification flagged amounts: {flagged_formatted}")
        return {
            "is_verified": False,
            "flagged_amounts": flagged_formatted,
            "message": (
                f"⚠️ Note: The following amounts could not be verified "
                f"against your document: {', '.join(flagged_formatted)}. "
                f"Please double-check these figures."
            )
        }
    logger.info("Math verification passed — all amounts found in document")
    return {
        "is_verified": True,
        "flagged_amounts": [],
        "message": "✅ All amounts verified against your document."
    }

def apply_guardrails(agent_answer: str,document_context: str,user_question: str) -> dict:
    """
    Master guardrails function. Runs all checks in sequence:
      1. PII sanitization  (always runs)
      2. Math verification (always runs)
    
    Note: scope check runs BEFORE the agent in app.py,
    not here — this function processes agent output only.
    
    Returns dict with:
      - final_answer   : sanitized answer ready to show user
      - math_verified  : True/False
      - warnings       : list of warning messages to show user
    """
    warnings = []
    sanitized_answer = sanitize_pii(agent_answer)
    math_result = verify_math(agent_answer,document_context)
    if not math_result["is_verified"]:
        warnings.append(math_result["message"])
    
    logger.info(
        f"Guardrails complete | "
        f"PII masked: {sanitized_answer != agent_answer} | "
        f"Math verified: {math_result['is_verified']}"
    )
    return {
        "final_answer": sanitized_answer,
        "math_verified": math_result["is_verified"],
        "warnings": warnings
    }



