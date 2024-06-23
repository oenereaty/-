import requests
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import xmltodict
import folium
import webbrowser


def current_date_string():
    current_date = datetime.now().date()
    return current_date.strftime("%Y%m%d")


def current_hour_string():
    now = datetime.now()
    if now.minute < 45:  # base_time과 base_date 구하는 함수
        if now.hour == 0:
            base_time = "2330"
        else:
            pre_hour = now.hour - 1
            if pre_hour < 10:
                base_time = "0" + str(pre_hour) + "30"
            else:
                base_time = str(pre_hour) + "30"
    else:
        if now.hour < 10:
            base_time = "0" + str(now.hour) + "30"
        else:
            base_time = str(now.hour) + "30"
    return base_time


keys = ('tEiS+AVlR6OrR9JiCGmq34qCAQQDoZRQfgEP8Joa+yAtl28k8bEClfDkrlSGqLM33y5MoeybYSliSdANy5fAqA==')  # 유효한 서비스 키를 여기에 입력
url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst'
params = {'serviceKey': keys,
          'pageNo': '1',
          'numOfRows': '60',
          'dataType': 'XML',  # XML로 변경
          'base_date': current_date_string(),
          'base_time': current_hour_string(),
          'nx': '63',
          'ny': '89'}


def forecast():
    response = requests.get(url, params=params, verify=False)
    xml_data = response.content.decode('utf-8')
    dict_data = xmltodict.parse(xml_data)

    if 'response' in dict_data:
        if 'header' in dict_data['response'] and dict_data['response']['header']['resultCode'] != '00':
            print("Error: " + dict_data['response']['header']['resultMsg'])
            return {}
        elif 'cmmMsgHeader' in dict_data['response']:
            print("Error: " + dict_data['response']['cmmMsgHeader']['errMsg'])
            return {}

    weather_data = {'tmp': None, 'hum': None, 'sky': None, 'sky2': None}
    if 'response' in dict_data and 'body' in dict_data['response'] and 'items' in dict_data['response']['body']:
        for item in dict_data['response']['body']['items']['item']:
            if item['category'] == 'T1H':
                weather_data['tmp'] = item['fcstValue']
            if item['category'] == 'REH':
                weather_data['hum'] = item['fcstValue']
            if item['category'] == 'SKY':
                weather_data['sky'] = item['fcstValue']
            if item['category'] == 'PTY':
                weather_data['sky2'] = item['fcstValue']
    else:
        print("Expected keys not found in the response")

    return weather_data


def proc_weather():
    dict_sky = forecast()
    str_sky = "전주시"
    if dict_sky.get('sky') is not None or dict_sky.get('sky2') is not None:
        str_sky += "날씨: "
        if dict_sky.get('sky2') == '0':
            if dict_sky.get('sky') == '1':
                str_sky += "맑음"
            elif dict_sky.get('sky') == '3':
                str_sky += "구름 많음"
            elif dict_sky.get('sky') == '4':
                str_sky += "흐림"
        elif dict_sky.get('sky2') == '1':
            str_sky += "비"
        elif dict_sky.get('sky2') == '2':
            str_sky += "비와 눈"
        elif dict_sky.get('sky2') == '3':
            str_sky += "눈"
        elif dict_sky.get('sky2') == '5':
            str_sky += "빗방울이 떨어짐"
        elif dict_sky.get('sky2') == '6':
            str_sky += "빗방울과 눈이 날림"
        elif dict_sky.get('sky2') == '7':
            str_sky += "눈이 날림"
        str_sky += "\n"
    if dict_sky.get('tmp') is not None:
        str_sky += "온도: " + dict_sky.get('tmp') + 'ºC\n'
    if dict_sky.get('hum') is not None:
        str_sky += "습도: " + dict_sky.get('hum') + '%'

    return str_sky


def find_haksik_menu():
    URL = "https://coopjbnu.kr/menu/week_menu.php"
    response = requests.get(URL)
    response.encoding = "UTF-8"

    soup = BeautifulSoup(response.text, 'html.parser')
    menu_items = soup.select('td')

    week_jin = ["월", "화", "수", "목", "금"]
    week_hu = ["월", "화", "수", "목", "금"]

    menus = [item.get_text().strip() for item in menu_items]
    menus.remove("소시지오므라이스Sausage omelet")
    menus.remove("순살등심돈까스 / 치즈돈까스 / 치킨까스pork cutlet /Cheese pork cutlet\xa0/Chicken cutlet")

    for i in range(5):
        menus.insert(55 + i, "순살등심돈까스(pork cutlet) / 치즈돈까스(Cheese pork cutlet) / 치킨까스(Chicken cutlet)")

    jinsudang = dict(zip(week_jin, menus[:5]))

    husaengkwan = {}
    for i, day in enumerate(week_hu):
        husaengkwan[day] = {
            '찌개': menus[25 + i],
            '돌솥': menus[30 + i],
            '특식': menus[35 + i],
            '덮밥or비빔밥': menus[45 + i],
            '샐러드': menus[50 + i],
            '돈까스': menus[55 + i],
            '오므라이스': (menus[60 + i], "소시지오므라이스Sausage omelet")
        }

    return jinsudang, husaengkwan


def pretty(husaengkwan):
    menu_strings = []

    for day, menu in husaengkwan.items():
        menu_string = (
            f"  찌개: {menu['찌개']}\n"
            f"  돌솥: {menu['돌솥']}\n"
            f"  특식: {menu['특식']}\n"
            f"  덮밥/비빔밥: {menu['덮밥or비빔밥']}\n"
            f"  샐러드: {menu['샐러드']}\n"
            f"  돈까스: {menu['돈까스']}\n"
            f"  오므라이스: {menu['오므라이스'][0]}, {menu['오므라이스'][1]}\n")
        menu_strings.append(menu_string)

    return "\n".join(menu_strings)


def show_haksik_menu():
    now = datetime.now()
    yoil = datetime.today().strftime("%a")

    day_names = {
        "Mon": "월", "Tue": "화", "Wed": "수", "Thu": "목", "Fri": "금"}

    korean_yoil = day_names.get(yoil, "요일을 찾을 수 없음")

    jinsudang_dict, husaengkwan_dict = find_haksik_menu()

    if korean_yoil in jinsudang_dict:
        messagebox.showinfo("진수당 메뉴", f"\n{korean_yoil}요일의 진수당 메뉴:\n{jinsudang_dict[korean_yoil]}")
    else:
        messagebox.showinfo("진수당 메뉴", f"\n{korean_yoil}요일의 진수당 메뉴를 찾을 수 없습니다.")

    if korean_yoil in husaengkwan_dict:
        husaengkwan_menus = pretty({korean_yoil: husaengkwan_dict[korean_yoil]})
        messagebox.showinfo("후생관 메뉴", f"\n{korean_yoil}요일의 후생관 메뉴:\n{husaengkwan_menus}")
    else:
        messagebox.showinfo("후생관 메뉴", f"\n{korean_yoil}요일의 후생관 메뉴를 찾을 수 없습니다.")


def load_restaurants():
    filename = "restaurant.xlsx"
    df = pd.read_excel(filename)
    return df


def checkbox_click(food_preferences, food_type):
    food_preferences[food_type] = not food_preferences[food_type]



def next_step(food_preferences, root):
    selected_food_types = [food_type for food_type, selected in food_preferences.items() if selected]
    if not selected_food_types:
        messagebox.showwarning("선택 필요", "음식 취향을 선택해주세요.")
    else:
        selected_food_message = ", ".join(selected_food_types)
        confirm = messagebox.askquestion("선호 확인", f"{selected_food_message}을(를) 좋아하세요?")
        if confirm == 'yes':
            show_recommend(selected_food_types, root)


def show_recommend(selected_food_types, root):
    recommend_window = tk.Toplevel(root)
    recommend_window.title("가게 추천")
    df = load_restaurants()
    recommend_restaurants = df[df['foodtype'].isin(selected_food_types)]
    recommend_restaurants = recommend_restaurants.sample(5)
    recommend_count = 0
    show_next_recommend(recommend_window, recommend_restaurants, recommend_count)


def event_recommend(recommend_window, recommend_restaurants, recommend_count):
    restaurant = recommend_restaurants.iloc[recommend_count]
    if restaurant['sky2'] == 1:
        df_rain = restaurant['sky2'] == 1
        recommend_label = tk.Label(recommend_window,
                                   text=f"비 오니까 {df_rain['locationtype']} 쪽에 있는 {df_rain['restaurant']} 어떠세요?\n대표메뉴: {restaurant['menu']}",
                                   padx=20, pady=20, font=("Arial", 12))
        recommend_label.pack()


def show_next_recommend(recommend_window, recommend_restaurants, recommend_count):
    if recommend_count < 5:
        restaurant = recommend_restaurants.iloc[recommend_count]
        recommend_count += 1

        for widget in recommend_window.winfo_children():
            widget.destroy()

        recommend_label = tk.Label(recommend_window,
                                   text=f"{restaurant['locationtype']} 쪽에 있는 {restaurant['restaurant']} 어떠세요?\n대표메뉴: {restaurant['menu']}",
                                   padx=20, pady=20, font=("Arial", 12))
        recommend_label.pack()

        now = datetime.now().strftime("%Y-%m-%d %a %H:%M:%S")
        df = pd.read_excel("restaurant.xlsx")
        open = df['open']
        closed = df['closed']
        if open <= now <= closed:
            print("지금 영업 중이에요!")
        else:
            print("지금은 영업을 하지 않아요!")

        like_button = tk.Button(recommend_window, text="좋아!",
                                command=lambda: like_recommend(recommend_window, restaurant))
        like_button.pack(side=tk.LEFT, padx=30, pady=30)

        dislike_button = tk.Button(recommend_window, text="싫어!",
                                   command=lambda: dislike_recommend(recommend_window, recommend_restaurants,
                                                                     recommend_count))
        dislike_button.pack(side=tk.RIGHT, padx=30, pady=30)
    else:
        show_haksik_option(recommend_window)


def like_recommend(recommend_window, restaurant):
    latitude = restaurant["latitude"]
    longitude = restaurant["longitude"]
    m = folium.Map(location=[latitude, longitude], zoom_start=34)
    folium.Marker([latitude, longitude], popup=restaurant['restaurant']).add_to(m)
    map_path = 'map.html'
    m.save(map_path)

    webbrowser.open(map_path)

    messagebox.showinfo("드디어 고르셨군요", "맛있게 드세요!")
    recommend_window.destroy()


def dislike_recommend(recommend_window, recommend_restaurants, recommend_count):
    if recommend_count < 5:
        show_next_recommend(recommend_window, recommend_restaurants, recommend_count)
    else:
        show_haksik_option(recommend_window)


def show_haksik_option(recommend_window):
    for widget in recommend_window.winfo_children():
        widget.destroy()

    haksik_label = tk.Label(recommend_window, text="학식이나 먹어라🙄", padx=30, pady=30, fg='#ff0000', font=("Arial", 12))
    haksik_label.pack()

    haksik_button = tk.Button(recommend_window, text="오늘의 학식 메뉴 뭐야?", command=show_haksik_menu)
    haksik_button.pack(padx=10, pady=20)


def update_time(time_label):
    now = datetime.now().strftime("%Y-%m-%d %a %H:%M:%S")
    time_label.config(text=now)
    time_label.after(1000, lambda: update_time(time_label))


def update_weather(weather_label):
    weather = proc_weather()
    weather_label.config(text=weather)
    weather_label.after(1800000, lambda: update_weather(weather_label))


def main():
    root = tk.Tk()
    root.title("당신의 취향은?")

    food_preferences = {'양식': False, '한식': False, '일식': False}

    time_label = tk.Label(root, text="", font=("arial", 10))
    time_label.pack(pady=5)
    update_time(time_label)

    weather_label = tk.Label(root, text="", font=("arial", 10))
    weather_label.pack(pady=5)
    update_weather(weather_label)

    checkbox_frame = tk.Frame(root)
    checkbox_frame.pack(padx=34, pady=10)

    for food_type in food_preferences:
        chk = tk.Checkbutton(checkbox_frame, text=food_type,
                             command=lambda f=food_type: checkbox_click(food_preferences, f))
        chk.pack(side=tk.LEFT, padx=10)

    next_button = tk.Button(root, text="다음 단계", command=lambda: next_step(food_preferences, root))
    next_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
