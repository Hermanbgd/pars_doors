import requests
from bs4 import BeautifulSoup
import pandas
import json

list = []
domen = "https://продверь.рф/"


def define_category(link_of_category):
    if "v-dom" in link_of_category:
        return "В дом"
    elif "v-kvartiru" in link_of_category:
        return "В квартиру"
    elif "metall--panel" in link_of_category:
        return "Металл / панель"
    elif "s-zerkalom" in link_of_category:
        return "С зеркалом"
    elif "panel--panel" in link_of_category:
        return "Панель / панель"
    elif "termorazryv" in link_of_category:
        return "Терморазрыв"
    elif "metall--metall" in link_of_category:
        return "Металл / металл"
    elif "nestandartnye-dveri-vhod" in link_of_category:
        return "Нестандартные входные двери"
    elif "v-hoz-postroyku" in link_of_category:
        return "В хоз постройку"
    elif "ekoshpon" in link_of_category:
        return "Экошпон"
    elif "emal" in link_of_category:
        return "Эмаль"
    elif "pod-pokrasku" in link_of_category:
        return "Под покраску"
    elif "arki-mezhkomnatnye" in link_of_category:
        return "Арки межкомнатные"
    elif "nestandartnye-dveri" in link_of_category:
        return "Нестандартные межкомнатные двери"
    elif "emalit" in link_of_category:
        return "Эмалит"


def pars(my_list, domen):
    response = requests.get(domen + "catalog/")
    soup = BeautifulSoup(response.text, "lxml")
    links_to_catalog = [domen + x["href"] for x in soup.find_all("a", class_="categorys__item")]
    for link_catalog in links_to_catalog:
        if "vhodnye-dveri" in link_catalog:
            type = "Входная дверь"
        else:
            type = "Межкомнатная дверь"
        response = requests.get(link_catalog)
        if response.status_code == 200:
            soup_catalog = BeautifulSoup(response.text, "lxml")
            links_to_categories = [domen + x["href"] for x in soup_catalog.find_all('a', class_="catalog-podbor__cat-link")]
            for link_categories in links_to_categories:
                categoria = define_category(link_categories)
                page = 1
                count_cards = 0
                while True:
                    response = requests.get(f"{link_categories}?page={page}")
                    soup_categories = BeautifulSoup(response.text, "lxml")
                    pagination = soup_categories.find("div", class_="pagination__count")
                    product_cards = soup_categories.find_all("div", class_="product-list__item")
                    for product_card in product_cards:
                        my_dict = {}
                        name = product_card.find("h3", class_="product-list__title").text
                        my_dict["Название"] = name
                        my_dict["Тип"] = type
                        my_dict["Категория"] = categoria
                        product_item = product_card.find_all("div", class_="product-list__char-name")
                        product_value = product_card.find_all("div", class_="product-list__char-value")
                        for item, value in zip(product_item, product_value):
                            my_dict[item.text] = value.text
                        exist = product_card.find("div", class_="product-list__exist")
                        if exist == None:
                            my_dict["В наличии"] = "Под заказ"
                        else:
                            my_dict["В наличии"] = exist.text
                        price = product_card.find("p", class_="product-list__price").text
                        my_dict["Цена"] = price
                        photo = [x["data-image"] for x in product_card.find_all("div", class_="image-data")]
                        if photo != []:
                            my_dict["Ссылка на фото"] = [domen + x[1:] for x in photo]
                        else:
                            photo = product_card.find("img")["src"]
                            my_dict["Ссылка на фото"] = domen + photo[1:]
                        my_list.append(my_dict)
                    print(f"Спарсилась {page} страница по этой ссылке {link_categories}")
                    if pagination is None:
                        break
                    pagination = int(pagination.text.strip().split(" ")[1])
                    page += 1
                    count_cards += len(product_cards)
                    if count_cards == pagination:
                        break
    return my_list


def main():
    list_with_dicts = pars(list, domen)
    my_json = json.dumps(list_with_dicts, ensure_ascii=False)
    with open("my_json.json", "w", encoding="utf-8") as f:
        f.write(my_json)
    pandas.read_json("my_json.json").to_excel("output.xlsx")


if __name__ == main():
    main()
