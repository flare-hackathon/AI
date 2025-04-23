import os
import asyncio
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.db.models import Post
from app.db.session import AsyncSessionLocal

POSTS_DIR = os.path.join(os.path.dirname(__file__), "..", "posts")
author_addresses = [
    "author_one@example.com",
    "author_two@example.com",
    "author_three@example.com",
    "author_four@example.com",
    "author_five@example.com",
    "author_six@example.com"
]

async def load_txt_posts():
    async with AsyncSessionLocal() as session:  # type: AsyncSession
        files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.txt')]
        posts_to_add = []

        for idx, filename in enumerate(files):
            filepath = os.path.join(POSTS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read().strip()
            if not content:
                print(f"Skipping empty file: {filename}")
                continue
            title = os.path.splitext(filename)[0]
            author = author_addresses[idx % len(author_addresses)]
            post = Post(title=title, content=content, published=True, authorAddress=author)
            posts_to_add.append(post)

        if posts_to_add:
            session.add_all(posts_to_add)
            await session.commit()
            print(f"Inserted {len(posts_to_add)} posts into the database.")
        else:
            print("No valid posts found to insert.")

if __name__ == "__main__":
    asyncio.run(load_txt_posts())
