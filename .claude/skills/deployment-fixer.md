---
name: deployment-fixer
description: Fix Docusaurus GitHub Pages and Vercel deployment issues.
inputs:
  - error_logs
outputs:
  - fix_steps
---

Analyze the deployment error logs.

Rules:
- Identify root cause
- Suggest minimal fix
- Avoid unnecessary refactoring

Return step-by-step fix instructions.
