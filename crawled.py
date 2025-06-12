import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

ZENROWS_API_KEY = "c212416c094144231ff8ce9daf751d0f5e07c045"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_listing_links(page_url):
    api_url = "https://api.zenrows.com/v1/"
    params = {
        "url": page_url,
        "apikey": ZENROWS_API_KEY,
        "js_render": "true"
    }

    response = requests.get(api_url, params=params, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "/ban-nha-rieng" in href and "-pr" in href:
            full_url = "https://batdongsan.com.vn" + href.split("?")[0]
            links.append(full_url)

    return list(set(links))

def get_text_by_label(soup, label):
    el = soup.find("div", string=label)
    return el.find_next_sibling("div").get_text(strip=True) if el and el.find_next_sibling("div") else ""

def fetch_property_data(detail_url):
    api_url = "https://api.zenrows.com/v1/"
    params = {
        "url": detail_url,
        "apikey": ZENROWS_API_KEY,
        "js_render": "true"
    }

    response = requests.get(api_url, params=params, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    data = {
        "url": detail_url,
        "price": "",
        "area_m2": "",
        "bedrooms": "",
        "bathrooms": "",
        "floors": "",
        "access_road_width_m": "",
        "frontage": "",
        "legal_status": "",
        "furniture_state": "",
        "address": "",
    }

    # ✅ Lấy địa chỉ
    address_tag = soup.find("span", class_="re__pr-short-description js__pr-address")
    if address_tag:
        data["address"] = address_tag.get_text(strip=True)

    # ✅ Lấy các thông tin trong mục specs
    specs_items = soup.find_all("div", class_="re__pr-specs-content-item")
    for item in specs_items:
        title = item.find("span", class_="re__pr-specs-content-item-title")
        value = item.find("span", class_="re__pr-specs-content-item-value")
        if not title or not value:
            continue

        label = title.get_text(strip=True)
        val = value.get_text(strip=True)

        if label == "Mức giá":
            data["price"] = val
        elif label == "Diện tích":
            data["area_m2"] = val
        elif "phòng ngủ" in label:
            data["bedrooms"] = val
        elif "phòng tắm" in label:
            data["bathrooms"] = val
        elif "tầng" in label:
            data["floors"] = val
        elif "Đường vào" in label:
            data["access_road_width_m"] = val
        elif "Mặt tiền" in label:
            data["frontage"] = val
        elif "Pháp lý" in label:
            data["legal_status"] = val
        elif "Nội thất" in label:
            data["furniture_state"] = val

    return data

if __name__ == "__main__":
    all_results = []

    for page_num in range(1, 100):  # có thể đổi số trang ở đây
        page_url = f"https://batdongsan.com.vn/ban-nha-rieng?page={page_num}"
        print(f"🔎 Trang {page_num}: {page_url}")

        detail_links = get_listing_links(page_url)
        print(f"🔗 {len(detail_links)} links tìm thấy")

        for url in detail_links:
            print(f"   🏠 Crawl: {url}")
            try:
                data = fetch_property_data(url)
                all_results.append(data)
            except Exception as e:
                print(f"❌ Lỗi: {e}")
            time.sleep(1)

    # ✅ Ghi dữ liệu ra CSV
    df = pd.DataFrame(all_results)
    df.to_csv("output.csv", index=False, encoding="utf-8-sig")
    print("✅ Dữ liệu đã được lưu vào 'output.csv'")
