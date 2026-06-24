# anki-english-card-skill

A Codex skill for generating concise English Anki cards and writing them to a
local Anki collection through AnkiConnect.

The skill is designed for vocabulary, phrases, sentence patterns, and grammar
structures. It combines card-writing rules, AnkiConnect workflow rules, and a
small helper script so generated cards stay consistent and safe to add.

## What It Does

- Generates English Anki cards for words, phrases, sentence patterns, and
  grammar structures.
- Uses concise learner-focused card content instead of full dictionary entries.
- Prefers British English spelling and phonetics.
- Writes generated cards to local Anki through AnkiConnect when requested.
- Can maintain existing notes, decks, cards, or tags only when the user
  explicitly asks for that operation.

## Requirements

- Codex with local skill support.
- Anki Desktop installed and running.
- The AnkiConnect add-on installed and enabled.
- A target Anki deck, or a deck name close enough for the skill's matching
  rules to resolve safely.

## Installation

Place this directory under your Codex skills directory:

```text
$CODEX_HOME/skills/anki-english-card-skill
```

On Windows, that is commonly:

```text
C:\Users\<you>\.codex\skills\anki-english-card-skill
```

## Usage

Invoke the skill by name when asking Codex to create English Anki cards.

```text
Use anki-english-card-skill to make cards for: come up with, carry out,
take into account. Add them to my IELTS deck.
```

```text
Use anki-english-card-skill to create a grammar card for "used to do".
```

```text
Use anki-english-card-skill to generate 10 concise phrase cards for academic
writing and write them to my English deck.
```

## Card Style

- Ordinary word and phrase fronts default to lowercase.
- Proper nouns keep normal capitalization.
- Cards should be short enough to review comfortably.
- Examples should support memory and usage, not overload the card.
- The final batch should be checked before writing to Anki.

Detailed card rules live in
[`references/card-generation-spec.md`](references/card-generation-spec.md).

## Anki Writing Workflow

When writing cards to local Anki, the skill uses
[`scripts/add_anki_card.py`](scripts/add_anki_card.py) as the default wrapper
around AnkiConnect.

The workflow is documented in
[`references/anki-connect-workflow.md`](references/anki-connect-workflow.md).

## Safety Rules

- Do not directly edit the Anki database.
- Use AnkiConnect for local Anki interaction.
- Do not delete, move, tag, or edit existing cards unless explicitly requested.
- Back up local Anki data before modifying existing content.
- If cards are added but sync fails, report the add as successful and the sync
  as failed instead of treating the whole operation as failed.

## Project Structure

```text
anki-english-card-skill/
├── SKILL.md
├── references/
│   ├── anki-connect-workflow.md
│   └── card-generation-spec.md
└── scripts/
    └── add_anki_card.py
```

## Limitations

- The write workflow requires Anki Desktop and AnkiConnect to be available.
- Deck-name matching is conservative; ambiguous matches should be confirmed.
- Existing-content modifications require an explicit user request and a backup.
- This skill is intended for Codex skill usage, not as a standalone Anki add-on.
