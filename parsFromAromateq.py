from app import Products,db , SQLAlchemy
from datetime import timedelta
from bs4 import BeautifulSoup
import requests
from datetime import datetime


def get_html(url):
    r=requests.get(url)
    #print(r.status_code, r.url)
    return r.text


def total_pages(html):
    soup= BeautifulSoup(html, 'html.parser')

    pages='https://aromateque.com.ua/perfums/nisparfum'
    # pagen=soup.find('ol')
    # print(pagen)
    return pages

def get_data(pages):
    # for i in pages:
    #     r=requests.get(i)
    time=datetime.now()

    r=requests.get(pages)
    #soup=BeautifulSoup(r.text,'lxml')
    soup= BeautifulSoup(r.text, 'html.parser')


    ads_block=soup.find( 'div', class_='product-grid category-products' ).find_all('div',class_='tile-box')
    for  ad in ads_block:
        brand= ad.find('span', class_='brand-name').text.strip()
        name=ad.find('div', class_='h2').text.strip() 
        price=ad.find('span', class_='price').text.strip()
        # price2=[]
        # for i in price:
        #     price2.append(i.isdigit)
        # print(price2)

        img=ad.find('div', class_='product-image').a.img['data-src'].strip()
        text=ad.find('span', class_='product-type').text.strip() 

        aromat='Древесный'
        Authors='deft'
        userId=1

        # items = Products(brand=brand, Authors=Authors, name=name, price=price,
        #             content=text, creationData=time,user_id=userId,
        #             img=img,aromat=aromat)
        # db.session.add(items)
        # db.session.commit()

        #print(text)
        #print(ref)
    # print(ads_block)
    # print(len(ads_block)




def main ():
    url='https://aromateque.com.ua/perfums/nisparfum'
    html= get_html(url)
    pages=total_pages(html)
    data=get_data(pages)




if __name__=='__main__':
    main()
