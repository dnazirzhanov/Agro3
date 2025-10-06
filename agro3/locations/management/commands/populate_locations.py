from django.core.management.base import BaseCommand
from locations.models import Country, Region


class Command(BaseCommand):
    help = 'Populate countries and regions with multilingual data'
    
    def handle(self, *args, **options):
        # Define countries and their regions with translations
        countries_data = {
            'USA': {
                'code': 'US',
                'translations': {
                    'en': 'United States',
                    'ru': 'США',
                    'ky': 'Америка Кошмо Штаттары'
                },
                'region_type': 'State',
                'regions': [
                    {'name': {'en': 'Alabama', 'ru': 'Алабама', 'ky': 'Алабама'}},
                    {'name': {'en': 'Alaska', 'ru': 'Аляска', 'ky': 'Аляска'}},
                    {'name': {'en': 'Arizona', 'ru': 'Аризона', 'ky': 'Аризона'}},
                    {'name': {'en': 'Arkansas', 'ru': 'Арканзас', 'ky': 'Арканзас'}},
                    {'name': {'en': 'California', 'ru': 'Калифорния', 'ky': 'Калифорния'}},
                    {'name': {'en': 'Colorado', 'ru': 'Колорадо', 'ky': 'Колорадо'}},
                    {'name': {'en': 'Connecticut', 'ru': 'Коннектикут', 'ky': 'Коннектикут'}},
                    {'name': {'en': 'Delaware', 'ru': 'Делавэр', 'ky': 'Делавэр'}},
                    {'name': {'en': 'Florida', 'ru': 'Флорида', 'ky': 'Флорида'}},
                    {'name': {'en': 'Georgia', 'ru': 'Джорджия', 'ky': 'Жоржия'}},
                    {'name': {'en': 'Hawaii', 'ru': 'Гавайи', 'ky': 'Гавайи'}},
                    {'name': {'en': 'Idaho', 'ru': 'Айдахо', 'ky': 'Айдахо'}},
                    {'name': {'en': 'Illinois', 'ru': 'Иллинойс', 'ky': 'Иллинойс'}},
                    {'name': {'en': 'Indiana', 'ru': 'Индиана', 'ky': 'Индиана'}},
                    {'name': {'en': 'Iowa', 'ru': 'Айова', 'ky': 'Айова'}},
                    {'name': {'en': 'Kansas', 'ru': 'Канзас', 'ky': 'Канзас'}},
                    {'name': {'en': 'Kentucky', 'ru': 'Кентукки', 'ky': 'Кентукки'}},
                    {'name': {'en': 'Louisiana', 'ru': 'Луизиана', 'ky': 'Луизиана'}},
                    {'name': {'en': 'Maine', 'ru': 'Мэн', 'ky': 'Мэн'}},
                    {'name': {'en': 'Maryland', 'ru': 'Мэриленд', 'ky': 'Мэриленд'}},
                    {'name': {'en': 'Massachusetts', 'ru': 'Массачусетс', 'ky': 'Массачусетс'}},
                    {'name': {'en': 'Michigan', 'ru': 'Мичиган', 'ky': 'Мичиган'}},
                    {'name': {'en': 'Minnesota', 'ru': 'Миннесота', 'ky': 'Миннесота'}},
                    {'name': {'en': 'Mississippi', 'ru': 'Миссисипи', 'ky': 'Миссисипи'}},
                    {'name': {'en': 'Missouri', 'ru': 'Миссури', 'ky': 'Миссури'}},
                    {'name': {'en': 'Montana', 'ru': 'Монтана', 'ky': 'Монтана'}},
                    {'name': {'en': 'Nebraska', 'ru': 'Небраска', 'ky': 'Небраска'}},
                    {'name': {'en': 'Nevada', 'ru': 'Невада', 'ky': 'Невада'}},
                    {'name': {'en': 'New Hampshire', 'ru': 'Нью-Гэмпшир', 'ky': 'Нью-Гэмпшир'}},
                    {'name': {'en': 'New Jersey', 'ru': 'Нью-Джерси', 'ky': 'Нью-Джерси'}},
                    {'name': {'en': 'New Mexico', 'ru': 'Нью-Мексико', 'ky': 'Нью-Мексико'}},
                    {'name': {'en': 'New York', 'ru': 'Нью-Йорк', 'ky': 'Нью-Йорк'}},
                    {'name': {'en': 'North Carolina', 'ru': 'Северная Каролина', 'ky': 'Түндүк Каролина'}},
                    {'name': {'en': 'North Dakota', 'ru': 'Северная Дакота', 'ky': 'Түндүк Дакота'}},
                    {'name': {'en': 'Ohio', 'ru': 'Огайо', 'ky': 'Огайо'}},
                    {'name': {'en': 'Oklahoma', 'ru': 'Оклахома', 'ky': 'Оклахома'}},
                    {'name': {'en': 'Oregon', 'ru': 'Орегон', 'ky': 'Орегон'}},
                    {'name': {'en': 'Pennsylvania', 'ru': 'Пенсильвания', 'ky': 'Пенсильвания'}},
                    {'name': {'en': 'Rhode Island', 'ru': 'Род-Айленд', 'ky': 'Род-Айленд'}},
                    {'name': {'en': 'South Carolina', 'ru': 'Южная Каролина', 'ky': 'Түштүк Каролина'}},
                    {'name': {'en': 'South Dakota', 'ru': 'Южная Дакота', 'ky': 'Түштүк Дакота'}},
                    {'name': {'en': 'Tennessee', 'ru': 'Теннесси', 'ky': 'Теннесси'}},
                    {'name': {'en': 'Texas', 'ru': 'Техас', 'ky': 'Техас'}},
                    {'name': {'en': 'Utah', 'ru': 'Юта', 'ky': 'Юта'}},
                    {'name': {'en': 'Vermont', 'ru': 'Вермонт', 'ky': 'Вермонт'}},
                    {'name': {'en': 'Virginia', 'ru': 'Виргиния', 'ky': 'Виргиния'}},
                    {'name': {'en': 'Washington', 'ru': 'Вашингтон', 'ky': 'Вашингтон'}},
                    {'name': {'en': 'West Virginia', 'ru': 'Западная Виргиния', 'ky': 'Батыш Виргиния'}},
                    {'name': {'en': 'Wisconsin', 'ru': 'Висконсин', 'ky': 'Висконсин'}},
                    {'name': {'en': 'Wyoming', 'ru': 'Вайоминг', 'ky': 'Вайоминг'}},
                ]
            },
            'Kyrgyzstan': {
                'code': 'KG',
                'translations': {
                    'en': 'Kyrgyzstan',
                    'ru': 'Кыргызстан',
                    'ky': 'Кыргызстан'
                },
                'region_type': 'Oblast',
                'regions': [
                    {'name': {'en': 'Batken Region', 'ru': 'Баткенская область', 'ky': 'Баткен областы'}},
                    {'name': {'en': 'Chuy Region', 'ru': 'Чуйская область', 'ky': 'Чүй областы'}},
                    {'name': {'en': 'Issyk-Kul Region', 'ru': 'Иссык-Кульская область', 'ky': 'Ысык-Көл областы'}},
                    {'name': {'en': 'Jalal-Abad Region', 'ru': 'Джалал-Абадская область', 'ky': 'Жалал-Абад областы'}},
                    {'name': {'en': 'Naryn Region', 'ru': 'Нарынская область', 'ky': 'Нарын областы'}},
                    {'name': {'en': 'Osh Region', 'ru': 'Ошская область', 'ky': 'Ош областы'}},
                    {'name': {'en': 'Talas Region', 'ru': 'Таласская область', 'ky': 'Талас областы'}},
                    {'name': {'en': 'Bishkek City', 'ru': 'город Бишкек', 'ky': 'Бишкек шаары'}},
                    {'name': {'en': 'Osh City', 'ru': 'город Ош', 'ky': 'Ош шаары'}},
                ]
            },
            'Uzbekistan': {
                'code': 'UZ',
                'translations': {
                    'en': 'Uzbekistan',
                    'ru': 'Узбекистан',
                    'ky': 'Өзбекстан'
                },
                'region_type': 'Region',
                'regions': [
                    {'name': {'en': 'Andijan Region', 'ru': 'Андижанская область', 'ky': 'Андижан областы'}},
                    {'name': {'en': 'Bukhara Region', 'ru': 'Бухарская область', 'ky': 'Бухара областы'}},
                    {'name': {'en': 'Fergana Region', 'ru': 'Ферганская область', 'ky': 'Фергана областы'}},
                    {'name': {'en': 'Jizzakh Region', 'ru': 'Джизакская область', 'ky': 'Жиззах областы'}},
                    {'name': {'en': 'Kashkadarya Region', 'ru': 'Кашкадарьинская область', 'ky': 'Кашкадария областы'}},
                    {'name': {'en': 'Khorezm Region', 'ru': 'Хорезмская область', 'ky': 'Хорезм областы'}},
                    {'name': {'en': 'Namangan Region', 'ru': 'Наманганская область', 'ky': 'Наманган областы'}},
                    {'name': {'en': 'Navoiy Region', 'ru': 'Навоийская область', 'ky': 'Навоий областы'}},
                    {'name': {'en': 'Samarkand Region', 'ru': 'Самаркандская область', 'ky': 'Самарканд областы'}},
                    {'name': {'en': 'Sirdaryo Region', 'ru': 'Сырдарьинская область', 'ky': 'Сырдария областы'}},
                    {'name': {'en': 'Surkhandarya Region', 'ru': 'Сурхандарьинская область', 'ky': 'Сурхандария областы'}},
                    {'name': {'en': 'Tashkent Region', 'ru': 'Ташкентская область', 'ky': 'Ташкент областы'}},
                    {'name': {'en': 'Tashkent City', 'ru': 'город Ташкент', 'ky': 'Ташкент шаары'}},
                    {'name': {'en': 'Karakalpakstan', 'ru': 'Каракалпакстан', 'ky': 'Каракалпакстан'}},
                ]
            },
            'Tajikistan': {
                'code': 'TJ',
                'translations': {
                    'en': 'Tajikistan',
                    'ru': 'Таджикистан',
                    'ky': 'Тажикстан'
                },
                'region_type': 'Region',
                'regions': [
                    {'name': {'en': 'Dushanbe', 'ru': 'Душанбе', 'ky': 'Душанбе'}},
                    {'name': {'en': 'Gorno-Badakhshan', 'ru': 'Горно-Бадахшанская область', 'ky': 'Горно-Бадахшан областы'}},
                    {'name': {'en': 'Khatlon Region', 'ru': 'Хатлонская область', 'ky': 'Хатлон областы'}},
                    {'name': {'en': 'Sughd Region', 'ru': 'Согдийская область', 'ky': 'Согд областы'}},
                    {'name': {'en': 'Districts of Republican Subordination', 'ru': 'Районы республиканского подчинения', 'ky': 'Республикалык баш ийүүдөгү райондор'}},
                ]
            },
            'Russia': {
                'code': 'RU',
                'translations': {
                    'en': 'Russia',
                    'ru': 'Россия',
                    'ky': 'Россия'
                },
                'region_type': 'Federal Subject',
                'regions': [
                    {'name': {'en': 'Moscow', 'ru': 'Москва', 'ky': 'Москва'}},
                    {'name': {'en': 'Saint Petersburg', 'ru': 'Санкт-Петербург', 'ky': 'Санкт-Петербург'}},
                    {'name': {'en': 'Moscow Oblast', 'ru': 'Московская область', 'ky': 'Москва областы'}},
                    {'name': {'en': 'Krasnodar Krai', 'ru': 'Краснодарский край', 'ky': 'Краснодар крайы'}},
                    {'name': {'en': 'Sverdlovsk Oblast', 'ru': 'Свердловская область', 'ky': 'Свердловск областы'}},
                    {'name': {'en': 'Rostov Oblast', 'ru': 'Ростовская область', 'ky': 'Ростов областы'}},
                    {'name': {'en': 'Tatarstan', 'ru': 'Татарстан', 'ky': 'Татарстан'}},
                    {'name': {'en': 'Bashkortostan', 'ru': 'Башкортостан', 'ky': 'Башкортостан'}},
                    {'name': {'en': 'Chelyabinsk Oblast', 'ru': 'Челябинская область', 'ky': 'Челябинск областы'}},
                    {'name': {'en': 'Nizhny Novgorod Oblast', 'ru': 'Нижегородская область', 'ky': 'Нижний Новгород областы'}},
                    {'name': {'en': 'Samara Oblast', 'ru': 'Самарская область', 'ky': 'Самара областы'}},
                    {'name': {'en': 'Omsk Oblast', 'ru': 'Омская область', 'ky': 'Омск областы'}},
                    {'name': {'en': 'Kemerovo Oblast', 'ru': 'Кемеровская область', 'ky': 'Кемерово областы'}},
                    {'name': {'en': 'Volgograd Oblast', 'ru': 'Волгоградская область', 'ky': 'Волгоград областы'}},
                    {'name': {'en': 'Novosibirsk Oblast', 'ru': 'Новосибирская область', 'ky': 'Новосибирск областы'}},
                    {'name': {'en': 'Perm Krai', 'ru': 'Пермский край', 'ky': 'Пермь крайы'}},
                    {'name': {'en': 'Voronezh Oblast', 'ru': 'Воронежская область', 'ky': 'Воронеж областы'}},
                    {'name': {'en': 'Saratov Oblast', 'ru': 'Саратовская область', 'ky': 'Саратов областы'}},
                    {'name': {'en': 'Krasnoyarsk Krai', 'ru': 'Красноярский край', 'ky': 'Красноярск крайы'}},
                    {'name': {'en': 'Tyumen Oblast', 'ru': 'Тюменская область', 'ky': 'Тюмень областы'}},
                ]
            }
        }
        
        # Create countries and regions
        for country_key, country_data in countries_data.items():
            # Create country with translations
            country, created = Country.objects.get_or_create(
                code=country_data['code'],
                defaults={
                    'name': country_data['translations']['en'],
                    'name_en': country_data['translations']['en'],
                    'name_ru': country_data['translations']['ru'],
                    'name_ky': country_data['translations']['ky']
                }
            )
            if created:
                self.stdout.write(f'Created country: {country.name}')
            else:
                # Update existing country with translations
                country.name_en = country_data['translations']['en']
                country.name_ru = country_data['translations']['ru']
                country.name_ky = country_data['translations']['ky']
                country.save()
                self.stdout.write(f'Updated country: {country.name}')
            
            # Create regions for this country
            for region_data in country_data['regions']:
                region_name = region_data['name']['en']  # Use English as default
                region, created = Region.objects.get_or_create(
                    country=country,
                    name=region_name,
                    defaults={
                        'type_name': country_data['region_type'],
                        'name_en': region_data['name']['en'],
                        'name_ru': region_data['name']['ru'],
                        'name_ky': region_data['name']['ky']
                    }
                )
                if created:
                    self.stdout.write(f'  Created region: {region.name}')
                else:
                    # Update existing region with translations
                    region.name_en = region_data['name']['en']
                    region.name_ru = region_data['name']['ru']
                    region.name_ky = region_data['name']['ky']
                    region.save()
                    self.stdout.write(f'  Updated region: {region.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated countries and regions!')
        )