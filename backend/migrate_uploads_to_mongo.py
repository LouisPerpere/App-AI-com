# migrate_uploads_to_mongo.py
import os, sys, mimetypes, asyncio, argparse
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

def guess_type(path: str) -> str | None:
    t, _ = mimetypes.guess_type(path)
    return t

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mongo-uri", required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--uploads-dir", default="uploads")
    parser.add_argument("--owner-id", required=True, help="owner_id par défaut pour tous les fichiers migrés")
    parser.add_argument("--public-base", required=True, help="ex: https://api.claire-marcus.com/uploads")
    args = parser.parse_args()

    client = AsyncIOMotorClient(args.mongo_uri)
    db = client[args.db]
    coll = db.media

    if not os.path.isdir(args.uploads_dir):
        print(f"❌ Dossier non trouvé: {args.uploads_dir}")
        sys.exit(1)

    files = [f for f in os.listdir(args.uploads_dir) if os.path.isfile(os.path.join(args.uploads_dir, f))]
    inserted = 0; skipped = 0

    for filename in files:
        path = os.path.join(args.uploads_dir, filename)
        file_type = guess_type(path)
        if not file_type:
            skipped += 1
            continue

        # existe déjà ?
        exists = await coll.find_one({"filename": filename, "owner_id": args.owner_id, "deleted": {"$ne": True}})
        if exists:
            skipped += 1
            continue

        stat = os.stat(path)
        created_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        doc = {
            "owner_id": args.owner_id,
            "filename": filename,
            "file_type": file_type,
            "url": f"{args.public_base}/{filename}",
            "thumb_url": None,             # à générer plus tard si besoin
            "description": "",
            "deleted": False,
            "created_at": created_at
        }
        await coll.insert_one(doc)
        inserted += 1

    print(f"✅ Migration terminée. Ajoutés: {inserted}, ignorés: {skipped}")

if __name__ == "__main__":
    asyncio.run(main())