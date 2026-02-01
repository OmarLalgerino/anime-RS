import feedparser
import csv
import requests
import re
import cloudscraper

# المصادر المحدثة لتشمل Nyaa و TokyoTosho مع البحث عن الترجمة العربية والجودات
SOURCES = [
    "https://nyaa.si/?page=rss&q=Arabic+1080p",
    "https://nyaa.si/?page=rss&q=Arabic+720p",
    "https://nyaa.si/?page=rss&q=Arabic+480p",
    "https://www.tokyotosho.info/rss.php?filter=1,11&z=Arabic" # رابط TokyoTosho للبحث عن الأنمي المترجم عربياً
]
DB_FILE = 'database.csv'

def get_clean_hash_link(entry):
    """استخراج الـ Hash وتحويله لرابط Webtor من أي مصدر"""
    # لمحرك Nyaa
    if hasattr(entry, 'nyaa_infohash'):
        return f"https://webtor.io/player/embed/{entry.nyaa_infohash}"
    
    # لمحرك TokyoTosho والروابط الأخرى (البحث عن الـ Hash داخل Magnet)
    link = getattr(entry, 'link', '')
    hash_match = re.search(r'btih:([a-fA-F0-9]{40})', link)
    if hash_match:
        return f"https://webtor.io/player/embed/{hash_match.group(1).lower()}"
    return None

def start_bot():
    database = {}
    scraper = cloudscraper.create_scraper()
    print("🎬 جاري جلب الأنمي المترجم بجميع الجودات من Nyaa و TokyoTosho...")

    for rss_url in SOURCES:
        try:
            # استخدام scraper لتجاوز حماية المواقع
            resp = scraper.get(rss_url, timeout=15)
            feed = feedparser.parse(resp.text)
            
            for entry in feed.entries[:40]:
                name_en = entry.title
                streaming_link = get_clean_hash_link(entry)
                
                if streaming_link:
                    # تصنيف الجودة بناءً على النص الموجود في العنوان
                    if "1080p" in name_en:
                        quality = "1080p (FHD) 💎"
                    elif "720p" in name_en:
                        quality = "720p (HD) ✅"
                    elif "480p" in name_en:
                        quality = "480p (SD) ⚡"
                    else:
                        quality = "جودة متنوعة"

                    # إضافة الحلقة للقائمة (يمنع التكرار باستخدام اسم الحلقة كمفتاح)
                    database[name_en] = {
                        'name_ar': name_en,
                        'name_en': name_en,
                        'torrent_url': streaming_link,
                        'status': quality
                    }
        except Exception as e:
            print(f"❌ خطأ في المصدر {rss_url}: {e}")

    # حفظ البيانات في ملف CSV
    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['name_ar', 'name_en', 'torrent_url', 'status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(database.values())
    
    print(f"✅ تم التحديث بنجاح! تم العثور على {len(database)} حلقة مترجمة.")

if __name__ == "__main__":
    start_bot()
