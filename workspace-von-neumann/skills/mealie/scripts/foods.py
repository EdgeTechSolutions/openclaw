#!/usr/bin/env python3
"""
foods.py — Mealie food/ingredient database management
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


def cmd_list(base_url, token, args):
    params = {
        "page": 1,
        "perPage": args.limit if args.limit else 50,
    }
    if args.search:
        params["search"] = args.search
    qs = urllib.parse.urlencode(params)
    url = f"{base_url}/api/foods?{qs}"
    data = api_request("GET", url, token)

    items = data.get("items", data.get("data", []))
    total = data.get("total", len(items))

    print(f"Foods ({total} total, showing {len(items)})\n")
    if not items:
        print("No foods found.")
        return

    for food in items:
        food_id = food.get("id", "")
        name = food.get("name", "Unnamed")
        aliases = food.get("aliases", [])
        alias_str = ""
        if aliases:
            alias_names = [a.get("name", "") for a in aliases if isinstance(a, dict)]
            if alias_names:
                alias_str = f"  (aliases: {', '.join(alias_names)})"
        print(f"  🥬 {name}{alias_str}  [id: {food_id}]")


def cmd_create(base_url, token, args):
    url = f"{base_url}/api/foods"
    payload = {"name": args.name}
    result = api_request("POST", url, token, data=payload)
    food_id = result.get("id", "")
    name = result.get("name", args.name)
    print(f"✅ Food '{name}' created! ID: {food_id}")


def cmd_delete(base_url, token, args):
    url = f"{base_url}/api/foods/{args.food_id}"
    confirm = input(f"Delete food '{args.food_id}'? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return
    api_request("DELETE", url, token)
    print(f"✅ Food {args.food_id} deleted.")


def main():
    parser = argparse.ArgumentParser(description="Mealie food/ingredient database management")
    parser.add_argument("--url", default=os.environ.get("MEALIE_URL", "https://hrana.stopar.si"),
                        help="Mealie base URL")
    parser.add_argument("--token", default=os.environ.get("MEALIE_TOKEN", ""),
                        help="Mealie API token")
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="List foods")
    p_list.add_argument("--search", help="Search query")
    p_list.add_argument("--limit", type=int, default=50, help="Max results (default 50)")

    # create
    p_create = sub.add_parser("create", help="Create a food")
    p_create.add_argument("--name", required=True, help="Food name")

    # delete
    p_del = sub.add_parser("delete", help="Delete a food")
    p_del.add_argument("--food-id", required=True, dest="food_id", help="Food ID")

    args = parser.parse_args()

    if not args.token:
        print("Error: API token required. Set MEALIE_TOKEN env var or use --token.", file=sys.stderr)
        sys.exit(1)

    base_url = args.url.rstrip("/")

    dispatch = {
        "list": cmd_list,
        "create": cmd_create,
        "delete": cmd_delete,
    }
    dispatch[args.command](base_url, args.token, args)


if __name__ == "__main__":
    main()
