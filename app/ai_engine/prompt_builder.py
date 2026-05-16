"""
Prompt Builder — Constructs AI prompts for all engine tasks.
"""

from __future__ import annotations

from app.ai_engine.ai_constants import (
    CANDIDATE_EXPERIENCE_YEARS,
    CANDIDATE_NAME,
    CANDIDATE_ROLE,
    CANDIDATE_SKILLS,
)


class PromptBuilder:
    """Builds structured prompts for AI providers."""

    @staticmethod
    def _candidate_context() -> str:
        skills = ", ".join(CANDIDATE_SKILLS)
        return (
            f"You are helping {CANDIDATE_NAME}, a {CANDIDATE_ROLE} "
            f"with {CANDIDATE_EXPERIENCE_YEARS}+ years of experience.\n"
            f"Core skills: {skills}\n"
        )

    @classmethod
    def build_match_scoring_prompt(
        cls,
        job_title: str,
        company_name: str,
        job_description: str,
        tech_stack: list[str] | None = None,
    ) -> str:
        tech_info = f"\nDetected tech stack: {', '.join(tech_stack)}" if tech_stack else ""
        return f"""
{cls._candidate_context()}
=== JOB OPPORTUNITY ===
Title: {job_title}
Company: {company_name}{tech_info}
Description:
{job_description}

=== TASK ===
Analyze this job against the candidate's profile. Return a JSON object with:
{{
  "match_score": <number 0-100>,
  "reasoning": "<detailed multi-point reasoning>",
  "job_category": "<category: Automation|Manual|Prompt Engineer|AI Engineer|SDET|Other>",
  "confidence": <0.0-1.0>,
  "prediction_market": "<Bullish|Neutral|Bearish> — <win rate description>",
  "interview_questions": ["<question1>", "<question2>", ...],
  "portfolio_suggestions": ["<suggestion1>", ...]
}}

Be aggressive and precise. Score 90+ only for elite matches.
Return ONLY valid JSON. No markdown. No explanation outside JSON.
""".strip()

    @classmethod
    def build_cover_letter_prompt(
        cls,
        job_title: str,
        company_name: str,
        job_description: str,
        match_score: float,
        reasoning: str,
    ) -> str:
        return f"""
{cls._candidate_context()}
=== JOB DETAILS ===
Title: {job_title}
Company: {company_name}
Match Score: {match_score}/100
Key Match Reasoning: {reasoning}

Job Description:
{job_description[:2000]}

=== TASK ===
Write a hyper-personalized, compelling cover letter for {CANDIDATE_NAME}.
Rules:
- Maximum 350 words
- Reference specific company tech or values if detectable
- Highlight QA Automation, AI Automation, and Playwright expertise
- Use confident, professional tone (GOAT mentality)
- End with a strong call to action
- Return ONLY the cover letter text, no subject line, no JSON
""".strip()

    @classmethod
    def build_interview_prep_prompt(
        cls,
        job_title: str,
        company_name: str,
        job_description: str,
    ) -> str:
        return f"""
{cls._candidate_context()}
=== JOB ===
Title: {job_title} at {company_name}
Description: {job_description[:1500]}

=== TASK ===
Generate 10 likely interview questions for this role, including:
- 3 technical QA/automation questions
- 2 behavioral (STAR format) questions  
- 2 situational problem-solving questions
- 2 AI/Prompt Engineering questions
- 1 company-specific question

For each question, also provide a model answer for {CANDIDATE_NAME}.

Return JSON:
{{
  "questions": [
    {{"question": "...", "type": "technical", "model_answer": "..."}},
    ...
  ]
}}
Return ONLY valid JSON.
""".strip()

    @classmethod
    def build_portfolio_prompt(
        cls,
        job_title: str,
        company_name: str,
        tech_stack: list[str],
    ) -> str:
        skills = ", ".join(CANDIDATE_SKILLS)
        tech = ", ".join(tech_stack) if tech_stack else "undetected"
        return f"""
{cls._candidate_context()}
=== TARGET JOB ===
Title: {job_title} at {company_name}
Company Tech Stack: {tech}
Candidate Skills: {skills}

=== TASK ===
Suggest 5 specific portfolio project ideas that would maximally impress this company.
Each project should demonstrate skills relevant to their detected tech stack.
Focus on QA automation, AI integration, and measurable impact.

Return JSON:
{{
  "portfolio_projects": [
    {{
      "title": "...",
      "description": "...",
      "tech_used": [...],
      "impact": "..."
    }}
  ]
}}
Return ONLY valid JSON.
""".strip()
