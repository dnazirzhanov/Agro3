import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Mount React app to Django template div or fallback to default root
const rootElement = document.getElementById('novel-editor-root') || document.getElementById('root')
createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
