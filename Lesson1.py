msc_price = 13_000
spb_price = 10_000
ekb_price = 8_000

dist = input("Введите пункт назначения (msc, spb, ekb): ")
count = int(input("Введите количество людей: "))

if dist == "msc":
    price = msc_price * count
elif dist == "spb":
    price = spb_price * count
elif dist == "ekb":
    price = ekb_price * count

print("Цена поездки: ", price, "руб.")
