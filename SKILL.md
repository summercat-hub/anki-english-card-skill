---
name: anki-english-card-skill
description: Generate English vocabulary, phrase, sentence-pattern, and grammar-structure Anki cards in the user's established format, write them to local Anki through AnkiConnect, and maintain existing Anki notes or tags when explicitly requested.
metadata:
  display-name: anki-english-card-skill
  short-description: Generate and import English Anki cards
---

# anki-english-card-skill

This skill is usually invoked explicitly by the user with words, phrases, sentence patterns, or grammar structures to turn into Anki cards. Its primary purpose is generating new Anki cards. It may also maintain existing Anki notes, cards, decks, or tags through AnkiConnect when the user explicitly asks for that operation.

## What to read

- Before generating card content, read `references/card-generation-spec.md`.
- Before writing to Anki, read `references/anki-connect-workflow.md`.
- If the user only asks for card text and does not want Anki import, `references/anki-connect-workflow.md` is not needed.

## Default workflow

- Generate one card per supplied word, phrase, sentence pattern, or structure unless the user asks otherwise.
- If the user specifies a target deck for new cards, generate the cards and write them directly to that deck.
- If the user asks to import/add/write cards but does not specify a deck, ask for the target deck before writing.
- Do not require preview or confirmation by default.
- Allow duplicate fronts by default. If duplicates are detected, still add the new cards and report possible duplicate fronts and existing note ids in the final summary.
- Do not add tags unless the user explicitly asks for tags.
- Do not edit, delete, retag, or otherwise modify existing Anki content unless the user explicitly asks for an existing-content maintenance operation.
- After generating or preparing all card changes for the current request, run one final full-batch quality check before any write that will sync. The check must cover content quality, especially sense separation, example coverage, Chinese translations, and Tip necessity, not only field or HTML format.

## Card generation

Follow `references/card-generation-spec.md`.

Important defaults:

- New ordinary word and phrase fronts default to lowercase.
- Proper nouns keep normal capitalization.
- British English spelling and phonetics are preferred.
- Cards should be concise and useful for vocabulary memory, not full dictionary entries.

## Anki import

When writing to local Anki:

1. Follow `references/anki-connect-workflow.md`.
2. Use `scripts/add_anki_card.py` as the default wrapper for AnkiConnect writes.
3. Do not hand-write AnkiConnect requests unless the script is unavailable or the user explicitly requests an operation the script does not support.
4. If bypassing the script, briefly explain why.
5. Run the final full-batch quality check from `references/card-generation-spec.md` before writing generated cards.
6. For batches, add all checked cards and sync only once at the end unless the user explicitly asks not to sync.
7. Report successful adds, failures, possible duplicates, resolved deck name, final-check status, and sync status.

When modifying existing Anki content:

1. Follow `references/anki-connect-workflow.md`.
2. Use AnkiConnect as the default interface. Do not directly edit the local Anki database files.
3. Treat adding newly generated cards as the only write workflow that does not require a pre-change backup by default.
4. Before any edit, delete, tag add/remove, deck move, or bulk update of existing Anki content, create a local Anki backup according to `references/anki-connect-workflow.md`.
5. For edits that change card text or HTML, run the final full-batch quality check from `references/card-generation-spec.md` before syncing.
6. After the operation, report what changed, final-check status, and state that the pre-change version was backed up and can be restored.

## Error handling

- If AnkiConnect is unavailable, stop and tell the user to open Anki Desktop and ensure AnkiConnect is installed/enabled.
- If the requested deck is not an exact deck name, use the deck-name matching rules in `references/anki-connect-workflow.md`.
- If no related deck exists or multiple decks are equally plausible, stop and ask the user to confirm the deck.
- If the note type or required fields do not exist, stop and report the mismatch.
- If a batch partially succeeds, report partial success and partial failure accurately.
- If adding succeeds but sync fails, report that the cards were added and sync failed; do not describe the whole operation as failed.

## Rule priority

Apply rules in this order:

1. Safety rule in this file.
2. The user's explicit request in the current turn.
3. `references/anki-connect-workflow.md` when writing to Anki.
4. `references/card-generation-spec.md`.
5. Default workflow in this file.

## Safety rule

Do not directly modify the Anki local database. Use AnkiConnect by default for all local Anki interaction. Do not delete cards, edit existing card content, move cards, or add/remove tags unless the user explicitly asks for that operation. For any existing-content modification, back up the local Anki data before making changes and report the backup in the final response.
