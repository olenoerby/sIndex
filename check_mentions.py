import sys
import re
sys.path.insert(0, 'api')
from api.models import Comment, Mention
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://pineapple:pineapple@db:5432/pineapple')
Session = sessionmaker(bind=engine)
session = Session()

RE_SUB = re.compile(r"(?:/r/|\br/|https?://(?:www\.)?reddit\.com/r/)([A-Za-z0-9_]{3,21})")

try:
    # Check sample comments
    comments = session.query(Comment).limit(100).all()
    found_with_mentions = 0
    
    print("=== CHECKING COMMENTS FOR MENTIONS ===\n")
    
    for c in comments:
        body = c.body or ""
        matches = RE_SUB.findall(body)
        if matches:
            found_with_mentions += 1
            print(f"Comment {c.reddit_comment_id}:")
            print(f"  Mentions: {matches}")
            print(f"  Body: {body[:120]}...")
            print()
    
    print(f"\n=== SUMMARY ===")
    print(f"Checked {len(comments)} comments")
    print(f"Found mentions in {found_with_mentions} comments")
    
    # Check mentions table
    mention_count = session.query(Mention).count()
    print(f"Total mentions in database: {mention_count}")
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    session.close()
