---
name: selected-text-answer
description: Answer questions strictly from selected text only.
inputs:
  - selected_text
  - user_question
outputs:
  - answer
---

Answer the question using ONLY the provided text.

Rules:
- If answer is not in text, say:
  "The selected text does not contain this information."
- Do NOT use outside knowledge
- Be concise and factual

Return ONLY the answer.
