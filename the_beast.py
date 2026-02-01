import requests
import re
import csv

def start_bot():
    # مصدر القنوات
    source_url = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ar.m3u"
    valid_channels = []
    
    try:
        response = requests.get(source_url, timeout=10)
        # استخراج الاسم والرابط
        matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*?\.m3u8)', response.text)
        
        for name, url in matches[:30]: # فحص أول 30 قناة فقط للسرعة
            valid_channels.append({
                'id': len(valid_channels) + 1,
                'title': name.strip(),
                'image': 'https://via.placeholder.com/150?text=TV',
                'url': url.strip()
            })
            
        # إنشاء ملف database.csv فوراً
        with open('database.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'image', 'url'])
            writer.writeheader()
            writer.writerows(valid_channels)
        print("✅ تم إنشاء الملف بنجاح")
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    start_bot()
