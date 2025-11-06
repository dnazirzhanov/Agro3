"""
MULTILINGUAL MARKET PRICE MANAGEMENT GUIDE
==========================================

This guide explains how to manage market prices in multiple languages
using the Django Admin interface.

OVERVIEW
--------
The market price system now supports full multilingual functionality:
- Product names, categories, and descriptions in English, Russian, and Kyrgyz
- Market names and descriptions in English, Russian, and Kyrgyz  
- Price notes in English, Russian, and Kyrgyz
- Language-based content filtering for users

HOW TO ADD MULTILINGUAL CONTENT
-------------------------------

1. ADDING PRODUCTS (Admin > Market > Products)
   - English fields are REQUIRED (default/fallback language)
   - Russian and Kyrgyz fields are OPTIONAL but RECOMMENDED
   
   Example:
   - Name (English): "Apples"
   - Name (Russian): "Яблоки" 
   - Name (Kyrgyz): "Алмалар"
   
   - Category (English): "Fruits"
   - Category (Russian): "Фрукты"
   - Category (Kyrgyz): "Жемиштер"

2. ADDING MARKETS (Admin > Market > Markets)
   - English fields are REQUIRED (default/fallback language)
   - Russian and Kyrgyz fields are OPTIONAL but RECOMMENDED
   
   Example:
   - Name (English): "Batken Central Market"
   - Name (Russian): "Баткенский центральный рынок"
   - Name (Kyrgyz): "Баткен борбордук базары"
   
   - Description (English): "Main agricultural market in Batken region"
   - Description (Russian): "Главный сельскохозяйственный рынок Баткенской области"
   - Description (Kyrgyz): "Баткен облусундагы негизги айыл чарба базары"

3. ADDING PRICE ENTRIES (Admin > Market > Market Prices)
   - Select Product and Market (these should already have translations)
   - Enter price, unit, and date
   - Add notes in multiple languages if needed
   
   Notes Example:
   - Notes (English): "High quality, organic produce"
   - Notes (Russian): "Высокое качество, органическая продукция"  
   - Notes (Kyrgyz): "Жогорку сапат, органикалык өнүм"

USER EXPERIENCE
--------------
When users visit the website:
- Russian users (/ru/market/) see only products/markets with Russian translations
- Kyrgyz users (/ky/market/) see only products/markets with Kyrgyz translations  
- English users (/en/market/) see all content (English is fallback)

This ensures users only see content they can understand in their language.

BEST PRACTICES
--------------
1. Always fill in English fields (required for system functionality)
2. Add Russian and Kyrgyz translations for content targeting those users
3. Use consistent terminology across languages
4. Keep product categories simple and translatable
5. Include location information in market descriptions

TECHNICAL NOTES
--------------
- Translation fields are automatically created by django-modeltranslation
- Database stores separate columns for each language (name_en, name_ru, name_ky)
- Frontend automatically filters content based on user's language choice
- Empty translations are hidden from users (they won't see untranslated content)

MIGRATION FROM OLD SYSTEM
------------------------
If you have existing market data:
1. Existing data will appear in English fields automatically
2. Add Russian/Kyrgyz translations by editing existing records
3. Users will only see translated content in their selected language

TROUBLESHOOTING
--------------
- If content doesn't appear for Russian/Kyrgyz users: Check that translations are filled in
- If English content is missing: English is required and should never be empty
- If admin interface looks different: Make sure you're using the correct admin fieldsets

EXAMPLE WORKFLOW
--------------
1. Create Product: "Wheat" (EN) / "Пшеница" (RU) / "Буудай" (KY)
2. Create Market: "Isfana Market" (EN) / "Исфанинский рынок" (RU) / "Исфана базары" (KY)
3. Add Price: 45.50 som/kg with notes in all languages
4. Result: Russian users see "Пшеница" at "Исфанинский рынок" for 45.50 сом/кг

This ensures a fully localized experience for all users while maintaining
administrative control over content quality and translation accuracy.
"""