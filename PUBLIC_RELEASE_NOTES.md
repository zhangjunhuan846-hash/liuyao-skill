# Public Release Notes

This package is a GitHub-ready release of `liuyao-iterative-divination`.

## What changed

- Added structured xiangyi registry: `knowledge/05_xiangyi_registry/xiangyi_registry.yml`.
- Added topic-specific divination rules: `knowledge/06_topic_rules/topic_rules.yml`.
- Integrated retrieval policy v2 into `config/retrieval_policy.yml`.
- Replaced the book manifest with a metadata-driven manifest template.
- Upgraded feedback schema to v2 and kept it as the default `feedback_schema.json`.
- Added `resources/templates/fresh_output_template_v2.md`.
- Added `scripts/validate_pack.py`.
- Expanded Codex regression prompts.
- Appended skill rules for xiangyi boundaries, modern topic mapping, and fresh-mode hard isolation.

## Removed from this public package

- Raw OCR / MinerU book text.
- Corrected book text.
- Generated book index files.
- Runtime case memory and feedback logs.
- Raw PDF files.
- Personal notes.

## Local use

For local full use, place your private corpora back into the ignored directories and regenerate indexes locally. Do not commit those files.
