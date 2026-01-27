#!/usr/bin/env python3
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://pineapple:pineapple@db:5432/pineapple')

engine = create_engine(DATABASE_URL, future=True)

def add_columns():
    with engine.connect() as conn:
        # Add retry_priority and next_retry_at if not present
        try:
            conn.execute(text("ALTER TABLE subreddits ADD COLUMN IF NOT EXISTS retry_priority integer NOT NULL DEFAULT 0"))
            conn.execute(text("ALTER TABLE subreddits ADD COLUMN IF NOT EXISTS next_retry_at timestamp NULL"))
            conn.commit()
            print('Columns ensured')
        except Exception as e:
            print('Failed to add columns:', e)

if __name__ == '__main__':
    add_columns()
