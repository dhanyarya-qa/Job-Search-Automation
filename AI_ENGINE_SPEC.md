
---

# `AI_ENGINE_SPEC.md`

```md id="mflj8u"
# AI_ENGINE_SPEC.md

# MODULE PURPOSE

Build an AI orchestration engine for:
- job matching
- cover letter generation
- interview prediction
- portfolio generation
- AI scoring

---

# REQUIRED PROVIDERS

Mandatory integrations:
- OpenAI
- Anthropic
- Gemini

Optional:
- OpenRouter
- LangChain

---

# REQUIRED STRUCTURE

app/ai_engine/
│
├── orchestrator.py
├── provider_manager.py
├── openai_provider.py
├── anthropic_provider.py
├── gemini_provider.py
├── prompt_builder.py
├── cover_letter_engine.py
├── scoring_engine.py
├── interview_engine.py
├── portfolio_generator.py
├── response_parser.py
├── retry_handler.py
└── ai_constants.py

---

# REQUIRED FEATURES

## Match Scoring

Generate:
- match_score
- reasoning
- job_category
- confidence
- prediction_market

Output format:

```json
{
  "match_score": 95,
  "reasoning": "",
  "job_category": "Automation",
  "prediction_market": "Bullish - 85% Win Rate"
}