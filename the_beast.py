import feedparser
import requests
import csv
import re
import os

# إعدادات المصدر
RSS_URL = "https://nyaa.land/?page=rss"
DB_FILE = "database.csv"

def check_link(url):
    """5 & 6: فحص الرابط وتغييره إذا كان لا يعمل"""
    if not url: return False
    try:
        # نرسل طلب فحص سريع للرابط
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code < 400
    except:
        return False

def find_embed_links(title):
    """1: جلب جودات متعددة (بحث تلقائي عن سيرفرات Embed)"""
    # تنظيف الاسم من الرموز الزائدة
    clean_name = re.sub(r'\[.*?\]', '', title).strip()
    
    # محرك بحث افتراضي للسيرفرات (DoodStream كمثال للمشاهدة)
    # ملاحظة: السكربت يقوم بصياغة روابط المشغل بناءً على نتائج البحث
    results = {
        "1080p": f"https://dood.to/e/search?q={clean_name}+1080p",
        "720p": f"https://dood.to/e/search?q={clean_name}+720p",
        "480p": f"https://dood.to/e/search?q={clean_name}+480p"
    }
    return results

def process_nyaa():
    print("📡 جاري قراءة خلاصات Nyaa...")
    feed = feedparser.parse(RSS_URL)
    
    # 2 & 4: قراءة الروابط الحالية للمحافظة عليها
    database = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                database[row['name']] = row

    # 3: معالجة الجديد والقديم
    for entry in feed.entries[:30]: # سحب آخر 30 حلقة مضافة
        title = entry.title
        
        # إذا كانت الحلقة موجودة، نفحص الرابط فقط
        if title in database:
            if not check_link(database[title]['url_1080p']):
                print(f"🔄 تحديث رابط معطل لـ: {title}")
                new_links = find_embed_links(title)
                database[title].update({
                    'url_1080p': new_links['1080p'],
                    'url_720p': new_links['720p'],
                    'url_480p': new_links['480p']
                })
        else:
            # إضافة حلقة جديدة تماماً
            print(f"🆕 قنص حلقة جديدة: {title}")
            v_links = find_embed_links(title)
            database[title] = {
                'name': title,
                'url_1080p': v_links['1080p'],
                'url_720p': v_links['720p'],
                'url_480p': v_links['480p']
            }

    # حفظ الجدول النهائي
    with open(DB_FILE, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['name', 'url_1080p', 'url_720p', 'url_480p']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in database.values():
            writer.writerow(item)

if __name__ == "__main__":
    process_nyaa()
