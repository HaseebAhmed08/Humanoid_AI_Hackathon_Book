---
name: mdx-chapter-generator
description: Convert structured outlines into clean Docusaurus MDX chapters.
inputs:
  - chapter_outline
outputs:
  - mdx_chapter
---

Generate a Docusaurus-compatible MDX chapter.

Rules:
- Use proper Markdown headings
- Add a "Learning Outcomes" section
- Use code blocks where relevant
- Keep language clear and educational
- Output valid MDX only

Return ONLY the MDX content.
