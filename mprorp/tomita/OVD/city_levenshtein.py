def distance(a, b):
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n
    current_row = range(n+1)
    for i in range(1, m+1):
        previous_row, current_row = current_row, [i]+[0]*n
        for j in range(1,n+1):
            add, delete, change = previous_row[j]+1, current_row[j-1]+1, previous_row[j-1]
            if a[j-1] != b[i-1]:
                change += 1
            current_row[j] = min(add, delete, change)
    return current_row[n]

def min_distance(line, arr):
    out = []
    min_d = len(line) + 10
    for i in arr:
        d = distance(line, i)
        if d < min_d:
            min_d = d
            out = [i]
        elif d == min_d:
            out.append(i)
    if min_d > (len(line) / 2):
        return []
    else:
        return list(set(out))

cities = ['Абаза',
'Абакан',
'Абдулино',
'Абинск',
'Агидель',
'Агрыз',
'Адыгейск',
'Азнакаево',
'Азов',
'Ак-Довурак',
'Аксай',
'Алагир',
'Алапаевск',
'Алатырь',
'Алдан',
'Алейск',
'Александров',
'Александровск',
'Александровск-Сахалинский',
'Алексеевка',
'Алексин',
'Алзамай',
'Алупка',
'Алушта',
'Альметьевск',
'Амурск',
'Анадырь',
'Анапа',
'Ангарск',
'Андреаполь',
'Анжеро-Судженск',
'Анива',
'Апатиты',
'Апрелевка',
'Апшеронск',
'Арамиль',
'Аргун',
'Ардатов',
'Ардон',
'Арзамас',
'Аркадак',
'Армавир',
'Армянск',
'Армянськ',
'Арсеньев',
'Арск',
'Артем',
'Артемовск',
'Артемовский',
'Архангельск',
'Асбест',
'Асино',
'Астрахань',
'Аткарск',
'Ахтубинск',
'Ахтубинск-7',
'Ачинск',
'Аша',
'Бабаево',
'Бабушкин',
'Бавлы',
'Багратионовск',
'Байкальск',
'Баймак',
'Бакал',
'Баксан',
'Балабаново',
'Балаково',
'Балахна',
'Балашиха',
'Балашов',
'Балей',
'Балтийск',
'Барабинск',
'Барнаул',
'Барыш',
'Батайск',
'Бахчисарай',
'Бежецк',
'Белая Калитва',
'Белая Холуница',
'Белгород',
'Белебей',
'Белев',
'Белинский',
'Белово',
'Белогорск',
'Белогорск',
'Белозерск',
'Белокуриха',
'Беломорск',
'Белорецк',
'Белореченск',
'Белоусово',
'Белоярский',
'Белый',
'Бердск',
'Березники',
'Березовский',
'Березовский',
'Беслан',
'Бийск',
'Бикин',
'Билибино',
'Биробиджан',
'Бирск',
'Бирюсинск',
'Бирюч',
'Благовещенск',
'Благовещенск',
'Благодарный',
'Бобров',
'Богданович',
'Богородицк',
'Богородск',
'Боготол',
'Богучар',
'Бодайбо',
'Бокситогорск',
'Болгар',
'Бологое',
'Болотное',
'Болохово',
'Болхов',
'Большой Камень',
'Бор',
'Борзя',
'Борисоглебск',
'Боровичи',
'Боровск',
'Боровск-1',
'Бородино',
'Братск',
'Бронницы',
'Брянск',
'Бугульма',
'Бугуруслан',
'Буденновск',
'Бузулук',
'Буинск',
'Буй',
'Буйнакск',
'Бутурлиновка',
'Валдай',
'Валуйки',
'Велиж',
'Великие Луки',
'Великие Луки-1',
'Великий Новгород',
'Великий Устюг',
'Вельск',
'Венев',
'Верещагино',
'Верея',
'Верхнеуральск',
'Верхний Тагил',
'Верхний Уфалей',
'Верхняя Пышма',
'Верхняя Салда',
'Верхняя Тура',
'Верхотурье',
'Верхоянск',
'Весьегонск',
'Ветлуга',
'Видное',
'Вилюйск',
'Вилючинск',
'Вихоревка',
'Вичуга',
'Владивосток',
'Владикавказ',
'Владимир',
'Волгоград',
'Волгодонск',
'Волгореченск',
'Волжск',
'Волжский',
'Вологда',
'Володарск',
'Волоколамск',
'Волосово',
'Волхов',
'Волчанск',
'Вольск',
'Вольск-18',
'Воркута',
'Воронеж',
'Воронеж-45',
'Ворсма',
'Воскресенск',
'Воткинск',
'Всеволожск',
'Вуктыл',
'Выборг',
'Выкса',
'Высоковск',
'Высоцк',
'Вытегра',
'Вышний Волочек',
'Вяземский',
'Вязники',
'Вязьма',
'Вятские Поляны',
'Гаврилов Посад',
'Гаврилов-Ям',
'Гагарин',
'Гаджиево',
'Гай',
'Галич',
'Гатчина',
'Гвардейск',
'Гдов',
'Геленджик',
'Георгиевск',
'Глазов',
'Голицыно',
'Горбатов',
'Горно-Алтайск',
'Горнозаводск',
'Горняк',
'Городец',
'Городище',
'Городовиковск',
'Городской округ Черноголовка',
'Гороховец',
'Горячий Ключ',
'Грайворон',
'Гремячинск',
'Грозный',
'Грязи',
'Грязовец',
'Губаха',
'Губкин',
'Губкинский',
'Гудермес',
'Гуково',
'Гулькевичи',
'Гурьевск',
'Гурьевск',
'Гусев',
'Гусиноозерск',
'Гусь-Хрустальный',
'Давлеканово',
'Дагестанские Огни',
'Далматово',
'Дальнегорск',
'Дальнереченск',
'Данилов',
'Данков',
'Дегтярск',
'Дедовск',
'Демидов',
'Дербент',
'Десногорск',
'Джанкой',
'Джанкой',
'Дзержинск',
'Дзержинский',
'Дивногорск',
'Дигора',
'Димитровград',
'Дмитриев',
'Дмитров',
'Дмитровск',
'Дно',
'Добрянка',
'Долгопрудный',
'Долинск',
'Домодедово',
'Донецк',
'Донской',
'Дорогобуж',
'Дрезна',
'Дубна',
'Дубовка',
'Дудинка',
'Духовщина',
'Дюртюли',
'Дятьково',
'Евпатория',
'Егорьевск',
'Ейск',
'Екатеринбург',
'Елабуга',
'Елец',
'Елизово',
'Ельня',
'Еманжелинск',
'Емва',
'Енисейск',
'Ермолино',
'Ершов',
'Ессентуки',
'Ефремов',
'Железноводск',
'Железногорск',
'Железногорск',
'Железногорск-Илимский',
'Железнодорожный',
'Жердевка',
'Жигулевск',
'Жиздра',
'Жирновск',
'Жуков',
'Жуковка',
'Жуковский',
'Завитинск',
'Заводоуковск',
'Заволжск',
'Заволжье',
'Задонск',
'Заинск',
'Закаменск',
'Заозерный',
'Заозерск',
'Западная Двина',
'Заполярный',
'Зарайск',
'Заречный',
'Заречный',
'Заринск',
'Звенигово',
'Звенигород',
'Зверево',
'Зеленогорск',
'Зеленогорск',
'Зеленоград',
'Зеленоградск',
'Зеленодольск',
'Зеленокумск',
'Зерноград',
'Зея',
'Зима',
'Златоуст',
'Злынка',
'Змеиногорск',
'Знаменск',
'Зубцов',
'Зуевка',
'Ивангород',
'Иваново',
'Ивантеевка',
'Ивдель',
'Игарка',
'Ижевск',
'Избербаш',
'Изобильный',
'Иланский',
'Инза',
'Инкерман',
'Инсар',
'Инта',
'Ипатово',
'Ирбит',
'Иркутск',
'Иркутск-45',
'Исилькуль',
'Искитим',
'Истра',
'Истра-1',
'Ишим',
'Ишимбай',
'Йошкар-Ола',
'Кадников',
'Казань',
'Калач',
'Калачинск',
'Калач-на-Дону',
'Калининград',
'Калининск',
'Калтан',
'Калуга',
'Калязин',
'Камбарка',
'Каменка',
'Каменногорск',
'Каменск-Уральский',
'Каменск-Шахтинский',
'Камень-на-Оби',
'Камешково',
'Камызяк',
'Камышин',
'Камышлов',
'Канаш',
'Кандалакша',
'Канск',
'Карабаново',
'Карабаш',
'Карабулак',
'Карасук',
'Карачаевск',
'Карачев',
'Каргат',
'Каргополь',
'Карпинск',
'Карталы',
'Касимов',
'Касли',
'Каспийск',
'Катав-Ивановск',
'Катайск',
'Качканар',
'Кашин',
'Кашира',
'Кашира-8',
'Кедровый',
'Кемерово',
'Кемь',
'Керчь',
'Кизел',
'Кизилюрт',
'Кизляр',
'Кимовск',
'Кимры',
'Кингисепп',
'Кинель',
'Кинешма',
'Киреевск',
'Киренск',
'Киржач',
'Кириллов',
'Кириши',
'Киров',
'Киров',
'Кировград',
'Кирово-Чепецк',
'Кировск',
'Кировск',
'Кирс',
'Кирсанов',
'Киселевск',
'Кисловодск',
'Климовск',
'Клин',
'Клинцы',
'Княгинино',
'Ковдор',
'Ковров',
'Ковылкино',
'Когалым',
'Кодинск',
'Козельск',
'Козловка',
'Козьмодемьянск',
'Кола',
'Кологрив',
'Коломна',
'Колпашево',
'Колпино',
'Кольчугино',
'Коммунар',
'Комсомольск',
'Комсомольск-на-Амуре',
'Конаково',
'Кондопога',
'Кондрово',
'Константиновск',
'Копейск',
'Кораблино',
'Кореновск',
'Коркино',
'Королев',
'Короча',
'Корсаков',
'Коряжма',
'Костерево',
'Костомукша',
'Кострома',
'Котельники',
'Котельниково',
'Котельнич',
'Котлас',
'Котово',
'Котовск',
'Кохма',
'Красавино',
'Красноармейск',
'Красноармейск',
'Красновишерск',
'Красногорск',
'Краснодар',
'Красное Село',
'Краснозаводск',
'Краснознаменск',
'Краснознаменск',
'Краснокаменск',
'Краснокамск',
'Красноперекопск',
'Красноперекопск',
'Краснослободск',
'Краснослободск',
'Краснотурьинск',
'Красноуральск',
'Красноуфимск',
'Красноярск',
'Красный Кут',
'Красный Сулин',
'Красный Холм',
'Кременки',
'Кронштадт',
'Кропоткин',
'Крымск',
'Кстово',
'Кубинка',
'Кувандык',
'Кувшиново',
'Кудымкар',
'Кузнецк',
'Кузнецк-12',
'Кузнецк-8',
'Куйбышев',
'Кулебаки',
'Кумертау',
'Кунгур',
'Купино',
'Курган',
'Курганинск',
'Курильск',
'Курлово',
'Куровское',
'Курск',
'Куртамыш',
'Курчатов',
'Куса',
'Кушва',
'Кызыл',
'Кыштым',
'Кяхта',
'Лабинск',
'Лабытнанги',
'Лагань',
'Ладушкин',
'Лаишево',
'Лакинск',
'Лангепас',
'Лахденпохья',
'Лебедянь',
'Лениногорск',
'Ленинск',
'Ленинск-Кузнецкий',
'Ленск',
'Лермонтов',
'Лесной',
'Лесозаводск',
'Лесосибирск',
'Ливны',
'Ликино-Дулево',
'Липецк',
'Липки',
'Лиски',
'Лихославль',
'Лобня',
'Лодейное Поле',
'Ломоносов',
'Лосино-Петровский',
'Луга',
'Луза',
'Лукоянов',
'Луховицы',
'Лысково',
'Лысьва',
'Лыткарино',
'Льгов',
'Любань',
'Люберцы',
'Любим',
'Людиново',
'Лянтор',
'Магадан',
'Магас',
'Магнитогорск',
'Майкоп',
'Майский',
'Макаров',
'Макарьев',
'Макушино',
'Малая Вишера',
'Малгобек',
'Малмыж',
'Малоархангельск',
'Малоярославец',
'Мамадыш',
'Мамоново',
'Мантурово',
'Мариинск',
'Мариинский Посад',
'Маркс',
'Махачкала',
'Мглин',
'Мегион',
'Медвежьегорск',
'Медногорск',
'Медынь',
'Межгорье',
'Междуреченск',
'Мезень',
'Меленки',
'Мелеуз',
'Менделеевск',
'Мензелинск',
'Мещовск',
'Миасс',
'Микунь',
'Миллерово',
'Минеральные Воды',
'Минусинск',
'Миньяр',
'Мирный',
'Мирный',
'Михайлов',
'Михайловка',
'Михайловск',
'Михайловск',
'Мичуринск',
'Могоча',
'Можайск',
'Можга',
'Моздок',
'Мончегорск',
'Морозовск',
'Моршанск',
'Мосальск',
'Москва',
'Московский',
'Московский',
'Муравленко',
'Мураши',
'Мурманск',
'Муром',
'Мценск',
'Мыски',
'Мытищи',
'Мышкин',
'Набережные Челны',
'Навашино',
'Наволоки',
'Надым',
'Назарово',
'Назрань',
'Называевск',
'Нальчик',
'Нариманов',
'Наро-Фоминск',
'Нарткала',
'Нарьян-Мар',
'Находка',
'Невель',
'Невельск',
'Невинномысск',
'Невьянск',
'Нелидово',
'Неман',
'Нерехта',
'Нерчинск',
'Нерюнгри',
'Нестеров',
'Нефтегорск',
'Нефтекамск',
'Нефтекумск',
'Нефтеюганск',
'Нея',
'Нижневартовск',
'Нижнекамск',
'Нижнеудинск',
'Нижние Серги',
'Нижние Серги-3',
'Нижний Ломов',
'Нижний Новгород',
'Нижний Тагил',
'Нижняя Салда',
'Нижняя Тура',
'Николаевск',
'Николаевск-на-Амуре',
'Никольск',
'Никольск',
'Никольское',
'Новая Ладога',
'Новая Ляля',
'Новоалександровск',
'Новоалтайск',
'Новоаннинский',
'Нововоронеж',
'Новодвинск',
'Новозыбков',
'Новокубанск',
'Новокузнецк',
'Новокуйбышевск',
'Новомичуринск',
'Новомосковск',
'Новопавловск',
'Новоржев',
'Новороссийск',
'Новосибирск',
'Новосиль',
'Новосокольники',
'Новотроицк',
'Новоузенск',
'Новоульяновск',
'Новоуральск',
'Новохоперск',
'Новочебоксарск',
'Новочеркасск',
'Новошахтинск',
'Новый Оскол',
'Новый Уренгой',
'Ногинск',
'Нолинск',
'Норильск',
'Ноябрьск',
'Нурлат',
'Нытва',
'Нюрба',
'Нягань',
'Нязепетровск',
'Няндома',
'Облучье',
'Обнинск',
'Обоянь',
'Обь',
'Одинцово',
'Ожерелье',
'Озерск',
'Озерск',
'Озеры',
'Октябрьск',
'Октябрьский',
'Окуловка',
'Олекминск',
'Оленегорск',
'Оленегорск-1',
'Оленегорск-2',
'Оленегорск-4',
'Олонец',
'Омск',
'Омутнинск',
'Онега',
'Опочка',
'Орёл',
'Оренбург',
'Орехово-Зуево',
'Орлов',
'Орск',
'Оса',
'Осинники',
'Осташков',
'Остров',
'Островной',
'Острогожск',
'Отрадное',
'Отрадный',
'Оха',
'Оханск',
'Очер',
'Павлово',
'Павловск',
'Павловск',
'Павловский Посад',
'Палласовка',
'Партизанск',
'Певек',
'Пенза',
'Первомайск',
'Первоуральск',
'Перевоз',
'Пересвет',
'Переславль-Залесский',
'Пермь',
'Пестово',
'Петергоф',
'Петров Вал',
'Петровск',
'Петровск-Забайкальский',
'Петрозаводск',
'Петропавловск-Камчатский',
'Петухово',
'Петушки',
'Печора',
'Печоры',
'Пикалево',
'Пионерский',
'Питкяранта',
'Плавск',
'Пласт',
'Плес',
'Поворино',
'Подгорное',
'Подольск',
'Подпорожье',
'Покачи',
'Покров',
'Покровск',
'Полевской',
'Полесск',
'Полысаево',
'Полярные Зори',
'Полярный',
'Поронайск',
'Порхов',
'Похвистнево',
'Почеп',
'Починок',
'Пошехонье',
'Правдинск',
'Приволжск',
'Приморск',
'Приморск',
'Приморско-Ахтарск',
'Приозерск',
'Прокопьевск',
'Пролетарск',
'Протвино',
'Прохладный',
'Псков',
'Пугачев',
'Пудож',
'Пустошка',
'Пучеж',
'Пушкин',
'Пушкино',
'Пущино',
'Пыталово',
'Пыть-Ях',
'Пятигорск',
'Радужный',
'Радужный',
'Райчихинск',
'Раменское',
'Рассказово',
'Ревда',
'Реж',
'Реутов',
'Ржев',
'Родники',
'Рославль',
'Россошь',
'Ростов',
'Ростов-на-Дону',
'Рошаль',
'Ртищево',
'Рубцовск',
'Рудня',
'Руза',
'Рузаевка',
'Рыбинск',
'Рыбное',
'Рыльск',
'Ряжск',
'Рязань',
'Саки',
'Саки',
'Салават',
'Салаир',
'Салехард',
'Сальск',
'Самара',
'Санкт-Петербург',
'Саранск',
'Сарапул',
'Саратов',
'Саров',
'Сасово',
'Сатка',
'Сафоново',
'Саяногорск',
'Саянск',
'Светлогорск',
'Светлоград',
'Светлый',
'Светогорск',
'Свирск',
'Свободный',
'Себеж',
'Севастополь',
'Северобайкальск',
'Северодвинск',
'Северо-Курильск',
'Североморск',
'Североуральск',
'Северск',
'Севск',
'Сегежа',
'Сельцо',
'Семенов',
'Семикаракорск',
'Семилуки',
'Сенгилей',
'Серафимович',
'Сергач',
'Сергиев Посад',
'Сергиев Посад-7',
'Сердобск',
'Серов',
'Серпухов',
'Сертолово',
'Сестрорецк',
'Сибай',
'Сим',
'Симферополь',
'Сковородино',
'Скопин',
'Славгород',
'Славск',
'Славянск-на-Кубани',
'Сланцы',
'Слободской',
'Слюдянка',
'Смоленск',
'Снегири',
'Снежинск',
'Снежногорск',
'Собинка',
'Советск',
'Советск',
'Советск',
'Советская Гавань',
'Советский',
'Сокол',
'Солигалич',
'Соликамск',
'Солнечногорск',
'Солнечногорск-2',
'Солнечногорск-25',
'Солнечногорск-30',
'Солнечногорск-7',
'Сольвычегодск',
'Соль-Илецк',
'Сольцы',
'Сольцы 2',
'Сорочинск',
'Сорск',
'Сортавала',
'Сосенский',
'Сосновка',
'Сосновоборск',
'Сосновый Бор',
'Сосногорск',
'Сочи',
'Спас-Деменск',
'Спас-Клепики',
'Спасск',
'Спасск-Дальний',
'Спасск-Рязанский',
'Среднеколымск',
'Среднеуральск',
'Сретенск',
'Ставрополь',
'Старая Купавна',
'Старая Русса',
'Старица',
'Стародуб',
'Старый крым',
'Старый Оскол',
'Стерлитамак',
'Стрежевой',
'Строитель',
'Струнино',
'Ступино',
'Суворов',
'Судак',
'Суджа',
'Судогда',
'Суздаль',
'Суоярви',
'Сураж',
'Сургут',
'Суровикино',
'Сурск',
'Сусуман',
'Сухиничи',
'Сухой Лог',
'Сызрань',
'Сыктывкар',
'Сысерть',
'Сычевка',
'Сясьстрой',
'Тавда',
'Таганрог',
'Тайга',
'Тайшет',
'Талдом',
'Талица',
'Тамбов',
'Тара',
'Тарко-Сале',
'Таруса',
'Татарск',
'Таштагол',
'Тверь',
'Теберда',
'Тейково',
'Темников',
'Темрюк',
'Терек',
'Тетюши',
'Тимашевск',
'Тихвин',
'Тихорецк',
'Тобольск',
'Тогучин',
'Тольятти',
'Томари',
'Томмот',
'Томск',
'Топки',
'Торжок',
'Торопец',
'Тосно',
'Тотьма',
'Трехгорный',
'Трехгорный-1',
'Троицк',
'Троицк',
'Трубчевск',
'Туапсе',
'Туймазы',
'Тула',
'Тулун',
'Туран',
'Туринск',
'Тутаев',
'Тында',
'Тырныауз',
'Тюкалинск',
'Тюмень',
'Уварово',
'Углегорск',
'Углич',
'Удачный',
'Удомля',
'Ужур',
'Узловая',
'Улан-Удэ',
'Ульяновск',
'Унеча',
'Урай',
'Урень',
'Уржум',
'Урус-Мартан',
'Урюпинск',
'Усинск',
'Усмань',
'Усолье',
'Усолье-Сибирское',
'Уссурийск',
'Усть-Джегута',
'Усть-Илимск',
'Усть-Катав',
'Усть-Кут',
'Усть-Лабинск',
'Устюжна',
'Уфа',
'Ухта',
'Учалы',
'Уяр',
'Фатеж',
'Феодосия',
'Фокино',
'Фокино',
'Фролово',
'Фрязино',
'Фурманов',
'Хабаровск',
'Хадыженск',
'Ханты-Мансийск',
'Харабали',
'Харовск',
'Хасавюрт',
'Хвалынск',
'Хилок',
'Химки',
'Холм',
'Холмск',
'Хотьково',
'Цивильск',
'Цимлянск',
'Чадан',
'Чайковский',
'Чапаевск',
'Чаплыгин',
'Чебаркуль',
'Чебоксары',
'Чегем',
'Чекалин',
'Челябинск',
'Чердынь',
'Черемхово',
'Черепаново',
'Череповец',
'Черкесск',
'Чермоз',
'Черноголовка',
'Черногорск',
'Чернушка',
'Черняховск',
'Чехов',
'Чехов-2',
'Чехов-3',
'Чехов-8',
'Чистополь',
'Чита',
'Чкаловск',
'Чудово',
'Чулым',
'Чулым-3',
'Чусовой',
'Чухлома',
'Шагонар',
'Шадринск',
'Шали',
'Шарыпово',
'Шарья',
'Шатура',
'Шахтерск',
'Шахты',
'Шахунья',
'Шацк',
'Шебекино',
'Шелехов',
'Шенкурск',
'Шилка',
'Шимановск',
'Шиханы',
'Шлиссельбург',
'Шумерля',
'Шумиха',
'Шуя',
'Щекино',
'Щелкино',
'Щелково',
'Щербинка',
'Щигры',
'Щучье',
'Электрогорск',
'Электросталь',
'Электроугли',
'Элиста',
'Энгельс',
'Энгельс-19',
'Энгельс-2',
'Эртиль',
'Юбилейный',
'Югорск',
'Южа',
'Южно-Сахалинск',
'Южно-Сухокумск',
'Южноуральск',
'Юрга',
'Юрьевец',
'Юрьев-Польский',
'Юрюзань',
'Юхнов',
'Юхнов-1',
'Юхнов-2',
'Ядрин',
'Якутск',
'Ялта',
'Ялуторовск',
'Янаул',
'Яранск',
'Яровое',
'Ярославль',
'Ярцево',
'Ясногорск',
'Ясный',
'Яхрома']