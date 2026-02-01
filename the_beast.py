import feedparser
import csv
import os
import requests
import re
import cloudscraper  # لتخطي حماية المواقع في GitHub Actions
from typing import Dict

# المصادر
SOURCES = [
    "https://nyaa.si/?page=rss",
    "https://www.tokyotosho.info/rss.php"
]
DB_FILE = 'database.csv'

def get_webtor_link(url):
    """تحويل رابط التورنت إلى رابط مشاهدة مباشرة عبر Webtor"""
    # البحث عن الـ Info Hash (كود مكون من 40 حرف)
    hash_match = re.search(r'btih:([a-fA-F0-9]{40})', url)
    if hash_match:
        info_hash = hash_match.group(1).lower()
        return f"https://webtor.io/player/embed/{info_hash}"
    
    # إذا كان الرابط لا يحتوي على ماغنيت، نرجعه كما هو (أو يمكن تطويره لاحقاً)
    return url

def translate_to_arabic(text):
    """ترجمة عناوين الأنمي إلى العربية"""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q={requests.utils.quote(text)}"
        res = requests.get(url, timeout=5)
        return res.json()[0][0][0]
    except:
        return text

def start_bot():
    database = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    database[row['name_en']] = row
        except: pass

    # استخدام cloudscraper بدلاً من requests العادية لتفادي حظر GitHub
    scraper = cloudscraper.create_scraper()
    print("📡 جاري قنص الروابط وتحويلها لمشاهدة مباشرة...")

    for rss_url in SOURCES:
        try:
            resp = scraper.get(rss_url, timeout=15)
            feed = feedparser.parse(resp.text)
            
            for entry in feed.entries[:20]:
                name_en = entry.title
                original_link = entry.link
                
                if name_en not in database:
                    print(f"🆕 معالجة: {name_en}")
                    
                    name_ar = translate_to_arabic(name_en)
                    # تحويل الرابط فوراً إلى رابط Embed
                    streaming_link = get_webtor_link(original_link)
                    
                    database[name_en] = {
                        'name_ar': name_ar,
                        'name_en': name_en,
                        'torrent_url': streaming_link, # الرابط المحول
                        'status': 'جاهز للمشاهدة 🍿'
                    }
        except Exception as e:
            print(f"❌ خطأ في المصدر: {e}")

    # حفظ النتائج
    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['name_ar', 'name_en', 'torrent_url', 'status']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(database.values())
    print(f"✨ تم التحديث! الملف جاهز الآن للمشاهدة المباشرة.")

if __name__ == "__main__":
    start_bot()
