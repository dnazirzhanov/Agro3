"""
Weather template tags for location name translations.

Provides custom template filters to translate location names (countries, regions, cities)
from English to Kyrgyz and Russian based on the current language setting.
"""
from django import template
from django.utils.translation import get_language

register = template.Library()

# Country name translations
COUNTRY_TRANSLATIONS = {
    'ky': {  # Kyrgyz translations
        'Afghanistan': 'Афганистан',
        'Kazakhstan': 'Казакстан',
        'Kyrgyzstan': 'Кыргызстан',
        'Russia': 'Россия',
        'Tajikistan': 'Тажикстан',
        'Turkmenistan': 'Түркмөнстан',
        'Uzbekistan': 'Өзбекстан',
        'China': 'Кытай',
        'Iran': 'Иран',
        'Mongolia': 'Монголия',
        'Pakistan': 'Пакистан',
        'Turkey': 'Түркия',
        'Ukraine': 'Украина',
        'United States': 'Америка Кошмо Штаттары',
        'United Kingdom': 'Улуу Британия',
        'Germany': 'Германия',
        'France': 'Франция',
        'Italy': 'Италия',
        'Spain': 'Испания',
        'Canada': 'Канада',
        'Australia': 'Австралия',
        'Japan': 'Япония',
        'India': 'Индия',
        'Brazil': 'Бразилия',
    },
    'ru': {  # Russian translations
        'Afghanistan': 'Афганистан',
        'Kazakhstan': 'Казахстан',
        'Kyrgyzstan': 'Кыргызстан',
        'Russia': 'Россия',
        'Tajikistan': 'Таджикистан',
        'Turkmenistan': 'Туркменистан',
        'Uzbekistan': 'Узбекистан',
        'China': 'Китай',
        'Iran': 'Иран',
        'Mongolia': 'Монголия',
        'Pakistan': 'Пакистан',
        'Turkey': 'Турция',
        'Ukraine': 'Украина',
        'United States': 'Соединенные Штаты Америки',
        'United Kingdom': 'Великобритания',
        'Germany': 'Германия',
        'France': 'Франция',
        'Italy': 'Италия',
        'Spain': 'Испания',
        'Canada': 'Канада',
        'Australia': 'Австралия',
        'Japan': 'Япония',
        'India': 'Индия',
        'Brazil': 'Бразилия',
    }
}

# Major city name translations for Central Asian countries
CITY_TRANSLATIONS = {
    'ky': {  # Kyrgyz translations
        'Bishkek': 'Бишкек',
        'Osh': 'Ош',
        'Jalal-Abad': 'Жалал-Абад',
        'Karakol': 'Каракол',
        'Tokmok': 'Токмок',
        'Uzgen': 'Өзгөн',
        'Naryn': 'Нарын',
        'Talas': 'Талас',
        'Batken': 'Баткен',
        'Kara-Balta': 'Кара-Балта',
        'Kant': 'Кант',
        'Kyzyl-Kiya': 'Кызыл-Кыя',
        'Cholpon-Ata': 'Чолпон-Ата',
        'Balykchy': 'Балыкчы',
        'Kerben': 'Кербен',
        'Tash-Kumyr': 'Таш-Көмүр',
        'Kochkor': 'Кочкор',
        'At-Bashi': 'Ат-Башы',
        'Aravan': 'Араван',
        'Nookat': 'Ноокат',
        'Almaty': 'Алматы',
        'Nur-Sultan': 'Нур-Султан',
        'Astana': 'Астана',
        'Shymkent': 'Шымкент',
        'Tashkent': 'Ташкент',
        'Samarkand': 'Самарканд',
        'Bukhara': 'Бухара',
        'Dushanbe': 'Душанбе',
        'Khujand': 'Худжанд',
        'Ashgabat': 'Ашгабат',
        'Moscow': 'Москва',
        'Saint Petersburg': 'Санкт-Петербург',
        'Yekaterinburg': 'Екатеринбург',
        'Novosibirsk': 'Новосибирск',
        'Urumqi': 'Үрүмчү',
        'Beijing': 'Пекин',
        'Shanghai': 'Шанхай',
        'Tehran': 'Тегеран',
        'Isfahan': 'Исфахан',
        'Kabul': 'Кабул',
        'Herat': 'Герат',
        'Islamabad': 'Исламабад',
        'Karachi': 'Карачи',
        'Lahore': 'Лахор'
    },
    'ru': {  # Russian translations
        'Bishkek': 'Бишкек',
        'Osh': 'Ош',
        'Jalal-Abad': 'Джалал-Абад',
        'Karakol': 'Каракол',
        'Tokmok': 'Токмак',
        'Uzgen': 'Узген',
        'Naryn': 'Нарын',
        'Talas': 'Талас',
        'Batken': 'Баткен',
        'Kara-Balta': 'Кара-Балта',
        'Kant': 'Кант',
        'Kyzyl-Kiya': 'Кызыл-Кия',
        'Cholpon-Ata': 'Чолпон-Ата',
        'Balykchy': 'Балыкчи',
        'Kerben': 'Кербен',
        'Tash-Kumyr': 'Таш-Кумыр',
        'Kochkor': 'Кочкор',
        'At-Bashi': 'Ат-Баши',
        'Aravan': 'Араван',
        'Nookat': 'Ноокат',
        'Almaty': 'Алматы',
        'Nur-Sultan': 'Нур-Султан',
        'Astana': 'Астана',
        'Shymkent': 'Шымкент',
        'Tashkent': 'Ташкент',
        'Samarkand': 'Самарканд',
        'Bukhara': 'Бухара',
        'Dushanbe': 'Душанбе',
        'Khujand': 'Худжанд',
        'Ashgabat': 'Ашгабат',
        'Moscow': 'Москва',
        'Saint Petersburg': 'Санкт-Петербург',
        'Yekaterinburg': 'Екатеринбург',
        'Novosibirsk': 'Новосибирск',
        'Urumqi': 'Урумчи',
        'Beijing': 'Пекин',
        'Shanghai': 'Шанхай',
        'Tehran': 'Тегеран',
        'Isfahan': 'Исфахан',
        'Kabul': 'Кабул',
        'Herat': 'Герат',
        'Islamabad': 'Исламабад',
        'Karachi': 'Карачи',
        'Lahore': 'Лахор'
    }
}

# Region/State name translations for all countries
REGION_TRANSLATIONS = {
    'ky': {  # Kyrgyz translations
        # Kyrgyzstan regions (official names)
        'Batken': 'Баткен',
        'Batken Region': 'Баткен областы',
        'Bishkek City': 'Бишкек шаары',
        'Chuy': 'Чүй',
        'Chuy Region': 'Чүй областы',
        'Issyk-Kul': 'Ысык-Көл',
        'Issyk-Kul Region': 'Ысык-Көл областы',
        'Jalal-Abad': 'Жалал-Абад',
        'Jalal-Abad Region': 'Жалал-Абад областы',
        'Naryn': 'Нарын',
        'Naryn Region': 'Нарын областы',
        'Osh': 'Ош',
        'Osh City': 'Ош шаары',
        'Osh Region': 'Ош областы',
        'Talas': 'Талас',
        'Talas Region': 'Талас областы',
        
        # Kazakhstan regions
        'Akmola Region': 'Акмола областы',
        'Aktobe Region': 'Ақтөбе областы',
        'Almaty City': 'Алматы шаары',
        'Almaty Region': 'Алматы областы',
        'Atyrau Region': 'Атырау областы',
        'East Kazakhstan Region': 'Чыгыш Казакстан областы',
        'Mangystau Region': 'Маңғыстау областы',
        'Nur-Sultan City': 'Нур-Султан шаары',
        'Shymkent City': 'Шымкент шаары',
        'South Kazakhstan Region': 'Түштүк Казакстан областы',
        'West Kazakhstan Region': 'Батыш Казакстан областы',
        
        # Uzbekistan regions
        'Andijan Region': 'Андижан областы',
        'Bukhara Region': 'Бухара областы',
        'Fergana Region': 'Фергана областы',
        'Jizzakh Region': 'Жиззах областы',
        'Karakalpakstan': 'Каракалпакстан',
        'Karakalpakstan Republic': 'Каракалпакстан Республикасы',
        'Kashkadarya Region': 'Кашкадария областы',
        'Khorezm Region': 'Хорезм областы',
        'Namangan Region': 'Наманган областы',
        'Navoiy Region': 'Навоий областы',
        'Samarkand Region': 'Самарканд областы',
        'Sirdaryo Region': 'Сырдария областы',
        'Surkhandarya Region': 'Сурхандария областы',
        'Tashkent City': 'Ташкент шаары',
        'Tashkent Region': 'Ташкент областы',
        
        # Tajikistan regions
        'Districts of Republican Subordination': 'Республикалык баш кармоодогу районлор',
        'Dushanbe': 'Душанбе',
        'Dushanbe City': 'Душанбе шаары',
        'Gorno-Badakhshan': 'Горно-Бадахшан',
        'Gorno-Badakhshan Autonomous Region': 'Горно-Бадахшан автономдуу областы',
        'Khatlon Region': 'Хатлон областы',
        'Sughd Region': 'Согд областы',
        
        # Russia regions (main ones)
        'Moscow': 'Москва',
        'Moscow City': 'Москва шаары',
        'Moscow Oblast': 'Москва областы',
        'Moscow Region': 'Москва областы',
        'Saint Petersburg': 'Санкт-Петербург',
        'Saint Petersburg City': 'Санкт-Петербург шаары',
        'Novosibirsk Oblast': 'Новосибирск областы',
        'Novosibirsk Region': 'Новосибирск областы',
        'Sverdlovsk Oblast': 'Свердловск областы',
        'Sverdlovsk Region': 'Свердловск областы',
        'Tatarstan': 'Татарстан',
        'Tatarstan Republic': 'Татарстан Республикасы',
        'Bashkortostan': 'Башкортостан',
        'Krasnodar Krai': 'Краснодар крайы',
        'Krasnoyarsk Krai': 'Красноярск крайы',
    },
    'ru': {  # Russian translations
        # Kyrgyzstan regions (official Russian names)
        'Batken': 'Баткен',
        'Batken Region': 'Баткенская область',
        'Bishkek City': 'город Бишкек',
        'Chuy': 'Чуй',
        'Chuy Region': 'Чуйская область',
        'Issyk-Kul': 'Иссык-Куль',
        'Issyk-Kul Region': 'Иссык-Кульская область',
        'Jalal-Abad': 'Джалал-Абад',
        'Jalal-Abad Region': 'Джалал-Абадская область',
        'Naryn': 'Нарын',
        'Naryn Region': 'Нарынская область',
        'Osh': 'Ош',
        'Osh City': 'город Ош',
        'Osh Region': 'Ошская область',
        'Talas': 'Талас',
        'Talas Region': 'Таласская область',
        
        # Kazakhstan regions (official Russian names)
        'Akmola Region': 'Акмолинская область',
        'Aktobe Region': 'Актюбинская область',
        'Almaty City': 'город Алматы',
        'Almaty Region': 'Алматинская область',
        'Atyrau Region': 'Атырауская область',
        'East Kazakhstan Region': 'Восточно-Казахстанская область',
        'Mangystau Region': 'Мангистауская область',
        'Nur-Sultan City': 'город Нур-Султан',
        'Shymkent City': 'город Шымкент',
        'South Kazakhstan Region': 'Южно-Казахстанская область',
        'West Kazakhstan Region': 'Западно-Казахстанская область',
        
        # Uzbekistan regions (official Russian names)
        'Andijan Region': 'Андижанская область',
        'Bukhara Region': 'Бухарская область',
        'Fergana Region': 'Ферганская область',
        'Jizzakh Region': 'Джизакская область',
        'Karakalpakstan': 'Каракалпакстан',
        'Karakalpakstan Republic': 'Республика Каракалпакстан',
        'Kashkadarya Region': 'Кашкадарьинская область',
        'Khorezm Region': 'Хорезмская область',
        'Namangan Region': 'Наманганская область',
        'Navoiy Region': 'Навоийская область',
        'Samarkand Region': 'Самаркандская область',
        'Sirdaryo Region': 'Сырдарьинская область',
        'Surkhandarya Region': 'Сурхандарьинская область',
        'Tashkent City': 'город Ташкент',
        'Tashkent Region': 'Ташкентская область',
        
        # Tajikistan regions (official Russian names)
        'Districts of Republican Subordination': 'Районы республиканского подчинения',
        'Dushanbe': 'Душанбе',
        'Dushanbe City': 'город Душанбе',
        'Gorno-Badakhshan': 'Горно-Бадахшан',
        'Gorno-Badakhshan Autonomous Region': 'Горно-Бадахшанская автономная область',
        'Khatlon Region': 'Хатлонская область',
        'Sughd Region': 'Согдийская область',
        
        # Russia regions (official names)
        'Moscow': 'Москва',
        'Moscow City': 'город Москва',
        'Moscow Oblast': 'Московская область',
        'Moscow Region': 'Московская область',
        'Saint Petersburg': 'Санкт-Петербург',
        'Saint Petersburg City': 'город Санкт-Петербург',
        'Novosibirsk Oblast': 'Новосибирская область',
        'Novosibirsk Region': 'Новосибирская область',
        'Sverdlovsk Oblast': 'Свердловская область',
        'Sverdlovsk Region': 'Свердловская область',
        'Tatarstan': 'Татарстан',
        'Tatarstan Republic': 'Республика Татарстан',
        'Bashkortostan': 'Башкортостан',
        'Krasnodar Krai': 'Краснодарский край',
        'Krasnoyarsk Krai': 'Красноярский край',
        'Chelyabinsk Oblast': 'Челябинская область',
        'Kemerovo Oblast': 'Кемеровская область',
        'Nizhny Novgorod Oblast': 'Нижегородская область',
        'Omsk Oblast': 'Омская область',
        'Perm Krai': 'Пермский край',
        'Rostov Oblast': 'Ростовская область',
        'Rostov Region': 'Ростовская область',
        'Samara Oblast': 'Самарская область',
        'Saratov Oblast': 'Саратовская область',
        'Tyumen Oblast': 'Тюменская область',
        'Volgograd Oblast': 'Волгоградская область',
        'Voronezh Oblast': 'Воронежская область',
    }
}


@register.filter
def translate_location(location_name):
    """
    Translate location name (country or city) to current language.
    
    Args:
        location_name: The English location name to translate
        
    Returns:
        Translated location name or original name if no translation found
    """
    if not location_name:
        return location_name
        
    current_lang = get_language()
    
    # Skip translation for English or unsupported languages
    if current_lang not in ['ky', 'ru']:
        return location_name
    
    # Try country translation first
    country_translations = COUNTRY_TRANSLATIONS.get(current_lang, {})
    if location_name in country_translations:
        return country_translations[location_name]
    
    # Try region translation
    region_translations = REGION_TRANSLATIONS.get(current_lang, {})
    if location_name in region_translations:
        return region_translations[location_name]
    
    # Try city translation
    city_translations = CITY_TRANSLATIONS.get(current_lang, {})
    if location_name in city_translations:
        return city_translations[location_name]
    
    # Return original name if no translation found
    return location_name


@register.filter
def translate_country(country_name):
    """
    Translate country name to current language.
    
    Args:
        country_name: The English country name to translate
        
    Returns:
        Translated country name or original name if no translation found
    """
    if not country_name:
        return country_name
        
    current_lang = get_language()
    
    # Skip translation for English or unsupported languages
    if current_lang not in ['ky', 'ru']:
        return country_name
    
    country_translations = COUNTRY_TRANSLATIONS.get(current_lang, {})
    return country_translations.get(country_name, country_name)


@register.filter
def translate_city(city_name):
    """
    Translate city name to current language.
    
    Args:
        city_name: The English city name to translate
        
    Returns:
        Translated city name or original name if no translation found
    """
    if not city_name:
        return city_name
        
    current_lang = get_language()
    
    # Skip translation for English or unsupported languages
    if current_lang not in ['ky', 'ru']:
        return city_name
    
    city_translations = CITY_TRANSLATIONS.get(current_lang, {})
    return city_translations.get(city_name, city_name)


@register.filter
def translate_region(region_name):
    """
    Translate region/state name to current language.
    
    Args:
        region_name: The English region name to translate
        
    Returns:
        Translated region name or original name if no translation found
    """
    if not region_name:
        return region_name
        
    current_lang = get_language()
    
    # Skip translation for English or unsupported languages
    if current_lang not in ['ky', 'ru']:
        return region_name
    
    region_translations = REGION_TRANSLATIONS.get(current_lang, {})
    return region_translations.get(region_name, region_name)