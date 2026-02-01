import requests
import re
import csv
import cloudscraper

# مصادر قنوات رياضية عامة وموثوقة
SOURCES = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ar.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/s.m3u",
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u"
]

# كلمات البحث عن الرياضة
SPORTS_KEYWORDS = ['sport', 'beIN', 'SSC', 'KSA', 'Stadium', 'Abu Dhabi', 'رياضة', 'كرة']

def is_token_link(url):
    """فحص الرابط: إذا كان يحتوي على رموز طويلة أو صيغة اشتراك يرفضه"""
    # استبعاد الروابط التي تحتوي على كلمات تدل على توكن أو اشتراك
    token_patterns = ['token=', 'key=', 'auth', 'pass', 'user', 'session']
    if any(pattern in url.lower() for pattern in token_patterns):
        return True
    
    # استبعاد الروابط التي تحتوي على سلاسل نصية طويلة جداً (عشوائية)
    path_segments = url.split('/')
    for segment in path_segments:
        if len(segment) > 20: # الرموز العشوائية عادة تكون طويلة جداً
            return True
    return False

def check_link(url):
    """تأكد أن الرابط عام ويعمل بدون حماية"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        with requests.get(url, timeout=5, stream=True, headers=headers) as r:
            if r.status_code == 200:
                return True
        return False
    except:
        return False

def start_process():
    scraper = cloudscraper.create_scraper()
    valid_sports = []
    seen_urls = set()

    print("🚀 جاري البحث في الـ Sports Zone عن الروابط المباشرة فقط...")

    for source in SOURCES:
        try:
            response = scraper.get(source, timeout=15)
            # نمط يبحث عن الاسم والرابط
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*?)\n', response.text)

            for name, url in matches:
                url = url.strip()
                name = name.strip()

                # الشروط: 
                # 1. اسم رياضي 
                # 2. ليس توكن 
                # 3. لم يتكرر
                if any(key.lower() in name.lower() for key in SPORTS_KEYWORDS):
                    if not is_token_link(url) and url not in seen_urls:
                        
                        if len(valid_sports) < 50:
                            if check_link(url):
                                valid_sports.append({
                                    'title': name,
                                    'url': url
                                })
                                seen_urls.add(url)
                                print(f"✅ تم إضافة: {name}")
        except:
            continue

    # حفظ النتائج
    with open('database.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'url'])
        writer.writerows(valid_sports)
    
    print(f"🏁 تم التحديث! تم العثور على {len(valid_sports)} قناة رياضية عامة.")

if __name__ == "__main__":
    start_process()
