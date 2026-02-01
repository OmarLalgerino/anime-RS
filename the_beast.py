import requests
import re
import csv
import os

# مصادر البحث (مستودعات تحدث روابطها باستمرار)
SOURCES = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ar.m3u",
    "https://raw.githubusercontent.com/mohammadreza-ertesh/TV-Channels/main/Arabic.m3u"
]

def check_link(url):
    """يختبر الرابط بسرعة قبل إضافته"""
    try:
        r = requests.head(url, timeout=3)
        return r.status_code == 200
    except:
        return False

def start_update():
    valid_channels = []
    print("جاري جلب الروابط من GitHub...")
    
    for source in SOURCES:
        try:
            response = requests.get(source)
            # استخراج الاسم والرابط
            matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*?\.m3u8)', response.text)
            
            for name, url in matches:
                url = url.strip()
                # فحص أول 30 قناة لضمان السرعة وعدم فشل البوت
                if len(valid_channels) < 30:
                    if check_link(url):
                        valid_channels.append({
                            'id': len(valid_channels) + 1,
                            'title': name.strip(),
                            'image': 'https://via.placeholder.com/150?text=TV',
                            'url': url
                        })
                        print(f"✅ تم إضافة: {name.strip()}")
        except:
            continue

    # حفظ النتائج في الجدول
    with open('database.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'title', 'image', 'url'])
        writer.writeheader()
        writer.writerows(valid_channels)

if __name__ == "__main__":
    start_update()
