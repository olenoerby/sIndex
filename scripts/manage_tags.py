"""
Helper script for managing subreddit category tags.

Usage:
    # Auto-tag subreddits based on keywords
    python scripts/manage_tags.py --auto-tag
    
    # Auto-tag with limit (e.g., first 100 subreddits)
    python scripts/manage_tags.py --auto-tag --limit 100
    
    # Dry run (see what would be tagged without making changes)
    python scripts/manage_tags.py --auto-tag --dry-run
    
    # Tag a specific subreddit manually
    python scripts/manage_tags.py --tag-subreddit bbw --tags "BBW,Curvy"
    
    # Show tag statistics
    python scripts/manage_tags.py --stats
    
    # Remove all tags from a subreddit
    python scripts/manage_tags.py --remove-tags --subreddit bbw
    
    # Remove specific tags from a subreddit
    python scripts/manage_tags.py --remove-tags --subreddit bbw --tags "BBW"
"""

import os
import sys
import re
import argparse
from typing import List

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.models import Subreddit, Category, CategoryTag, SubredditCategoryTag

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://pineapple:pineapple@db:5432/pineapple")


def auto_tag_subreddit(session: Session, subreddit: Subreddit, dry_run: bool = False) -> List[str]:
    """Auto-tag a subreddit based on keyword matching."""
    tags = session.query(CategoryTag).filter(CategoryTag.active == True).all()
    
    search_text = " ".join([
        subreddit.name or "",
        subreddit.title or "",
        subreddit.description or "",
        subreddit.display_name or ""
    ]).lower()
    
    applied_tags = []
    
    for tag in tags:
        if not tag.keywords:
            continue
        
        keywords = [k.strip().lower() for k in tag.keywords.split(',')]
        
        for keyword in keywords:
            if not keyword:
                continue
            
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, search_text):
                confidence = min(95, 70 + len(keyword) * 2)
                
                existing = session.query(SubredditCategoryTag).filter(
                    SubredditCategoryTag.subreddit_id == subreddit.id,
                    SubredditCategoryTag.category_tag_id == tag.id
                ).first()
                
                if existing:
                    print(f"  ℹ️  Tag '{tag.name}' already applied")
                    break
                
                if not dry_run:
                    association = SubredditCategoryTag(
                        subreddit_id=subreddit.id,
                        category_tag_id=tag.id,
                        source='auto',
                        confidence=confidence
                    )
                    session.add(association)
                
                applied_tags.append(f"{tag.name} ({confidence}%)")
                print(f"  ✅ Tagged with '{tag.name}' (confidence: {confidence}%)")
                break
    
    return applied_tags


def auto_tag_all(session: Session, limit: int = None, dry_run: bool = False):
    """Auto-tag all untagged or partially tagged subreddits."""
    print("🏷️  Starting auto-tag process...\n")
    
    query = session.query(Subreddit).filter(
        Subreddit.subreddit_found == True,
        Subreddit.is_banned == False
    )
    
    if limit:
        query = query.limit(limit)
    
    subreddits = query.all()
    total = len(subreddits)
    tagged_count = 0
    
    mode = " (DRY RUN)" if dry_run else ""
    print(f"Processing {total} subreddits{mode}...\n")
    
    for i, subreddit in enumerate(subreddits, 1):
        print(f"[{i}/{total}] r/{subreddit.name}")
        
        tags = auto_tag_subreddit(session, subreddit, dry_run=dry_run)
        if tags:
            tagged_count += 1
            print(f"  Applied: {', '.join(tags)}")
        else:
            print(f"  No matching tags found")
        print()
    
    if not dry_run:
        session.commit()
        print(f"✅ Auto-tagging complete! Tagged {tagged_count}/{total} subreddits")
    else:
        print(f"✅ Dry run complete! Would tag {tagged_count}/{total} subreddits")


def tag_subreddit_manually(session: Session, subreddit_name: str, tag_names: List[str]):
    """Manually tag a subreddit with specific tags."""
    subreddit = session.query(Subreddit).filter(
        Subreddit.name == subreddit_name.lower()
    ).first()
    
    if not subreddit:
        print(f"❌ Subreddit '{subreddit_name}' not found")
        return
    
    print(f"Tagging r/{subreddit.name}...")
    
    for tag_name in tag_names:
        tag = session.query(CategoryTag).filter(
            func.lower(CategoryTag.name) == tag_name.lower()
        ).first()
        
        if not tag:
            print(f"  ⚠️  Tag '{tag_name}' not found")
            continue
        
        existing = session.query(SubredditCategoryTag).filter(
            SubredditCategoryTag.subreddit_id == subreddit.id,
            SubredditCategoryTag.category_tag_id == tag.id
        ).first()
        
        if existing:
            print(f"  ℹ️  Already tagged with '{tag.name}'")
            continue
        
        association = SubredditCategoryTag(
            subreddit_id=subreddit.id,
            category_tag_id=tag.id,
            source='manual',
            confidence=100
        )
        session.add(association)
        print(f"  ✅ Tagged with '{tag.name}'")
    
    session.commit()
    print(f"✅ Done!")


def remove_tags(session: Session, subreddit_name: str, tag_names: List[str] = None):
    """Remove tags from a subreddit."""
    subreddit = session.query(Subreddit).filter(
        Subreddit.name == subreddit_name.lower()
    ).first()
    
    if not subreddit:
        print(f"❌ Subreddit '{subreddit_name}' not found")
        return
    
    if tag_names:
        for tag_name in tag_names:
            tag = session.query(CategoryTag).filter(
                func.lower(CategoryTag.name) == tag_name.lower()
            ).first()
            
            if not tag:
                print(f"  ⚠️  Tag '{tag_name}' not found")
                continue
            
            deleted = session.query(SubredditCategoryTag).filter(
                SubredditCategoryTag.subreddit_id == subreddit.id,
                SubredditCategoryTag.category_tag_id == tag.id
            ).delete()
            
            if deleted:
                print(f"  ✅ Removed tag '{tag.name}'")
            else:
                print(f"  ℹ️  Tag '{tag.name}' was not applied")
    else:
        deleted = session.query(SubredditCategoryTag).filter(
            SubredditCategoryTag.subreddit_id == subreddit.id
        ).delete()
        print(f"  ✅ Removed {deleted} tags from r/{subreddit.name}")
    
    session.commit()


def show_statistics(session: Session):
    """Show tag usage statistics."""
    print("📊 Tag Statistics\n")
    
    total_categories = session.query(Category).count()
    total_tags = session.query(CategoryTag).count()
    total_tagged_subreddits = session.query(SubredditCategoryTag.subreddit_id).distinct().count()
    total_associations = session.query(SubredditCategoryTag).count()
    
    print(f"Categories: {total_categories}")
    print(f"Tags: {total_tags}")
    print(f"Tagged Subreddits: {total_tagged_subreddits}")
    print(f"Total Tag Associations: {total_associations}")
    print()
    
    print("🏆 Top 20 Most Used Tags:\n")
    top_tags = session.query(
        CategoryTag.name,
        Category.name.label('category_name'),
        func.count(SubredditCategoryTag.id).label('usage_count')
    ).join(
        SubredditCategoryTag,
        SubredditCategoryTag.category_tag_id == CategoryTag.id
    ).join(
        Category,
        Category.id == CategoryTag.category_id
    ).group_by(
        CategoryTag.id,
        CategoryTag.name,
        Category.name
    ).order_by(
        func.count(SubredditCategoryTag.id).desc()
    ).limit(20).all()
    
    for i, (tag_name, category_name, count) in enumerate(top_tags, 1):
        print(f"{i:2}. {tag_name:25} ({category_name:20}) - {count:4} subreddits")
    
    print()
    
    print("📌 Tags by Source:\n")
    by_source = session.query(
        SubredditCategoryTag.source,
        func.count(SubredditCategoryTag.id).label('count')
    ).group_by(
        SubredditCategoryTag.source
    ).all()
    
    for source, count in by_source:
        print(f"  {source or 'unknown':10} - {count:5} tags")
    
    print()
    
    untagged = session.query(Subreddit).filter(
        Subreddit.subreddit_found == True,
        Subreddit.is_banned == False,
        ~Subreddit.id.in_(
            session.query(SubredditCategoryTag.subreddit_id).distinct()
        )
    ).count()
    
    print(f"⚠️  Untagged Subreddits: {untagged}")


def main():
    parser = argparse.ArgumentParser(description='Manage subreddit category tags')
    parser.add_argument('--auto-tag', action='store_true', help='Auto-tag subreddits based on keywords')
    parser.add_argument('--tag-subreddit', type=str, help='Subreddit name to tag')
    parser.add_argument('--tags', type=str, help='Comma-separated list of tag names')
    parser.add_argument('--remove-tags', action='store_true', help='Remove tags from a subreddit')
    parser.add_argument('--subreddit', type=str, help='Subreddit name for remove operation')
    parser.add_argument('--stats', action='store_true', help='Show tag statistics')
    parser.add_argument('--limit', type=int, help='Limit number of subreddits to process')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no changes)')
    
    args = parser.parse_args()
    
    engine = create_engine(DATABASE_URL, echo=False)
    
    with Session(engine) as session:
        if args.stats:
            show_statistics(session)
        
        elif args.auto_tag:
            auto_tag_all(session, limit=args.limit, dry_run=args.dry_run)
        
        elif args.tag_subreddit and args.tags:
            tag_names = [t.strip() for t in args.tags.split(',')]
            tag_subreddit_manually(session, args.tag_subreddit, tag_names)
        
        elif args.remove_tags and (args.tag_subreddit or args.subreddit):
            subreddit_name = args.tag_subreddit or args.subreddit
            tag_names = [t.strip() for t in args.tags.split(',')] if args.tags else None
            remove_tags(session, subreddit_name, tag_names)
        
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
