import requests
import csv
import re
import cloudscraper
import os

# مصادر ذهبية متجددة لقنوات beIN و SSC
SOURCES = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ar.m3u",
    "https://raw.githubusercontent.com/skid96/M3U/main/Sport.m3u",
    "https://raw.githubusercontent.com/YassinEnnamli/iptv/master/sport.m3u",
    "https://raw.githubusercontent.com/Moebis/beIN-Sports-IPTV/master/beIN.m3u" # مصدر مخصص لـ beIN
]

# كلمات البحث لضمان عدم تفويت أي قناة رياضية عربية
SPORTS_KEYWORDS = ['beIN', 'SSC', 'KSA', 'رياضة', 'AD Sports', 'Alkass', 'بين سبورت']
DB_FILE = 'database.csv'

def check_link(url):
    """فحص سريع وصارم للرابط لضمان الجودة"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        # نستخدم GET مع timeout قصير جداً لسرعة الفحص
        with requests.get(url, timeout=4, stream=True, headers=headers) as r:
            return r.status_code == 200
    except:
        return False

def start_process():
    scraper = cloudscraper.create_scraper()
    final_list = []
    seen_urls = set()

    # 1. فحص وتطهير الجدول الحالي
    if os.path.exists(DB_FILE):
        print("🔍 جاري فحص الروابط المخزنة حالياً...")
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if check_link(row['url']):
                    final_list.append(row)
                    seen_urls.add(row['url'])

    # 2. الهجوم على المصادر الجديدة
    print("🚀 جاري سحب روابط beIN Sports الجديدة...")
    for source in SOURCES:
        try:
            response = scraper.get(source, timeout=10)
            # استخراج الاسم والرابط بدقة
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*?)\n', response.text)
            for name, url in matches:
                url = url.strip()
                name = name.strip()
                
                # شرط الإضافة: اسم رياضي، ليس توكن، ليس مكرر، وشغال
                if any(k.lower() in name.lower() for k in SPORTS_KEYWORDS):
                    if "token" not in url.lower() and url not in seen_urls:
                        if check_link(url):
                            final_list.append({'title': name, 'url': url})
                            seen_urls.add(url)
                            print(f"➕ مضافة الآن: {name}")
        except: continue

    # 3. ترتيب ذكي: beIN Sports تظهر في القمة دائماً
    # يتم الترتيب بحيث أي اسم يحتوي على beIN يرتفع للأعلى
    final_list.sort(key=lambda x: ("BEIN" in x['title'].upper()), reverse=True)

    # 4. حفظ النتيجة النهائية
    with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'url'])
        writer.writeheader()
        writer.writerows(final_list)
    
    print(f"✅ اكتمل التحديث! لديك الآن {len(final_list)} قناة رياضية جاهزة.")

if __name__ == "__main__":
    start_process()
