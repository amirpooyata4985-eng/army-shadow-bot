"""
ماژول مدیریت داده FAQ کانال — مستقل و بدون وابستگی به بقیه پروژه.
فقط این یک فایل را داخل ربات موجودت import کن.

نصب مورد نیاز:
    pip install requests

استفاده داخل ربات موجودت:
    import data_loader

    # یک‌بار موقع بالا آمدن ربات (یا هر چند دقیقه با یک تایمر/JobQueue)
    data_loader.refresh_data(
        github_url="https://raw.githubusercontent.com/USERNAME/REPO/main/data/videos.json",
        local_path="data/videos.json"
    )

    # داخل هندلر پیام متنی ربات
    results = data_loader.search(user_message_text)
    for item in results:
        # item["title"], item["review"], item["video_link"]
        ...
"""

import json
import logging
import requests

logger = logging.getLogger(__name__)

# حافظه موقت — دیتا در RAM نگه داشته می‌شود تا هر پیام، فایل دوباره خوانده نشود
_cached_data = []


def refresh_data(github_url: str = "", local_path: str = "data/videos.json") -> int:
    """
    دیتا را بارگذاری/بازخوانی می‌کند.
    اول از لینک خام (Raw) گیت‌هاب تلاش می‌کند؛ اگر ناموفق بود (اینترنت قطع،
    لینک اشتباه، فایل هنوز پوش نشده)، از فایل محلی می‌خواند.

    این تابع را می‌توانی هم موقع استارت ربات صدا بزنی، هم دوره‌ای
    (مثلاً هر ۱۰ دقیقه) تا آپدیت‌های گیت‌هاب بدون ری‌استارت ربات اعمال شوند.

    خروجی: تعداد رکوردهای بارگذاری‌شده.
    """
    global _cached_data

    if github_url:
        try:
            response = requests.get(github_url, timeout=10)
            response.raise_for_status()
            _cached_data = response.json()
            logger.info(f"[data_loader] از گیت‌هاب بارگذاری شد ({len(_cached_data)} رکورد).")
            return len(_cached_data)
        except Exception as e:
            logger.warning(f"[data_loader] خواندن از گیت‌هاب ناموفق بود: {e} — استفاده از فایل محلی.")

    try:
        with open(local_path, "r", encoding="utf-8") as f:
            _cached_data = json.load(f)
        logger.info(f"[data_loader] از فایل محلی بارگذاری شد ({len(_cached_data)} رکورد).")
    except Exception as e:
        logger.error(f"[data_loader] خواندن فایل محلی هم ناموفق بود: {e}")
        _cached_data = []

    return len(_cached_data)


def get_all_entries() -> list:
    """کل دیتای فعلی در حافظه — برای ساخت لیست/منو در ربات مفید است."""
    return _cached_data


def search(query: str, max_results: int = 5) -> list:
    """
    جستجو در کلیدواژه‌ها و عنوان هر رکورد.
    غیرحساس به بزرگی/کوچکی حروف، بر اساس زیررشته (substring).

    مثال: search("نولان") یا search("Tenet") یا search("زمان")
    """
    query_normalized = query.strip().lower()
    if not query_normalized:
        return []

    matches = []
    for entry in _cached_data:
        keywords = [k.lower() for k in entry.get("keywords", [])]
        title = entry.get("title", "").lower()

        is_match = (
            any(query_normalized in kw or kw in query_normalized for kw in keywords)
            or query_normalized in title
        )

        if is_match:
            matches.append(entry)
        if len(matches) >= max_results:
            break

    return matches
