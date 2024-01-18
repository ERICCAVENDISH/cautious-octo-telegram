
from pytesseract import pytesseract
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import requests
from bs4 import BeautifulSoup
import time
from PIL import Image
import cv2
# 设置Chrome浏览器选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式运行，即不弹出浏览器窗口
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 创建Selenium的Chrome驱动
driver = webdriver.Chrome(options=chrome_options)


# 在fetch_food_images_with_selenium函数中修改搜索关键词
def fetch_food_images_with_selenium(food):
    # 构建搜索URL
    search_query = food + " 食材"  # 将食物名称与"食材"关键词结合
    url = f'https://pixabay.com/zh/images/search/{search_query}'

    driver.get(url)
    # 等待页面加载完成
    time.sleep(2)

    # 获取页面内容
    page_source = driver.page_source
    return page_source


def fetch_food_images(food):
    page_source = fetch_food_images_with_selenium(food)
    soup = BeautifulSoup(page_source, 'html.parser')

    # 查找所有带有srcset属性的img标签
    img_links = [img['src'] if img['src'].startswith('http') else 'https://' + img['src'][2:] for img in soup.find_all('img', attrs={'srcset': True})]

    # 限制最多爬取七张照片
    img_links = img_links[:7]

    return img_links


# 继续下面的部分保持不变
# 继续下面的部分保持不变

# 从文件中读取食物列表
with open('foods.txt', 'r', encoding='utf-8') as file:
    foods = file.read().splitlines()

# 创建一个文件夹用于保存图片
os.makedirs('food_images', exist_ok=True)

# 循环爬取图片链接并下载
for food in foods:
    image_links = fetch_food_images(food)

    if len(image_links) > 0:
        # 下载并保存每种食物的图片
        os.makedirs(f'food_images/{food}', exist_ok=True)
        for idx, link in enumerate(image_links):
            response = requests.get(link)
            if response.status_code == 200:
                with open(f'food_images/{food}/image{idx + 1}.jpg', 'wb') as f:
                    f.write(response.content)
                    print(f"Saved image{idx + 1}.jpg for {food}")

                    image_path = f'food_images/{food}/image{idx + 1}.jpg'
                    try:
                        # 打开图片文件
                        image = Image.open(image_path)

                        # 使用 OCR 检测图片中的文本
                        text = pytesseract.image_to_string(image)

                        # 检测到的文本为空，则说明图片中没有文字
                        if not text:
                            # 保存原始图片
                            image.save(f'food_images/{food}/image{idx + 1}.jpg')
                            print(f"Saved original image{idx + 1}.jpg for {food}")
                        else:
                            # 删除原始图片
                            os.remove(image_path)
                            print(f"Deleted original image{idx + 1}.jpg for {food} due to text detection")

                    except Exception as e:
                        print(f"Failed to process image{idx + 1} for {food}: {str(e)}")
            else:
                print(f"Failed to download image{idx + 1} for {food}. Status code: {response.status_code}")
    else:
        print(f"No image found for {food}")

# 关闭浏览器
driver.quit()
print("图片下载、转换和原始照片删除完成")