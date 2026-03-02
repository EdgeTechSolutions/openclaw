#!/usr/bin/env python3
"""
mealplan.py — Mealie meal plan management
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import date


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


MEAL_ICONS = {
    "breakfast": "🌅",
    "lunch": "🌞",
    "dinner": "🌙",
    "side": "🥗",
}


def fmt_entry(entry):
    entry_type = entry.get("entryType", "dinner").lower()
    icon = MEAL_ICONS.get(entry_type, "🍽️")
    recipe = entry.get("recipe")
    title = entry.get("title", "")
    text = entry.get("text", "")
    plan_id = entry.get("id", "")
    entry_date = entry.get("date", "")

    if recipe:
        name = recipe.get("name", "Unnamed")
        slug = recipe.get("slug", "")
        line = f"  {icon} [{entry_type.capitalize()}] {name}"
        if slug:
            line += f" (slug: {slug})"
    elif title:
        line = f"  {icon} [{entry_type.capitalize()}] {title}"
        if text:
            line += f"\n     📝 {text}"
    else:
        line = f"  {icon} [{entry_type.capitalize()}] (no details)"

    line += f"  [plan-id: {plan_id}]"
    return line


def cmd_today(base_url, token, args):
    url = f"{base_url}/api/households/mealplans/today"
    data = api_request("GET", url, token)

    today_str = str(date.today())
    print(f"📅 Today's Meal Plan ({today_str})\n")

    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        entries = data.get("data", data.get("items", [data] if data else []))
    else:
        entries = []

    if not entries:
        print("  No meals planned for today.")
        return

    for entry in entries:
        print(fmt_entry(entry))


def cmd_list(base_url, token, args):
    params = {}
    if args.start_date:
        params["start_date"] = args.start_date
    if args.end_date:
        params["end_date"] = args.end_date
    qs = urllib.parse.urlencode(params)
    url = f"{base_url}/api/households/mealplans?{qs}" if qs else f"{base_url}/api/households/mealplans"
    data = api_request("GET", url, token)

    entries = data.get("data", data.get("items", []))
    if not entries:
        print("No meal plans found.")
        return

    # Group by date
    by_date = {}
    for entry in entries:
        d = entry.get("date", "Unknown")
        by_date.setdefault(d, []).append(entry)

    print(f"📅 Meal Plans ({len(entries)} entries)\n")
    for d in sorted(by_date.keys()):
        print(f"  {d}:")
        for entry in sorted(by_date[d], key=lambda e: e.get("entryType", "")):
            print(fmt_entry(entry))
        print()


def cmd_add(base_url, token, args):
    url = f"{base_url}/api/households/mealplans"

    entry_date = args.date or str(date.today())
    entry_type = args.entry_type or "dinner"

    payload = {
        "date": entry_date,
        "entryType": entry_type,
    }

    if args.recipe_slug:
        # Need to look up the recipe ID from slug
        recipe_url = f"{base_url}/api/recipes/{urllib.parse.quote(args.recipe_slug, safe='')}"
        recipe = api_request("GET", recipe_url, args.token if hasattr(args, 'token') else "")
        recipe_id = recipe.get("id")
        if not recipe_id:
            print(f"Error: could not find recipe with slug '{args.recipe_slug}'", file=sys.stderr)
            sys.exit(1)
        payload["recipeId"] = recipe_id
    elif args.title:
        payload["title"] = args.title
        if args.text:
            payload["text"] = args.text
    else:
        print("Error: provide --recipe-slug or --title", file=sys.stderr)
        sys.exit(1)

    result = api_request("POST", url, token, data=payload)
    plan_id = result.get("id", "")
    print(f"✅ Meal plan entry added for {entry_date} ({entry_type})! ID: {plan_id}")


def cmd_delete(base_url, token, args):
    url = f"{base_url}/api/households/mealplans/{args.plan_id}"
    api_request("DELETE", url, token)
    print(f"✅ Meal plan entry {args.plan_id} deleted.")


def cmd_random(base_url, token, args):
    url = f"{base_url}/api/households/mealplans/random"
    entry_date = args.date or str(date.today())
    entry_type = args.entry_type or "dinner"
    payload = {
        "date": entry_date,
        "entryType": entry_type,
    }
    result = api_request("POST", url, token, data=payload)
    icon = MEAL_ICONS.get(entry_type.lower(), "🍽️")
    recipe = result.get("recipe")
    if recipe:
        name = recipe.get("name", "Unnamed")
        slug = recipe.get("slug", "")
        print(f"{icon} Random suggestion for {entry_date} ({entry_type}): {name} (slug: {slug})")
    else:
        print(f"Result: {json.dumps(result, indent=2)}")


def main():
    parser = argparse.ArgumentParser(description="Mealie meal plan management")
    parser.add_argument("--url", default=os.environ.get("MEALIE_URL", "https://hrana.stopar.si"),
                        help="Mealie base URL")
    parser.add_argument("--token", default=os.environ.get("MEALIE_TOKEN", ""),
                        help="Mealie API token")
    sub = parser.add_subparsers(dest="command", required=True)

    # today
    sub.add_parser("today", help="Show today's meal plan")

    # list
    p_list = sub.add_parser("list", help="List meal plans in a date range")
    p_list.add_argument("--start-date", dest="start_date", help="Start date YYYY-MM-DD")
    p_list.add_argument("--end-date", dest="end_date", help="End date YYYY-MM-DD")

    # add
    p_add = sub.add_parser("add", help="Add a meal plan entry")
    p_add.add_argument("--date", help="Date YYYY-MM-DD (default: today)")
    p_add.add_argument("--entry-type", dest="entry_type", default="dinner",
                       choices=["breakfast", "lunch", "dinner", "side"],
                       help="Meal type")
    p_add.add_argument("--recipe-slug", dest="recipe_slug", help="Recipe slug to add")
    p_add.add_argument("--title", help="Note title (if not a recipe)")
    p_add.add_argument("--text", help="Note text")

    # delete
    p_del = sub.add_parser("delete", help="Delete a meal plan entry")
    p_del.add_argument("--plan-id", required=True, dest="plan_id")

    # random
    p_rand = sub.add_parser("random", help="Get a random meal plan suggestion")
    p_rand.add_argument("--date", help="Date YYYY-MM-DD (default: today)")
    p_rand.add_argument("--entry-type", dest="entry_type", default="dinner",
                        choices=["breakfast", "lunch", "dinner", "side"],
                        help="Meal type")

    args = parser.parse_args()

    if not args.token:
        print("Error: API token required. Set MEALIE_TOKEN env var or use --token.", file=sys.stderr)
        sys.exit(1)

    base_url = args.url.rstrip("/")

    # Inject token into args for cmd_add to use
    args.token = args.token

    dispatch = {
        "today": cmd_today,
        "list": cmd_list,
        "add": cmd_add,
        "delete": cmd_delete,
        "random": cmd_random,
    }
    dispatch[args.command](base_url, args.token, args)


if __name__ == "__main__":
    main()
