import cloudscraper
from bs4 import BeautifulSoup
import csv
import os
import time

# --- الإعدادات ---
BASE_URL = "https://mycima.rip"
DB_FILE = "database.csv"
# استخدام cloudscraper لتجاوز حماية الموقع
scraper = cloudscraper.create_scraper()

def check_link(url):
    """التأكد من أن الرابط لا يزال يعمل"""
    try:
        response = scraper.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_movie_sources(movie_url):
    """الدخول لصفحة الفيلم واستخراج روابط التحميل المباشرة"""
    links = {"1080": "", "720": "", "480": ""}
    try:
        res = scraper.get(movie_url)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        # البحث عن أزرار التحميل (لأنها الأفضل للمشاهدة المباشرة)
        download_btns = soup.select('a.download-item, a[href*="download"]')
        
        for btn in download_btns:
            text = btn.text.lower()
            href = btn['href']
            
            if "1080" in text and not links["1080"]: links["1080"] = href
            elif "720" in text and not links["720"]: links["720"] = href
            elif "480" in text and not links["480"]: links["480"] = href
            
        return links
    except Exception as e:
        print(f"خطأ في استخراج الروابط: {e}")
        return links

def main():
    # 1. قراءة البيانات الموجودة مسبقاً
    existing_data = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_data[row['Name']] = row

    # 2. جلب الأفلام من الصفحة الرئيسية أو صفحات الجودة
    print("جاري فحص الموقع...")
    res = scraper.get(BASE_URL)
    soup = BeautifulSoup(res.content, 'html.parser')
    items = soup.select('.GridItem')
    
    updated_rows = []

    for item in items:
        name = item.find('strong').text.strip()
        movie_link = item.find('a')['href']
        
        # 3. منطق التحديث (الجديد والقديم)
        if name in existing_data:
            # إذا كان الفيلم موجوداً، نفحص إذا كان الرابط لا يزال يعمل
            old_row = existing_data[name]
            if check_link(old_row['URL_1080']):
                print(f"الرابط لا يزال صالحاً: {name}")
                updated_rows.append(old_row)
                continue
            else:
                print(f"الرابط معطل، جاري التحديث: {name}")

        # 4. جلب روابط جديدة (في حال كان جديداً أو قديماً معطلاً)
        print(f"جلب بيانات: {name}")
        sources = get_movie_sources(movie_link)
        updated_rows.append({
            "Name": name,
            "URL_1080": sources["1080"],
            "URL_720": sources["720"],
            "URL_480": sources["480"],
            "Status": "Active" if sources["1080"] else "Broken"
        })
        time.sleep(1) # تأخير بسيط لتجنب الحظر

    # 5. حفظ الجدول النهائي بتنسيق CSV
    keys = ["Name", "URL_1080", "URL_720", "URL_480", "Status"]
    with open(DB_FILE, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(updated_rows)
    print("تم تحديث قاعدة البيانات بنجاح!")

if __name__ == "__main__":
    main()
