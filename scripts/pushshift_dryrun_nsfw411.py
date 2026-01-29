#!/usr/bin/env python3
"""
Dry-run Pushshift backfill for /r/nsfw411 - count unique subreddit mentions

Usage examples:
  .venv\Scripts\Activate.ps1
  python scripts\pushshift_dryrun_nsfw411.py --subreddit nsfw411 --max-comments 20000

The script will page Pushshift comments for the given subreddit and extract subreddit
mentions using the same regex used by the scanner. It will NOT write to the DB
when run (dry-run). It prints totals and the top-mentioned subreddits.
"""

import argparse
import time
import requests
import re
import sys
from collections import Counter

RE_SUB = re.compile(r"(?:/r/|\br/|https?://(?:www\.)?reddit\.com/r/)([A-Za-z0-9_]{3,21})")


def normalize(name: str) -> str:
    return name.lower().strip().lstrip('/').lstrip('r/').replace('\n', '')


def fetch_batch(subreddit: str, before: int = None, size: int = 500, timeout: int = 30):
    url = 'https://api.pushshift.io/reddit/comment/search'
    params = {'subreddit': subreddit, 'size': size, 'fields': 'body,created_utc,id'}
    if before:
        params['before'] = before
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    payload = r.json()
    return payload.get('data', [])


def run_dryrun(subreddit: str, max_comments: int = None, batch_size: int = 500, delay: float = 1.0):
    before = int(time.time())
    total_comments = 0
    unique_subs = set()
    counts = Counter()
    batches = 0

    print(f"Starting dry-run for /r/{subreddit} (batch_size={batch_size})")

    while True:
        batches += 1
        try:
            data = fetch_batch(subreddit, before=before, size=batch_size)
        except Exception as e:
            print(f"Error fetching batch: {e}")
            break

        if not data:
            print('No more data returned by Pushshift (exhausted).')
            break

        # Process batch
        min_created = None
        for c in data:
            total_comments += 1
            body = c.get('body') or ''
            # find mentions
            for m in RE_SUB.findall(body):
                nm = normalize(m)
                if 3 <= len(nm) <= 21 and nm not in ('all', 'random'):
                    unique_subs.add(nm)
                    counts[nm] += 1
            try:
                ts = int(c.get('created_utc') or 0)
                if not min_created or ts < min_created:
                    min_created = ts
            except Exception:
                pass

        print(f"Batch {batches}: fetched {len(data)} comments, total_comments={total_comments}, unique_subreddits={len(unique_subs)}")

        # Stop if max_comments reached
        if max_comments and total_comments >= max_comments:
            print(f"Reached max_comments={max_comments}, stopping.")
            break

        # Prepare next 'before' param to page older comments
        if min_created:
            before = min_created - 1
        else:
            # defensively stop to avoid infinite loop
            print('No valid created_utc in batch; stopping.')
            break

        # be polite
        time.sleep(delay)

    # Summary
    print('\nDry-run complete')
    print(f"Total comments processed: {total_comments}")
    print(f"Unique subreddits mentioned: {len(unique_subs)}")
    print('\nTop mentioned subreddits:')
    for name, cnt in counts.most_common(50):
        print(f"{name}\t{cnt}")

    return unique_subs, counts


def main():
    parser = argparse.ArgumentParser(description='Pushshift dry-run: count unique subreddit mentions from a subreddit')
    parser.add_argument('--subreddit', '-s', default='nsfw411', help='Source subreddit to scan (default: nsfw411)')
    parser.add_argument('--max-comments', '-m', type=int, default=None, help='Stop after this many comments (dry-run only)')
    parser.add_argument('--batch-size', '-b', type=int, default=500, help='Pushshift batch size (max 500)')
    parser.add_argument('--delay', '-d', type=float, default=1.0, help='Delay between Pushshift requests (seconds)')
    args = parser.parse_args()

    try:
        run_dryrun(args.subreddit, max_comments=args.max_comments, batch_size=args.batch_size, delay=args.delay)
    except KeyboardInterrupt:
        print('\nInterrupted by user')
        sys.exit(1)


if __name__ == '__main__':
    main()
