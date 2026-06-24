#!/usr/bin/env python3
import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.request


DEFAULT_URL = "http://127.0.0.1:8765"
DEFAULT_MODEL = "问答题"
DEFAULT_FRONT_FIELD = "正面"
DEFAULT_BACK_FIELD = "背面"


class AnkiConnectError(RuntimeError):
    pass


def normalise_front(value):
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalise_html(value):
    value = html.unescape(value or "")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r">\s+<", "><", value)
    return re.sub(r"\s+", " ", value).strip()


def invoke(action, params=None, url=DEFAULT_URL):
    payload = json.dumps({"action": action, "version": 6, "params": params or {}}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise AnkiConnectError(
            f"AnkiConnect unavailable at {url}. Open Anki Desktop and ensure AnkiConnect is installed. Detail: {exc}"
        )
    except json.JSONDecodeError as exc:
        raise AnkiConnectError(f"Invalid JSON response from AnkiConnect action {action}: {exc}")

    if data.get("error"):
        raise AnkiConnectError(f"AnkiConnect error from {action}: {data['error']}")
    return data.get("result")


def quote_search(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def normalise_deck_name(value):
    value = (value or "").casefold()
    value = re.sub(r"(牌组|卡组|deck)", " ", value)
    value = re.sub(r"[^\w\u4e00-\u9fff]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def deck_tokens(value):
    return {token for token in normalise_deck_name(value).split() if token}


def deck_match_score(requested, candidate):
    if requested == candidate:
        return 100

    requested_norm = normalise_deck_name(requested)
    candidate_norm = normalise_deck_name(candidate)
    if not requested_norm or not candidate_norm:
        return 0
    if requested_norm == candidate_norm:
        return 90
    if requested_norm in candidate_norm or candidate_norm in requested_norm:
        return 80

    requested_tokens = deck_tokens(requested)
    candidate_tokens = deck_tokens(candidate)
    if requested_tokens and candidate_tokens:
        overlap = requested_tokens & candidate_tokens
        if overlap:
            return 60 + min(10, len(overlap))
    return 0


def resolve_deck_name(requested, decks):
    if requested in decks:
        return requested, None

    matches = []
    for deck in decks:
        score = deck_match_score(requested, deck)
        if score > 0:
            matches.append((score, deck))

    if not matches:
        raise AnkiConnectError(f"Deck not found: {requested}")

    matches.sort(key=lambda item: (-item[0], item[1].casefold()))
    best_score = matches[0][0]
    best = [deck for score, deck in matches if score == best_score]
    if len(best) > 1:
        raise AnkiConnectError(
            f"Deck name is ambiguous: {requested}. Possible matches: {', '.join(best)}"
        )

    return best[0], requested


def find_duplicate(deck, front, url, front_field):
    query = f"deck:{quote_search(deck)} {quote_search(front)}"
    ids = invoke("findNotes", {"query": query}, url)
    if not ids:
        return []

    notes = invoke("notesInfo", {"notes": ids}, url)
    exact = []
    target = normalise_front(front)
    for note in notes:
        fields = note.get("fields", {})
        value = fields.get(front_field, {}).get("value", "")
        if normalise_front(value) == target:
            exact.append(note.get("noteId"))
    return exact


def verify_note(note_id, front, back, url, front_field, back_field):
    notes = invoke("notesInfo", {"notes": [note_id]}, url)
    if not notes:
        return False, "created note was not returned by notesInfo"

    fields = notes[0].get("fields", {})
    got_front = fields.get(front_field, {}).get("value", "")
    got_back = fields.get(back_field, {}).get("value", "")

    if normalise_front(got_front) != normalise_front(front):
        return False, "front field mismatch"
    if normalise_html(got_back) != normalise_html(back):
        return False, "back field HTML mismatch"
    return True, "verified"


def read_text_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_cards(args):
    if args.cards_file:
        if args.front or args.back or args.back_file:
            raise SystemExit("Use either --cards-file or single-card arguments, not both.")
        try:
            data = json.loads(read_text_file(args.cards_file))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON in --cards-file: {exc}")
        if not isinstance(data, list):
            raise SystemExit("--cards-file must contain a JSON array.")

        cards = []
        for index, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                raise SystemExit(f"Card {index} must be a JSON object.")
            front = item.get("front")
            back = item.get("back")
            if not isinstance(front, str) or not front.strip():
                raise SystemExit(f"Card {index} has missing or invalid front.")
            if not isinstance(back, str) or not back.strip():
                raise SystemExit(f"Card {index} has missing or invalid back.")
            tags = item.get("tags", [])
            if tags is None:
                tags = []
            if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
                raise SystemExit(f"Card {index} tags must be a list of strings.")
            cards.append({"front": front, "back": back, "tags": tags})
        if not cards:
            raise SystemExit("--cards-file contains no cards.")
        return cards

    if not args.front:
        raise SystemExit("Single-card mode requires --front.")
    if bool(args.back) == bool(args.back_file):
        raise SystemExit("Single-card mode requires exactly one of --back or --back-file.")

    back = args.back if args.back is not None else read_text_file(args.back_file)
    return [{"front": args.front, "back": back, "tags": []}]


def add_one_card(card, args, deck, allow_duplicate):
    front = card["front"]
    back = card["back"]
    tags = args.tag + card.get("tags", [])

    duplicates = find_duplicate(deck, front, args.connect_url, args.front_field)
    if duplicates and not allow_duplicate:
        return {
            "status": "duplicate_skipped",
            "front": front,
            "duplicateNoteIds": duplicates,
            "added": False,
        }

    note_id = invoke("addNote", {
        "note": {
            "deckName": deck,
            "modelName": args.model,
            "fields": {
                args.front_field: front,
                args.back_field: back,
            },
            "options": {
                "allowDuplicate": allow_duplicate,
                "duplicateScope": "deck",
                "duplicateScopeOptions": {
                    "deckName": deck,
                    "checkChildren": False,
                    "checkAllModels": False,
                },
            },
            "tags": tags,
        }
    }, args.connect_url)

    verified, message = verify_note(
        note_id,
        front,
        back,
        args.connect_url,
        args.front_field,
        args.back_field,
    )

    return {
        "status": "added" if verified else "added_unverified",
        "front": front,
        "duplicateNoteIds": duplicates,
        "noteId": note_id,
        "added": True,
        "verified": verified,
        "verificationMessage": message,
    }


def main():
    parser = argparse.ArgumentParser(description="Add generated Anki cards through AnkiConnect.")
    parser.add_argument("--deck", required=True, help="Target Anki deck name or a clear deck phrase.")
    parser.add_argument("--front", help="Single-card front field content.")
    parser.add_argument("--back", help="Single-card back field HTML content.")
    parser.add_argument("--back-file", help="Path to a UTF-8 file containing single-card back field HTML.")
    parser.add_argument("--cards-file", help="Path to a UTF-8 JSON file containing an array of cards.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Anki note type. Default: {DEFAULT_MODEL}")
    parser.add_argument("--front-field", default=DEFAULT_FRONT_FIELD, help=f"Front field name. Default: {DEFAULT_FRONT_FIELD}")
    parser.add_argument("--back-field", default=DEFAULT_BACK_FIELD, help=f"Back field name. Default: {DEFAULT_BACK_FIELD}")
    parser.add_argument("--connect-url", default=DEFAULT_URL, help=f"AnkiConnect URL. Default: {DEFAULT_URL}")
    parser.add_argument("--tag", action="append", default=[], help="Optional global tag. Can be passed multiple times.")
    parser.add_argument("--allow-duplicate", action="store_true", help="Compatibility flag. Duplicates are already allowed by default.")
    parser.add_argument("--block-duplicate", action="store_true", help="Skip a card if the same front already exists in the target deck.")
    parser.add_argument("--no-sync", action="store_true", help="Skip Anki sync after adding. Use only when explicitly requested.")
    parser.add_argument("--dry-run", action="store_true", help="Validate connection, schema, deck, and duplicates without adding.")
    args = parser.parse_args()

    if args.allow_duplicate and args.block_duplicate:
        raise SystemExit("Use either --allow-duplicate or --block-duplicate, not both.")

    allow_duplicate = not args.block_duplicate
    cards = load_cards(args)

    try:
        version = invoke("version", url=args.connect_url)
        decks = invoke("deckNames", url=args.connect_url)
        deck, requested_deck = resolve_deck_name(args.deck, decks)

        models = invoke("modelNames", url=args.connect_url)
        if args.model not in models:
            raise AnkiConnectError(f"Note type not found: {args.model}")

        fields = invoke("modelFieldNames", {"modelName": args.model}, args.connect_url)
        for field in (args.front_field, args.back_field):
            if field not in fields:
                raise AnkiConnectError(f"Required field {field!r} not found in note type {args.model!r}")

        if args.dry_run:
            dry_results = []
            for card in cards:
                duplicates = find_duplicate(deck, card["front"], args.connect_url, args.front_field)
                dry_results.append({
                    "front": card["front"],
                    "duplicateNoteIds": duplicates,
                    "wouldAdd": allow_duplicate or not duplicates,
                })
            print(json.dumps({
                "status": "dry_run_ok",
                "ankiConnectVersion": version,
                "deck": deck,
                "requestedDeck": requested_deck,
                "model": args.model,
                "frontField": args.front_field,
                "backField": args.back_field,
                "cardCount": len(cards),
                "results": dry_results,
                "addedCount": 0,
                "synced": False,
            }, ensure_ascii=False, indent=2))
            return 0

        results = []
        for card in cards:
            try:
                results.append(add_one_card(card, args, deck, allow_duplicate))
            except AnkiConnectError as exc:
                results.append({
                    "status": "failed",
                    "front": card.get("front"),
                    "added": False,
                    "error": str(exc),
                })

        added_count = sum(1 for item in results if item.get("added"))
        failed_count = sum(1 for item in results if item.get("status") == "failed")
        skipped_duplicate_count = sum(1 for item in results if item.get("status") == "duplicate_skipped")
        unverified_count = sum(1 for item in results if item.get("status") == "added_unverified")

        sync_result = None
        sync_error = None
        should_sync = added_count > 0 and not args.no_sync
        if should_sync:
            try:
                sync_result = invoke("sync", url=args.connect_url)
            except AnkiConnectError as exc:
                sync_error = str(exc)

        if failed_count or skipped_duplicate_count or unverified_count:
            status = "partial_failure" if added_count else "failed"
        elif sync_error:
            status = "added_sync_failed"
        else:
            status = "completed"

        print(json.dumps({
            "status": status,
            "ankiConnectVersion": version,
            "deck": deck,
            "requestedDeck": requested_deck,
            "model": args.model,
            "frontField": args.front_field,
            "backField": args.back_field,
            "cardCount": len(cards),
            "addedCount": added_count,
            "failedCount": failed_count,
            "skippedDuplicateCount": skipped_duplicate_count,
            "unverifiedCount": unverified_count,
            "results": results,
            "synced": bool(should_sync and not sync_error),
            "syncResult": sync_result,
            "syncError": sync_error,
        }, ensure_ascii=False, indent=2))

        if status in {"completed", "added_sync_failed"}:
            return 0
        return 3

    except AnkiConnectError as exc:
        print(json.dumps({
            "status": "failed",
            "error": str(exc),
            "addedCount": 0,
            "failedCount": len(cards),
            "synced": False,
        }, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())
