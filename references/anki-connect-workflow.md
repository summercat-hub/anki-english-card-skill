# AnkiConnect Workflow

Use this reference when writing generated cards to local Anki or when explicitly requested to maintain existing Anki content.

## Preconditions

- Anki Desktop must be open.
- AnkiConnect must be installed and reachable at `http://127.0.0.1:8765`.
- Do not write directly to `collection.anki2`.
- Use AnkiConnect as the default interface for local Anki operations.
- Adding newly generated cards is the only write workflow that does not require a pre-change backup by default.
- For existing-note/card/deck/tag modifications, create a local Anki backup before making any change.
- Use `scripts/add_anki_card.py` by default.

## Defaults

- `connect_url`: `http://127.0.0.1:8765`
- `modelName`: `问答题`
- `front field`: `正面`
- `back field`: `背面`
- `tags`: empty by default
- duplicates: allowed by default
- sync: enabled by default

Do not add `Codex Generated` or any other tag unless the user explicitly requests tags.

## Add-note procedure

1. Generate card fronts and backs according to `card-generation-spec.md`.
2. Use `scripts/add_anki_card.py` for the write.
3. Confirm AnkiConnect is reachable.
4. Resolve the target deck name using the Deck Name Matching rules below, then check that the resolved deck exists.
5. Check that the note type exists.
6. Check that the front and back fields exist.
7. Search for possible duplicates in the target deck.
8. Treat a note as duplicate only when the front field exactly matches the generated front after HTML unescaping, HTML stripping, and whitespace normalization.
9. Run the final full-batch quality check in `card-generation-spec.md`. This is the only content-quality check for generated cards; it must cover sense separation, examples, Chinese translations, and Tip necessity before any write that will sync.
10. Add the note with `addNote`.
11. Verify the technical write result with `notesInfo`:
    - note exists
    - front field matches the generated front
    - back field HTML matches the generated back after whitespace normalization
12. Sync Anki unless the user explicitly asked not to sync.
13. Report:
    - successful add count
    - failed add count
    - resolved deck name if it differs from the user's wording
    - possible duplicate fronts and existing note ids, if any
    - final-check status
    - sync status
    - specific failure points, if any

## Batch procedure

For more than one card, prefer the helper script's `--cards-file` mode.

The cards file should be UTF-8 JSON:

```json
[
  {
    "front": "humid",
    "back": "<div class=\"phonetic\">/ˈhjuː.mɪd/</div>\n\n<div class=\"meanings\">...</div>"
  }
]
```

Before using the script for a batch, run the final full-batch quality check in `card-generation-spec.md` against the complete cards file. The script should then add all valid checked cards and sync once at the end. If sync fails after cards were added, report the cards as added and sync as failed.

## Deck Name Matching

- Do not require the user to type the exact deck name.
- First prefer an exact deck-name match.
- If there is no exact match, normalize the user's phrase and current deck names by ignoring case, whitespace, punctuation, and generic words such as `deck`, `牌组`, and `卡组`.
- If exactly one current deck has a clear normalized or keyword-containing match, use that deck directly without asking for confirmation.
- Example: if the user says `测试牌组` and the current deck list contains `测试`, write to `测试`.
- Ask the user only when no related deck exists or when multiple decks are equally plausible.
- In the final result, report the actual deck written to when it differs from the user's wording.

## Existing Content Maintenance

Only use this workflow when the user explicitly asks to modify existing Anki content, such as updating old card backs to match the current card-generation format, deleting notes/cards, moving cards between decks, or adding/removing tags.

Required procedure:

1. Identify the target notes/cards/decks/tags through AnkiConnect queries.
2. Show or summarize the intended scope when the operation could affect multiple existing notes.
3. Create a local Anki backup before any modification.
4. Apply the requested operation through AnkiConnect.
5. For operations that change card text or HTML, run the final full-batch quality check in `card-generation-spec.md` on all changed cards before syncing. This is the only content-quality check for changed cards; it must cover sense separation, examples, Chinese translations, and Tip necessity.
6. Verify the technical write result through AnkiConnect after the write.
7. Sync once at the end unless the user explicitly asks not to sync.
8. Report:
   - exact operation type
   - number of notes/cards affected
   - tags added or removed, if any
   - decks affected, if any
   - final-check status, when card text or HTML changed
   - failures or skipped items, if any
   - backup location or backup confirmation
   - that the pre-change version was backed up and can be restored

For bulk edits that reformat old cards, preserve the existing note type, field names, card identity, scheduling history, and user-owned content unless the user explicitly asks to change them. Update only the fields needed to match the current card-generation format.

## Failure handling

- If AnkiConnect connection fails, stop and tell the user to open Anki Desktop and ensure AnkiConnect is installed/enabled.
- If no related deck matches the user's requested deck phrase, stop and ask the user to confirm the deck name.
- If multiple decks are equally plausible matches, stop and list the candidates for user confirmation.
- If the note type does not exist, stop and report the missing note type.
- If required fields do not exist or the field mapping does not match, stop and report the mismatch.
- If adding succeeds but sync fails, report that cards were added and sync failed.
- For batch adds, do not hide partial success or partial failure.
- If backup creation fails before an existing-content modification, stop and do not modify Anki.
- If an existing-content modification partially succeeds, report exactly what changed, what failed or was skipped, and that the pre-change version was backed up.

## Helper script examples

Single card:

```powershell
python "C:\Users\summer cat\.codex\skills\anki-english-card-skill\scripts\add_anki_card.py" --deck "Daily Vocabulary" --front "humid" --back-file "D:\path\to\back.html"
```

Batch:

```powershell
python "C:\Users\summer cat\.codex\skills\anki-english-card-skill\scripts\add_anki_card.py" --deck "Daily Vocabulary" --cards-file "D:\path\to\cards.json"
```

Skip sync only when the user explicitly asks not to sync:

```powershell
python "C:\Users\summer cat\.codex\skills\anki-english-card-skill\scripts\add_anki_card.py" --deck "Daily Vocabulary" --cards-file "D:\path\to\cards.json" --no-sync
```
