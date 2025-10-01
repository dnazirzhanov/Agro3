import { useState } from 'react'
import { Editor } from 'novel'
import './App.css'
import './novel-editor.css'

function App() {
  const [content, setContent] = useState('')
  const [title, setTitle] = useState('')

    const handleSave = () => {
    // Get CSRF token and URLs from Django template
    const csrfToken = window.CSRF_TOKEN || 
                     document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                     document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
    
    const saveUrl = window.DJANGO_URLS?.savePost || '/forum/save-novel-post/'
    
    // Validate required fields
    if (!title.trim()) {
      alert('🌾 Please enter a title for your agricultural story!')
      return
    }
    
    if (!content || content === '""' || content === 'null') {
      alert('🌱 Please add some content to your blog post!')
      return
    }
    
    // Show saving indicator
    const saveButton = document.querySelector('[data-save-button]')
    if (saveButton) {
      saveButton.disabled = true
      saveButton.innerHTML = '💾 Saving...'
    }
    
    fetch(saveUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        title: title.trim(),
        content: content
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      return response.json()
    })
    .then(data => {
      if (data.success) {
        alert('🎉 Your agricultural story has been published successfully!')
        // Redirect to the blog post
        window.location.href = data.redirect_url || (window.DJANGO_URLS?.blogIndex || '/forum/')
      } else {
        alert('❌ Error saving post: ' + (data.error || 'Unknown error'))
      }
    })
    .catch(error => {
      console.error('Save Error:', error)
      alert('❌ Error saving post: ' + error.message)
    })
    .finally(() => {
      // Reset save button
      if (saveButton) {
        saveButton.disabled = false
        saveButton.innerHTML = '🚀 Publish Post'
      }
    })
  }

  return (
    <div className="agricultural-theme min-h-screen" style={{ backgroundColor: '#f8fafc' }}>
      <div className="max-w-5xl mx-auto">
        {/* Enhanced Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
          <div className="px-6 py-4">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900" style={{ fontFamily: 'Inter, sans-serif' }}>
                  🌾 Agricultural Blog Studio
                </h1>
                <p className="text-gray-600 mt-1">Create engaging agricultural content with Notion-like editing</p>
              </div>
              <div className="flex gap-3">
                <button 
                  onClick={() => window.history.back()}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors rounded-lg hover:bg-gray-100"
                >
                  ← Cancel
                </button>
                <button 
                  onClick={() => {
                    setTitle('')
                    setContent('')
                  }}
                  className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-medium"
                >
                  🗑️ Clear
                </button>
                <button 
                  onClick={handleSave}
                  data-save-button
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium shadow-sm"
                >
                  🚀 Publish Post
                </button>
              </div>
            </div>
            
            {/* Enhanced Title Input */}
            <input
              type="text"
              placeholder="🌱 Enter your story title..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full text-4xl font-bold border-none outline-none resize-none bg-transparent placeholder-gray-400 text-gray-900 py-3 px-2"
              style={{ 
                fontFamily: 'Inter, sans-serif',
                textAlign: 'center'
              }}
            />
          </div>
        </header>

        {/* Enhanced Novel Editor Container */}
        <main className="px-6 py-8">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden" style={{ minHeight: '700px' }}>
            <Editor
              className="novel-editor"
              defaultValue=""
              onUpdate={(editor) => {
                const json = editor?.getJSON()
                setContent(JSON.stringify(json))
              }}
              onDebouncedUpdate={(editor) => {
                const json = editor?.getJSON()
                setContent(JSON.stringify(json))
              }}
              storageKey="agro3-agricultural-blog-draft"
              completionApi="/api/generate"
              extensions={[]}
              editorProps={{
                attributes: {
                  class: 'novel-editor-content focus:outline-none',
                },
                handleDOMEvents: {
                  keydown: () => false,
                },
              }}
            />
          </div>

          {/* Enhanced Footer with Tips */}
          <div className="mt-8 bg-green-50 rounded-xl p-6 border border-green-200">
            <h3 className="text-lg font-semibold text-green-800 mb-4">📝 Editing Tips</h3>
            <div className="grid md:grid-cols-2 gap-4 text-sm text-green-700">
              <div>
                <p><strong>💬 Commands:</strong> Type <code className="bg-green-100 px-2 py-1 rounded">/</code> for slash commands</p>
                <p><strong>🖼️ Images:</strong> Drag & drop or paste image URLs</p>
              </div>
              <div>
                <p><strong>🎥 Videos:</strong> Paste YouTube links for embedded videos</p>
                <p><strong>� Tables:</strong> Use <code className="bg-green-100 px-2 py-1 rounded">/table</code> for data presentation</p>
              </div>
            </div>
          </div>

          {/* Development Debug Panel */}
          <div className="mt-6 bg-blue-50 rounded-xl p-4 border border-blue-200">
            <details className="cursor-pointer">
              <summary className="font-medium text-blue-800 select-none">🔧 Developer Tools</summary>
              <div className="mt-3 space-y-2">
                <button
                  onClick={() => {
                    console.log('=== AGRICULTURAL BLOG DEBUG ===')
                    console.log('Title:', title)
                    console.log('Content JSON:', content)
                    console.log('Content Length:', content.length)
                    alert('Content logged to browser console! Open Developer Tools (F12) to view.')
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  🔍 Debug Content
                </button>
              </div>
            </details>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
