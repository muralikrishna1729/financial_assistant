import sys
from pathlib import Path

from core.agent import build_agent, stream_agent_response
from core.tools import search_merchant


# ─────────────────────────────────────────────
# Test 1: Search Tool standalone
# ─────────────────────────────────────────────
print("=" * 50)
print("TEST 1: search_merchant tool")
print("=" * 50)

result = search_merchant.invoke("AWS EC2 charge bank statement")
print(result)


# ─────────────────────────────────────────────
# Test 2: Agent with sample document
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("TEST 2: Agent streaming response")
print("=" * 50)

# Simulated parsed markdown from Phase 1
sample_document = """
| Date       | Description                   | Amount  | Balance   |
|------------|-------------------------------|---------|-----------|
| 12/02/2026 | Payment                       | $300.00 | $5,660.00 |
| 12/02/2026 | Amazon Web Services EC2 Usage | $320.45 | $4,512.78 |
| 12/02/2026 | Netflix Subscription          | $15.99  | $4,496.79 |
| 12/02/2026 | Grocery Store Purchase        | $74.32  | $4,422.47 |

Previous Balance: $4,215.60
Payments Received: -$600.00
New Charges: $947.68
Taxes & Fees: $24.50
Total Due: $4,512.78
"""

agent = build_agent(sample_document)

print("\nQuestion: Why was the $320.45 charge deducted?\n")
print("Answer: ", end="", flush=True)

for chunk in stream_agent_response(agent, "Why was the $320.45 charge deducted?", []):
    print(chunk, end="", flush=True)

print("\n")