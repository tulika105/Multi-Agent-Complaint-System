# Component-Level Benchmark Evaluation of a Multi-Agent Complaint System

This document presents a benchmark evaluation of the core agent logic using a manually curated golden test dataset of 10 input/output pairs. Each input was run through the live system and the agent's output was recorded and compared against the expected output.

**Metrics measured:**
- Routing Accuracy — did the supervisor correctly classify the input as `complaint` or `general`?
- Severity Accuracy — did the complaint agent correctly classify urgency as `HIGH`, `MEDIUM`, or `LOW`?
- Error Rate — what percentage of responses contained any mistake?

---

## Test Cases

| # | Input | Expected Routing | Agent Routing | Routing Pass/Fail | Expected Severity | Agent Severity | Severity Pass/Fail |
|---|-------|-----------------|---------------|-------------------|-------------------|----------------|--------------------|
| 1 | "My amazon product 88892 has been stolen" | complaint | complaint | PASS | HIGH | HIGH | PASS |
| 2 | "My order has not received yet" | complaint | complaint | PASS | MEDIUM | MEDIUM | PASS |
| 3 | "Order #5512 has a small scratch on the back panel. It still works fine." | complaint | complaint | PASS | LOW | LOW | PASS |
| 4 | "What is your refund policy? Also, I want to return my damaged product from Order 8810" | complaint | complaint | PASS | HIGH | HIGH | PASS |
| 5 | "How long does Amazon India's standard delivery take to rural areas?" | general | general | PASS | N/A | N/A | N/A |
| 6 | "My Amazon India order 9021 is delayed by 5 days" | complaint | complaint | PASS | HIGH | LOW | FAIL |
| 7 | "Does Flipkart SuperCoins expire if I don't use them?" | general | general | PASS | N/A | N/A | N/A |
| 8 | "I ordered food on Zomato (Order ZM8821) and it arrived cold and 45 min late. The restaurant had marked it as delivered on time which is a lie." | complaint | complaint | PASS | HIGH | MEDIUM | FAIL |
| 9 | "My order 56788 came late from swiggy never gonna order again" | complaint | complaint | PASS | MEDIUM | LOW | FAIL |
| 10 | "My 6 year old daughter swallowed a small detachable part from the toy I ordered on Flipkart (Order #FK4421). We are rushing to the hospital right now." | complaint | complaint | PASS | HIGH | HIGH | PASS |

> **Note:** Severity is tested for all complaint inputs (cases 1, 2, 3, 4, 6, 8, 9, 10 — 8 total). General queries (cases 5 and 7) are marked N/A.

---

## Results

| Metric | Formula | Score |
|--------|---------|-------|
| Routing Accuracy | (Correct routing predictions / 10) × 100 | **100%** (10/10) |
| Severity Accuracy | (Correct severity predictions / 8) × 100 | **63%** (5/8) |
| Error Rate | (Inputs with any mistake / 10) × 100 | **30%** (3/10) |

---

## Confusion Matrices

![Confusion Matrix(Severity)](<Screenshot 2026-05-06 133408.png>) ![Confusion Matrix(Routing)](<Screenshot 2026-05-06 133326.png>)

---
## Failure Details

### Case 6 — Severity FAIL
**Input:** "My Amazon India order 9021 is delayed by 5 days"
- Expected: `HIGH` — a 5-day delivery delay represents significant customer inconvenience and a high churn risk
- Agent returned: `LOW`
- Gap: Two-level miss. The agent significantly underestimated the urgency of a multi-day unresolved delay

### Case 8 — Severity FAIL
**Input:** "I ordered food on Zomato (Order ZM8821) and it arrived cold and 45 min late. The restaurant had marked it as delivered on time which is a lie."
- Expected: `HIGH` — fraudulent status marking is a platform integrity violation that goes beyond a standard delivery complaint. It signals a restaurant gaming the system, which poses legal, reputational, and trust risks to the platform
- Agent returned: `MEDIUM`
- Gap: One-level miss. The agent treated this as a standard food quality complaint and missed the business impact of the fraudulent reporting

### Case 9 — Severity FAIL
**Input:** "My order 56788 came late from swiggy never gonna order again"
- Expected: `MEDIUM` — late delivery combined with an explicit churn signal ("never gonna order again") indicates moderate-to-high business impact
- Agent returned: `LOW`
- Gap: One-level miss. The agent underweighted the churn signal and treated the complaint as low priority

---

## Analysis

- The supervisor correctly routed 10/10 inputs, demonstrating strong intent classification across diverse complaint types, tones, and company names. It handled vague inputs ("My order has not received yet"), mixed intent ("What is your refund policy? Also, I want to return my damaged product"), and emotionally charged language ("never gonna order again") without misrouting.

- Severity classification was accurate for clear-cut extremes — stolen products, child safety emergencies, and cosmetic damage were all correctly identified. The failure mode is specific: the complaint agent under-escalates when business impact is high but explicit physical danger keywords are absent. All three failures (cases 6, 8, and 9) fall into this category.

- Error rate is 30%, driven entirely by severity misclassifications. There are zero routing errors on complaint cases and zero false positives on general queries.

- The main finding is a systematic under-escalation bias on delivery and platform integrity complaints. The agent appears to rely heavily on keywords like "injury", "stolen", or "damaged" to trigger HIGH severity, and does not adequately weight operational signals such as multi-day delays, fraudulent status reporting, or customer churn language.

---


## Evaluation Method

This evaluation was conducted using **manual human evaluation** on a golden test dataset of 10 curated input/output pairs. Each input was run through the live system and the agent's output was recorded from session logs and compared against the expected label. Metrics were calculated manually using the formulas above. All judgments were made by human reviewers against predefined golden labels.

### Dataset design

- Test cases were selected to cover a range of complaint types (theft, delay, damage, food quality, safety), general query types (policy, delivery time), and mixed intent inputs
- Companies used: Amazon India, Flipkart, Zomato, Swiggy — deliberately varied to test generalization across brand names
- Edge cases included: vague complaints with no order ID, emotionally charged language, mixed intent queries, and a life-threatening emergency
- Expected severity labels were set from a **business impact perspective**, not purely from a customer experience perspective. For example, fraudulent delivery status marking was labelled HIGH because of platform integrity implications, not just customer inconvenience

