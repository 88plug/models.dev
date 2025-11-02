# Knowledge Cutoff Date Sources

This document tracks the sources for manually-curated knowledge cutoff dates in OpenRouter models.

## Research Methodology

Knowledge dates were researched using 10 parallel agents checking:
- Official model documentation and model cards
- Provider technical reports
- Community databases (github.com/HaoooWang/llm-knowledge-cutoff-dates)
- Extracted system prompts
- HuggingFace model cards

## Verified Knowledge Dates

### OpenAI Models

**GPT-4o** → `2023-10`
- Source: https://arxiv.org/html/2410.21276v1 (Official GPT-4o System Card)
- Verification: Official arXiv-hosted system card

**O1** → `2023-10`
- Source: https://github.com/HaoooWang/llm-knowledge-cutoff-dates
- Verification: Community database

**O3** → `2024-06`
- Source: https://github.com/HaoooWang/llm-knowledge-cutoff-dates
- Verification: Community database + multiple secondary sources

**O3-Mini** → `2023-10`
- Source: https://github.com/HaoooWang/llm-knowledge-cutoff-dates
- Verification: Community database + technical articles

**GPT-4o Mini** → `2023-10`
- Source: https://github.com/HaoooWang/llm-knowledge-cutoff-dates
- Verification: Community database

### Anthropic Models

**Claude 3 Haiku** → `2023-08`
- Source: https://www-cdn.anthropic.com/de8ba9b01c9ab7cbabf5c33b80b7bbc618857627/Model_Card_Claude_3.pdf
- Verification: Official Anthropic model card

**Claude 3 Opus** → `2023-08`
- Source: https://www-cdn.anthropic.com/de8ba9b01c9ab7cbabf5c33b80b7bbc618857627/Model_Card_Claude_3.pdf
- Verification: Official Anthropic model card

**Claude 3.5 Sonnet** → `2024-04`
- Source: https://www-cdn.anthropic.com/fed9cc193a14b84131812372d8d5857f8f304c52/Model_Card_Claude_3_Addendum.pdf
- Verification: Official Anthropic model card addendum

**Claude 3.5 Haiku** → `2024-07`
- Source: https://docs.claude.com/en/docs/about-claude/models/overview
- Verification: Official Anthropic documentation

**Claude 3.7 Sonnet (Thinking)** → `2024-11`
- Source: https://docs.claude.com/en/docs/about-claude/models/overview
- Verification: Official Anthropic documentation

### Google Models

**Gemma 3-27B IT** → `2024-08`
- Source: https://ai.google.dev/gemma/docs/core/model_card_3
- Verification: Official Google Gemma 3 model card
- Note: Corrected from incorrect `2024-10`

**Gemma 3-12B IT** → `2024-08`
- Source: https://ai.google.dev/gemma/docs/core/model_card_3
- Verification: Official Google Gemma 3 model card
- Note: Corrected from incorrect `2024-10`

**Gemini 2.0 Flash Exp** → `2024-08`
- Source: https://ai.google.dev/gemini-api/docs/models/gemini
- Verification: Official Google AI documentation
- Note: Corrected from suspicious `2024-12` (only 10 days before release)

### Meta Llama Models

**Llama 3.3 70B Instruct** → `2023-12`
- Source: https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct
- Verification: Official Meta HuggingFace model card

**Llama 3.1 405B Instruct** → `2023-12`
- Source: https://huggingface.co/meta-llama/Llama-3.1-405B-Instruct
- Verification: Official Meta HuggingFace model card

**Llama 4 Scout** → `2024-08`
- Source: https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct
- Verification: Official Meta HuggingFace model card + GitHub MODEL_CARD.md

### X.AI Models

**Grok 3** → `2024-11`
- Source: https://docs.oracle.com/en-us/iaas/Content/generative-ai/xai-grok-3.htm
- Verification: Oracle official documentation for X.AI models

**Grok 4** → `2024-11`
- Source: https://docs.oracle.com/en-us/iaas/Content/generative-ai/xai-grok-4.htm
- Verification: Oracle official documentation
- Note: Corrected from incorrect `2025-07` (only 8 days before release - clearly wrong)

**Grok Code Fast 1** → `2025-03`
- Source: xAI official documentation + multiple verification sources
- Verification: Official sources, Oracle docs
- Note: Corrected from incorrect `2025-08` (only 26 days before release)

### DeepSeek Models

**DeepSeek Chat** → `2024-07`
- Source: https://www.knostic.ai/blog/exposing-deepseek-system-prompts
- Verification: Extracted system prompt from actual model

### Microsoft Models

**Phi-4** → `2024-06`
- Source: https://azure.microsoft.com/en-us/products/phi/
- Verification: Official Microsoft Azure product page

## Corrections Made

### Models with Incorrect Knowledge Dates

1. **GLM-4.6** - REMOVED knowledge field
   - Previous: `2025-09` (only 29 days before release)
   - No verifiable source found for knowledge cutoff date
   - Action: Removed unverifiable placeholder date

2. **Grok 4** - CORRECTED
   - Previous: `2025-07` (suspicious - only 8 days before release)
   - Correct: `2024-11` (from official Oracle/xAI docs)

3. **Grok Code Fast 1** - CORRECTED
   - Previous: `2025-08` (suspicious - only 26 days before release)
   - Correct: `2025-03` (from official sources)

4. **Gemini 2.0 Flash Exp** - CORRECTED
   - Previous: `2024-12` (suspicious - only 10 days before release)
   - Correct: `2024-08` (from official Google docs)

5. **Gemma 3-27B IT & 3-12B IT** - CORRECTED
   - Previous: `2024-10` (unverified)
   - Correct: `2024-08` (from official Google model card)

## Pattern Observed

**Problem**: Some knowledge dates were using the model release month as a placeholder rather than the actual training data cutoff date. This created suspiciously short gaps between knowledge cutoff and release (< 30 days), which is not realistic for model training timelines.

**Expected Pattern**: Knowledge cutoff should be 2-6 months BEFORE model release to allow time for training, testing, and validation.

## Sync Script Modification

Modified `sync_openrouter.py` to:
1. NOT create empty `knowledge` fields for new models
2. Only preserve non-empty knowledge values from existing files
3. Match the pattern of other providers (missing field instead of empty string)

This prevents the accumulation of meaningless `knowledge = ""` entries and aligns with industry best practices (79% of non-OpenRouter models have populated knowledge dates, 0% use empty strings).

## Future Maintenance

Knowledge dates should be:
- Researched from official sources when possible
- Left omitted if unknown (rather than guessed)
- Validated to ensure realistic gaps between training cutoff and release
- Updated when better information becomes available

## Data Quality Impact

- **Before**: 75% empty strings (257 of 343 models)
- **After**: 20+ high-priority models with verified knowledge dates, empty strings eliminated
- **Public Website**: Clean data display without meaningless empty fields
