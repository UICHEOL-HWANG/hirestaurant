import sys
import os
import django
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
import pandas as pd 
from hirestaurant.models import Category,Restaurant

def main():
    # CSV 파일에서 데이터 불러오기
    data = pd.read_csv('hirestaurant/블루리본_최종.csv',encoding="utf-8")

    for index, row in data.iterrows():
        row = row.where(pd.notnull(row), '')

        # 카테고리 데이터 삽입 또는 검색
        category, created = Category.objects.get_or_create(name=row['category'])

        # 레스토랑 데이터 삽입
        restaurant = Restaurant.objects.create(
            restaurant_name=row['market_title'],
            number=row['number'],
            restaurant_image1=row['image'],
            address=row['address'],
            price_range=row['price_range'],
            latitude=row['latitude'],
            longitude=row['longitude']
        )
        restaurant.categories.add(category)

    print('Data successfully loaded into database')

if __name__ == '__main__':
    main()
