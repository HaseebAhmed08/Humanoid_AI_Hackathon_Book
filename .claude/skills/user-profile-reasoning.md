---
name: user-profile-reasoning
description: Decide content difficulty based on user background.
inputs:
  - user_profile
  - chapter_topic
outputs:
  - difficulty_level
  - focus_areas
---

Analyze the user profile.

Rules:
- Determine beginner / intermediate / advanced level
- Identify whether user is software-heavy or hardware-heavy
- Recommend focus areas
- Do NOT modify content directly

Return structured JSON.
