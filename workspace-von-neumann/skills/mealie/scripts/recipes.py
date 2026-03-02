#!/usr/bin/env python3
"""
recipes.py — Mealie recipe management
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


def fmt_recipe(r, verbose=False):
    lines = []
    name = r.get("name", "Untitled")
    slug = r.get("slug", "")
    desc = r.get("description", "")
    tags = [t.get("name", "") for t in r.get("tags", [])]
    categories = [c.get("name", "") for c in r.get("recipeCategory", [])]
    ingredients = r.get("recipeIngredient", [])
    rating = r.get("rating")

    lines.append(f"📖 {name}")
    if slug:
        lines.append(f"   Slug: {slug}")
    if desc:
        lines.append(f"   {desc[:200]}{'...' if len(desc) > 200 else ''}")
    if rating:
        stars = "⭐" * int(rating)
        lines.append(f"   Rating: {stars} ({rating})")
    if categories:
        lines.append(f"   Categories: {', '.join(categories)}")
    if tags:
        lines.append(f"   Tags: {', '.join(tags)}")
    if verbose and ingredients:
        lines.append(f"   Ingredients ({len(ingredients)}):")
        for ing in ingredients[:10]:
            qty = ing.get("quantity", "")
            unit = ing.get("unit", {})
            unit_name = unit.get("name", "") if isinstance(unit, dict) else str(unit or "")
            note = ing.get("note", "") or ing.get("display", "")
            food = ing.get("food", {})
            food_name = food.get("name", "") if isinstance(food, dict) else str(food or "")
            part = " ".join(filter(None, [str(qty) if qty else "", unit_name, food_name, note]))
            lines.append(f"     • {part.strip()}")
        if len(ingredients) > 10:
            lines.append(f"     ... and {len(ingredients) - 10} more")
    elif ingredients:
        lines.append(f"   Ingredients: {len(ingredients)} items")
    return "\n".join(lines)


def cmd_list(base_url, token, args):
    params = {
        "page": args.page,
        "perPage": args.limit,
    }
    if args.search:
        params["search"] = args.search
    if hasattr(args, "category") and args.category:
        params["queryFilter"] = f"recipeCategory.name={args.category}"
    if hasattr(args, "tag") and args.tag:
        params["queryFilter"] = f"tags.name={args.tag}"

    qs = urllib.parse.urlencode(params)
    url = f"{base_url}/api/recipes?{qs}"
    data = api_request("GET", url, token)

    items = data.get("items", data.get("data", []))
    total = data.get("total", len(items))
    page = data.get("page", args.page)
    total_pages = data.get("total_pages", 1)

    print(f"Recipes (page {page}/{total_pages}, total: {total})\n")
    if not items:
        print("No recipes found.")
        return
    for r in items:
        print(fmt_recipe(r))
        print()


def cmd_get(base_url, token, args):
    url = f"{base_url}/api/recipes/{urllib.parse.quote(args.slug, safe='')}"
    data = api_request("GET", url, token)
    print(fmt_recipe(data, verbose=True))

    # Show instructions summary
    instructions = data.get("recipeInstructions", [])
    if instructions:
        print(f"\n   Steps ({len(instructions)}):")
        for i, step in enumerate(instructions, 1):
            text = step.get("text", "")
            print(f"   {i}. {text[:120]}{'...' if len(text) > 120 else ''}")

    # Show nutrition if available
    nutrition = data.get("nutrition")
    if nutrition:
        kcal = nutrition.get("calories")
        if kcal:
            print(f"\n   Nutrition (per serving): {kcal} kcal")

    # Show source URL
    org_url = data.get("orgURL") or data.get("orgUrl")
    if org_url:
        print(f"\n   Source: {org_url}")


def cmd_create_url(base_url, token, args):
    url = f"{base_url}/api/recipes/create/url"
    payload = {"url": args.url_source}
    print(f"Importing recipe from {args.url_source} ...")
    result = api_request("POST", url, token, data=payload)
    # Returns the slug string or object
    if isinstance(result, str):
        print(f"✅ Recipe imported! Slug: {result}")
    elif isinstance(result, dict):
        slug = result.get("slug", result.get("id", ""))
        name = result.get("name", "")
        print(f"✅ Recipe imported! Name: {name}, Slug: {slug}")
    else:
        print(f"✅ Done: {result}")


def cmd_create(base_url, token, args):
    if args.file:
        with open(args.file, "r") as f:
            payload = json.load(f)
    else:
        payload = json.load(sys.stdin)

    url = f"{base_url}/api/recipes"
    result = api_request("POST", url, token, data=payload)
    if isinstance(result, str):
        print(f"✅ Recipe created! Slug: {result}")
    elif isinstance(result, dict):
        slug = result.get("slug", "")
        name = result.get("name", "")
        print(f"✅ Recipe created! Name: {name}, Slug: {slug}")
    else:
        print(f"✅ Done: {result}")


def cmd_delete(base_url, token, args):
    url = f"{base_url}/api/recipes/{urllib.parse.quote(args.slug, safe='')}"
    confirm = input(f"Delete recipe '{args.slug}'? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return
    api_request("DELETE", url, token)
    print(f"✅ Recipe '{args.slug}' deleted.")


def main():
    parser = argparse.ArgumentParser(description="Mealie recipe management")
    parser.add_argument("--url", default=os.environ.get("MEALIE_URL", "https://hrana.stopar.si"),
                        help="Mealie base URL")
    parser.add_argument("--token", default=os.environ.get("MEALIE_TOKEN", ""),
                        help="Mealie API token")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="List recipes")
    p_list.add_argument("--search", help="Search query")
    p_list.add_argument("--category", help="Filter by category name")
    p_list.add_argument("--tag", help="Filter by tag name")
    p_list.add_argument("--limit", type=int, default=20, help="Results per page")
    p_list.add_argument("--page", type=int, default=1, help="Page number")

    # get
    p_get = sub.add_parser("get", help="Get recipe by slug")
    p_get.add_argument("--slug", required=True, help="Recipe slug")

    # create-url
    p_curl = sub.add_parser("create-url", help="Import recipe from URL")
    p_curl.add_argument("--url-source", required=True, dest="url_source", help="Recipe source URL")

    # create
    p_create = sub.add_parser("create", help="Create recipe from JSON")
    p_create.add_argument("--file", help="JSON file path (else reads stdin)")

    # delete
    p_del = sub.add_parser("delete", help="Delete a recipe")
    p_del.add_argument("--slug", required=True, help="Recipe slug")

    args = parser.parse_args()

    if not args.token:
        print("Error: API token required. Set MEALIE_TOKEN env var or use --token.", file=sys.stderr)
        sys.exit(1)

    base_url = args.url.rstrip("/")

    if args.command == "list":
        cmd_list(base_url, args.token, args)
    elif args.command == "get":
        cmd_get(base_url, args.token, args)
    elif args.command == "create-url":
        cmd_create_url(base_url, args.token, args)
    elif args.command == "create":
        cmd_create(base_url, args.token, args)
    elif args.command == "delete":
        cmd_delete(base_url, args.token, args)


if __name__ == "__main__":
    main()
