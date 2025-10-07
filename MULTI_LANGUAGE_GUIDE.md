# Multi-Language Blog Post Guide

## 🌍 Multi-Language HTML File Upload Feature

This feature allows you to upload different HTML files for different language versions of your blog posts. The system supports:

- **English (en)** - Default language
- **Russian (ru)** - Русский язык  
- **Kyrgyz (ky)** - Кыргыз тили

## 📝 How to Use

### 1. Create Your Content
Create separate HTML files for each language version of your blog post. Each file should be complete and self-contained.

**Example file structure:**
```
my_post_en.html  (English version)
my_post_ru.html  (Russian version)
my_post_ky.html  (Kyrgyz version)
```

### 2. Upload in Django Admin

1. **Go to Blog Post Admin**: `/admin/forum/blogpost/add/`

2. **Fill Basic Information**:
   - Title (main/default)
   - Slug (URL identifier)

3. **Multi-language Titles & Descriptions** (Optional):
   - `title_en`, `title_ru`, `title_ky`
   - `short_description_en`, `short_description_ru`, `short_description_ky`

4. **HTML File Uploads** (Recommended):
   - `html_file` - Default/English version
   - `html_file_en` - Specific English version (if different from default)
   - `html_file_ru` - Russian version
   - `html_file_ky` - Kyrgyz version

5. **Rich Text Editor** (Alternative):
   - Use if you don't have HTML files
   - Supports `content`, `content_en`, `content_ru`, `content_ky`

### 3. Language Detection

The system automatically detects the user's language from:
1. URL path (`/en/`, `/ru/`, `/ky/`)
2. Request language code
3. Falls back to English if none detected

### 4. Content Rendering Priority

For each language, the system uses this priority:
1. **HTML File** for that language (e.g., `html_file_ru` for Russian)
2. **Rich Text Content** for that language (e.g., `content_ru`)
3. **Default content** (fallback)

## 🎯 Best Practices

### HTML File Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Post Title</title>
    <style>
        /* Include your styles here */
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        h1 { color: #2c5530; }
        .tip { background: #f0f8f0; padding: 15px; }
    </style>
</head>
<body>
    <h1>Your Main Heading</h1>
    <p>Your content here...</p>
</body>
</html>
```

### CSS Styling Guidelines
- Use inline styles or `<style>` tags within HTML files
- Follow agricultural/farming color scheme (greens, earth tones)
- Ensure responsive design for mobile devices
- Include proper typography for readability

### Content Guidelines
- **English**: Technical agricultural terms, modern farming practices
- **Russian**: Accessible language for Central Asian farmers
- **Kyrgyz**: Local terminology and culturally relevant examples

## 🔧 Technical Details

### Model Fields Created
- `html_file_en` - English HTML file
- `html_file_ru` - Russian HTML file  
- `html_file_ky` - Kyrgyz HTML file

### Template Tags Available
- `{% render_blog_content_with_language post %}` - Auto-detects language
- `{{ post|render_blog_content:"ru" }}` - Specific language
- `{{ post|get_title_for_language:"ky" }}` - Language-specific title
- `{{ post|get_description_for_language:"en" }}` - Language-specific description

### Model Methods
- `post.get_html_file_for_language('ru')` - Get HTML file for language
- `post.has_translation('ky')` - Check if translation exists
- `post.get_title_for_language('en')` - Get title for language

## 📁 Example Files

See the `test_html_files/` directory for complete examples:
- `farming_tips_en.html` - English agricultural tips
- `farming_tips_ru.html` - Russian version (Русский)
- `farming_tips_ky.html` - Kyrgyz version (Кыргызча)

## 🚀 Getting Started

1. **Test with provided examples**: Upload the sample HTML files to see how it works
2. **Create your first post**: Start with one language, then add translations
3. **Use the rich text editor**: For simple posts without complex formatting
4. **Scale up**: Create comprehensive multi-language agricultural content

## 💡 Tips for Agricultural Content

### English Content
- Focus on modern farming techniques
- Include scientific terminology
- Reference international best practices

### Russian Content  
- Use familiar agricultural terms
- Include Soviet-era farming knowledge where relevant
- Focus on climate-appropriate techniques for Central Asia

### Kyrgyz Content
- Include traditional farming wisdom
- Use local plant and animal names
- Reference local climate and geography

This multi-language system enables you to reach farmers across Central Asia in their native languages, making agricultural knowledge more accessible and actionable.