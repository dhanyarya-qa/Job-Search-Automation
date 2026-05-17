"""
Cleanup: Normalize existing job URLs and remove duplicates.

LinkedIn URLs with tracking params (position, pageNum, refId) caused
the same job to be stored multiple times. This script:
1. Normalizes all existing URLs (strips tracking params)
2. Keeps only the earliest record for each normalized URL
3. Removes duplicate records
"""
import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlparse, urlencode, parse_qs

sys.path.insert(0, str(Path(__file__).parent.parent))


def normalize_job_url(url: str) -> str:
    """Normalize job URL by removing tracking/session parameters."""
    if not url:
        return url
    
    url = url.strip()
    
    linkedin_strip_params = {
        'position', 'pageNum', 'refId', 'trackingId',
        'trk', 'lipi', 'lici', 'currentJobId', 'eBP',
        'recommendedFlavor', 'savedSearchId',
    }
    
    indeed_strip_params = {
        'fclid', 'from', 'utm_source', 'utm_medium',
        'utm_campaign', 'vjk', 'advn', 'sjdu',
    }
    
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ''
        
        if 'linkedin.com' in hostname:
            params_to_strip = linkedin_strip_params
        elif 'indeed.com' in hostname:
            params_to_strip = indeed_strip_params
        else:
            return url
        
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        cleaned_params = {
            k: v for k, v in query_params.items()
            if k not in params_to_strip
        }
        
        clean_query = urlencode(cleaned_params, doseq=True) if cleaned_params else ''
        cleaned_url = parsed._replace(query=clean_query, fragment='').geturl()
        
        return cleaned_url
    except Exception:
        return url


def main():
    db_path = Path(__file__).parent.parent / "job_hunting_ats.db"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    
    print("=" * 60)
    print("🧹 URL Cleanup & Deduplication")
    print("=" * 60)
    
    # Step 1: Get all jobs
    cur.execute("SELECT id, job_url, created_at FROM jobs ORDER BY created_at ASC")
    all_jobs = cur.fetchall()
    print(f"\n📊 Total jobs before cleanup: {len(all_jobs)}")
    
    # Step 2: Normalize URLs and find duplicates
    seen_urls = {}  # normalized_url -> (first_id, first_created_at)
    to_update = []  # (id, new_url) - jobs that need URL update
    to_delete = []  # ids to delete (duplicates)
    
    for job_id, job_url, created_at in all_jobs:
        normalized = normalize_job_url(job_url)
        
        if normalized in seen_urls:
            # This is a duplicate — mark for deletion
            to_delete.append(job_id)
        else:
            # First occurrence — keep it, update URL if needed
            seen_urls[normalized] = (job_id, created_at)
            if normalized != job_url:
                to_update.append((job_id, normalized))
    
    print(f"🔗 URLs to normalize: {len(to_update)}")
    print(f"🗑️  Duplicates to remove: {len(to_delete)}")
    print(f"✅ Unique jobs to keep: {len(seen_urls)}")
    
    if not to_update and not to_delete:
        print("\n✨ Database is already clean!")
        conn.close()
        return
    
    # Confirm
    print(f"\n⚠️  This will:")
    print(f"   - Update {len(to_update)} URLs (remove tracking params)")
    print(f"   - Delete {len(to_delete)} duplicate records")
    
    response = input("\nProceed? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled.")
        conn.close()
        return
    
    # Step 3: Update normalized URLs
    updated = 0
    for job_id, new_url in to_update:
        try:
            cur.execute("UPDATE jobs SET job_url = ? WHERE id = ?", (new_url, job_id))
            updated += 1
        except sqlite3.IntegrityError:
            # URL conflict with existing unique constraint — mark as duplicate instead
            to_delete.append(job_id)
    
    print(f"\n✅ Updated {updated} URLs")
    
    # Step 4: Delete duplicates
    if to_delete:
        # Also delete related records first (cascade manually for SQLite)
        for table in ['ai_analyses', 'applications', 'application_tracking']:
            try:
                placeholders = ','.join('?' * len(to_delete))
                cur.execute(f"DELETE FROM {table} WHERE job_id IN ({placeholders})", to_delete)
            except sqlite3.OperationalError:
                pass  # Table might not exist
        
        placeholders = ','.join('?' * len(to_delete))
        cur.execute(f"DELETE FROM jobs WHERE id IN ({placeholders})", to_delete)
        print(f"🗑️  Deleted {len(to_delete)} duplicate records")
    
    conn.commit()
    
    # Step 5: Verify
    cur.execute("SELECT COUNT(*) FROM jobs")
    final_count = cur.fetchone()[0]
    print(f"\n📊 Total jobs after cleanup: {final_count}")
    print(f"🎉 Removed {len(all_jobs) - final_count} duplicates!")
    
    # Check for remaining duplicates
    cur.execute("SELECT job_url, COUNT(*) FROM jobs GROUP BY job_url HAVING COUNT(*) > 1")
    remaining = cur.fetchall()
    if remaining:
        print(f"\n⚠️  {len(remaining)} duplicate URLs still remain (different platforms?)")
    else:
        print("✅ No duplicate URLs remaining!")
    
    conn.close()


if __name__ == "__main__":
    main()
