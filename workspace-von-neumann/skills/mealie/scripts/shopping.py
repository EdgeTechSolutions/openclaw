#!/usr/bin/env python3
"""
shopping.py — Mealie shopping list management
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error


def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def api_request(method, url, token, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=get_headers(token), method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        try:
            msg = json.loads(err).get("detail", err)
        except Exception:
            msg = err
        print(f"Error {e.code}: {msg}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def fmt_item(item):
    checked = "✅" if item.get("checked") else "⬜"
    note = item.get("note", "") or ""
    qty = item.get("quantity")
    unit = item.get("unit", {})
    unit_name = unit.get("name", "") if isinstance(unit, dict) else str(unit or "")
    food = item.get("food", {})
    food_name = food.get("name", "") if isinstance(food, dict) else str(food or "")
    display = item.get("display", "")
    item_id = item.get("id", "")

    if display:
        label = display
    else:
        parts = []
        if qty:
            parts.append(str(qty) if qty == int(qty) else f"{qty:.2f}")
        if unit_name:
            parts.append(unit_name)
        if food_name:
            parts.append(food_name)
        if note:
            parts.append(f"({note})")
        label = " ".join(parts) if parts else "unnamed item"

    return f"  {checked} {label}  [id: {item_id}]"


def cmd_lists(base_url, token, args):
    url = f"{base_url}/api/households/shopping/lists?perPage=-1"
    data = api_request("GET", url, token)
    items = data.get("items", data.get("data", []))
    if not items:
        print("No shopping lists found.")
        return
    print(f"Shopping Lists ({len(items)}):\n")
    for lst in items:
        name = lst.get("name", "Unnamed")
        lst_id = lst.get("id", "")
        item_count = len(lst.get("listItems", []))
        print(f"  🛒 {name}")
        print(f"     ID: {lst_id}")
        if item_count:
            print(f"     Items: {item_count}")
        print()


def cmd_get(base_url, token, args):
    url = f"{base_url}/api/households/shopping/lists/{args.list_id}"
    data = api_request("GET", url, token)
    name = data.get("name", "Unnamed")
    items = data.get("listItems", [])

    print(f"🛒 {name} ({len(items)} items)\n")

    # Group by label
    labeled = {}
    unlabeled = []
    for item in items:
        label_obj = item.get("label")
        if label_obj and isinstance(label_obj, dict):
            label_name = label_obj.get("name", "Other")
        else:
            label_name = None

        if label_name:
            labeled.setdefault(label_name, []).append(item)
        else:
            unlabeled.append(item)

    # Print labeled groups
    for label_name, group_items in sorted(labeled.items()):
        print(f"  [{label_name}]")
        for item in group_items:
            print(fmt_item(item))
        print()

    # Print unlabeled
    if unlabeled:
        if labeled:
            print("  [Uncategorized]")
        for item in unlabeled:
            print(fmt_item(item))

    # Summary
    checked = sum(1 for i in items if i.get("checked"))
    unchecked = len(items) - checked
    print(f"\n  Total: {len(items)} | ✅ {checked} checked | ⬜ {unchecked} remaining")


def cmd_create_list(base_url, token, args):
    url = f"{base_url}/api/households/shopping/lists"
    payload = {"name": args.name}
    result = api_request("POST", url, token, data=payload)
    lst_id = result.get("id", "")
    name = result.get("name", args.name)
    print(f"✅ Shopping list '{name}' created! ID: {lst_id}")


def cmd_add(base_url, token, args):
    if not args.list_id:
        print("Error: --list-id required", file=sys.stderr)
        sys.exit(1)

    items_to_add = []

    # Handle --note (freeform)
    if args.note:
        items_to_add.append({"shoppingListId": args.list_id, "note": args.note, "quantity": 1})

    # Handle --item entries
    for item_str in (args.item or []):
        # Parse "qty unit note" format loosely
        parts = item_str.split(None, 2)
        item_payload = {"shoppingListId": args.list_id, "quantity": 1}
        if parts:
            try:
                item_payload["quantity"] = float(parts[0])
                if len(parts) > 1:
                    item_payload["note"] = " ".join(parts[1:])
            except ValueError:
                # Not a number, treat whole string as note
                item_payload["note"] = item_str
        items_to_add.append(item_payload)

    if not items_to_add:
        print("Error: provide --item or --note", file=sys.stderr)
        sys.exit(1)

    if len(items_to_add) == 1:
        url = f"{base_url}/api/households/shopping/items"
        result = api_request("POST", url, token, data=items_to_add[0])
        item_id = result.get("id", "")
        print(f"✅ Item added! ID: {item_id}")
    else:
        url = f"{base_url}/api/households/shopping/items/create-bulk"
        result = api_request("POST", url, token, data=items_to_add)
        print(f"✅ {len(items_to_add)} items added!")


def cmd_check(base_url, token, args):
    # First get current item state
    # We need to PUT the full item, so fetch it first
    # Workaround: we'll do a minimal PUT with checked flag
    checked_val = args.checked.lower() in ("true", "1", "yes")

    # Get the item details by listing the parent list — but we don't know the list.
    # Instead, do a targeted update with just the checked field.
    url = f"{base_url}/api/households/shopping/items/{args.item_id}"
    payload = {"checked": checked_val}
    api_request("PUT", url, token, data=payload)
    status = "✅ checked" if checked_val else "⬜ unchecked"
    print(f"Item {args.item_id} marked as {status}")


def cmd_remove(base_url, token, args):
    url = f"{base_url}/api/households/shopping/items/{args.item_id}"
    api_request("DELETE", url, token)
    print(f"✅ Item {args.item_id} removed.")


def cmd_clear_checked(base_url, token, args):
    # Get the list
    url = f"{base_url}/api/households/shopping/lists/{args.list_id}"
    data = api_request("GET", url, token)
    items = data.get("listItems", [])
    checked_items = [i for i in items if i.get("checked")]

    if not checked_items:
        print("No checked items to remove.")
        return

    print(f"Removing {len(checked_items)} checked items...")
    for item in checked_items:
        del_url = f"{base_url}/api/households/shopping/items/{item['id']}"
        api_request("DELETE", del_url, token)

    print(f"✅ Removed {len(checked_items)} checked items.")


def cmd_add_recipe(base_url, token, args):
    url = f"{base_url}/api/households/shopping/lists/{args.list_id}/recipe/{args.recipe_id}"
    api_request("POST", url, token, data={})
    print(f"✅ Recipe ingredients added to shopping list {args.list_id}!")


def main():
    parser = argparse.ArgumentParser(description="Mealie shopping list management")
    parser.add_argument("--url", default=os.environ.get("MEALIE_URL", "https://hrana.stopar.si"),
                        help="Mealie base URL")
    parser.add_argument("--token", default=os.environ.get("MEALIE_TOKEN", ""),
                        help="Mealie API token")
    sub = parser.add_subparsers(dest="command", required=True)

    # lists
    sub.add_parser("lists", help="List all shopping lists")

    # get
    p_get = sub.add_parser("get", help="Get a shopping list with items")
    p_get.add_argument("--list-id", required=True, dest="list_id")

    # create-list
    p_cl = sub.add_parser("create-list", help="Create a new shopping list")
    p_cl.add_argument("--name", required=True)

    # add
    p_add = sub.add_parser("add", help="Add item(s) to a list")
    p_add.add_argument("--list-id", required=True, dest="list_id")
    p_add.add_argument("--item", action="append", help="Item as 'qty unit note' (repeatable)")
    p_add.add_argument("--note", help="Freeform item note")

    # check
    p_check = sub.add_parser("check", help="Check/uncheck an item")
    p_check.add_argument("--item-id", required=True, dest="item_id")
    p_check.add_argument("--checked", required=True, help="true or false")

    # remove
    p_remove = sub.add_parser("remove", help="Remove an item")
    p_remove.add_argument("--item-id", required=True, dest="item_id")

    # clear-checked
    p_cc = sub.add_parser("clear-checked", help="Remove all checked items from a list")
    p_cc.add_argument("--list-id", required=True, dest="list_id")

    # add-recipe
    p_ar = sub.add_parser("add-recipe", help="Add recipe ingredients to a shopping list")
    p_ar.add_argument("--list-id", required=True, dest="list_id")
    p_ar.add_argument("--recipe-id", required=True, dest="recipe_id")

    args = parser.parse_args()

    if not args.token:
        print("Error: API token required. Set MEALIE_TOKEN env var or use --token.", file=sys.stderr)
        sys.exit(1)

    base_url = args.url.rstrip("/")

    dispatch = {
        "lists": cmd_lists,
        "get": cmd_get,
        "create-list": cmd_create_list,
        "add": cmd_add,
        "check": cmd_check,
        "remove": cmd_remove,
        "clear-checked": cmd_clear_checked,
        "add-recipe": cmd_add_recipe,
    }
    dispatch[args.command](base_url, args.token, args)


if __name__ == "__main__":
    main()
