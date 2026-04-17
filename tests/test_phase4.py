import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from core.guardrails import (
    check_scope,
    sanitize_pii,
    extract_amounts,
    verify_math,
    apply_guardrails
)


# ─────────────────────────────────────────────
# Test 1: check_scope
# ─────────────────────────────────────────────
print("=" * 50)
print("TEST 1: check_scope")
print("=" * 50)

test_questions = [
    ("Why was the $320.45 charge deducted?", True),
    ("What is my total balance due?", True),
    ("What is the weather in Hyderabad?", False),
    ("Tell me a joke", False),
    ("Why?", True),                     # short follow-up → allow
    ("List all transactions", True),
]

for question, expected in test_questions:
    result, message = check_scope(question)
    status = "✅" if result == expected else "❌ WRONG"
    print(f"{status} | in_scope={result} | '{question[:40]}'")


# ─────────────────────────────────────────────
# Test 2: sanitize_pii
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("TEST 2: sanitize_pii")
print("=" * 50)

test_texts = [
    "Your card 4532 1234 5678 9010 was charged $320.45",
    "Account number 4532123456789010 shows a balance",
    "SSN on file: 123-45-6789",
    "The charge of $320.45 was for AWS EC2 Usage",  # no PII — should be unchanged
]

for text in test_texts:
    result = sanitize_pii(text)
    print(f"Input:  {text}")
    print(f"Output: {result}")
    print()


# ─────────────────────────────────────────────
# Test 3: extract_amounts
# ─────────────────────────────────────────────
print("=" * 50)
print("TEST 3: extract_amounts")
print("=" * 50)

text = """
The charge of $320.45 was for AWS EC2 Usage.
Your Netflix subscription costs $15.99 per month.
Total balance due is $4,512.78.
"""

amounts = extract_amounts(text)
print(f"Extracted amounts: {amounts}")
# Expected: [320.45, 15.99, 4512.78]


# ─────────────────────────────────────────────
# Test 4: verify_math
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("TEST 4: verify_math")
print("=" * 50)

document = """
| Date       | Description    | Amount  |
|------------|----------------|---------|
| 12/02/2026 | AWS EC2 Usage  | $320.45 |
| 12/02/2026 | Netflix        | $15.99  |
Total Due: $4,512.78
"""

# Case 1: all amounts verified
good_answer = "The $320.45 charge was for AWS EC2 Usage."
result = verify_math(good_answer, document)
print(f"Good answer → verified: {result['is_verified']}")

# Case 2: hallucinated amount
bad_answer = "The charge was $999.00 for AWS EC2 Usage."
result = verify_math(bad_answer, document)
print(f"Bad answer  → verified: {result['is_verified']}")
print(f"Flagged: {result['flagged_amounts']}")


# ─────────────────────────────────────────────
# Test 5: apply_guardrails (full pipeline)
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("TEST 5: apply_guardrails full pipeline")
print("=" * 50)

agent_answer = (
    "Your card 4532 1234 5678 9010 was charged $320.45 "
    "for Amazon Web Services EC2 Usage on 12/02/2026. "
    "This reflects your cloud computing usage. "
    "Your total due is $999.00."   # ← hallucinated number
)

result = apply_guardrails(agent_answer, document, "Why was I charged?")

print(f"Final answer:\n{result['final_answer']}")
print(f"\nMath verified: {result['math_verified']}")
print(f"Warnings: {result['warnings']}")