/**
 * Simple Rich Text Editor JavaScript
 * Clean, modern rich text editing without complex dependencies
 * Based on Django Girls best practices
 */

(function() {
    'use strict';

    function initSimpleRichText() {
        const textareas = document.querySelectorAll('.simple-rich-text');
        
        textareas.forEach(function(textarea) {
            if (textarea.dataset.richTextInit) return;
            textarea.dataset.richTextInit = 'true';
            
            // Create toolbar
            const toolbar = createToolbar();
            textarea.parentNode.insertBefore(toolbar, textarea);
            
            // Style the textarea
            textarea.style.borderTopLeftRadius = '0';
            textarea.style.borderTopRightRadius = '0';
            
            // Add content editing features
            setupContentEditing(textarea);
        });
    }

    function createToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'rich-text-toolbar';
        
        const buttons = [
            { command: 'bold', label: 'B', title: 'Bold (Ctrl+B)' },
            { command: 'italic', label: 'I', title: 'Italic (Ctrl+I)' },
            { command: 'underline', label: 'U', title: 'Underline (Ctrl+U)' },
            { separator: true },
            { command: 'formatBlock', value: 'h2', label: 'H2', title: 'Heading 2' },
            { command: 'formatBlock', value: 'h3', label: 'H3', title: 'Heading 3' },
            { command: 'formatBlock', value: 'p', label: 'P', title: 'Paragraph' },
            { separator: true },
            { command: 'insertUnorderedList', label: '•', title: 'Bullet List' },
            { command: 'insertOrderedList', label: '1.', title: 'Numbered List' },
            { separator: true },
            { command: 'createLink', label: 'Link', title: 'Insert Link' },
            { command: 'insertImage', label: 'Img', title: 'Insert Image' },
            { separator: true },
            { command: 'formatBlock', value: 'blockquote', label: '"', title: 'Quote' },
            { command: 'removeFormat', label: 'Clear', title: 'Remove Formatting' }
        ];

        buttons.forEach(function(btn) {
            if (btn.separator) {
                const sep = document.createElement('div');
                sep.className = 'rich-text-separator';
                toolbar.appendChild(sep);
            } else {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'rich-text-btn';
                button.innerHTML = btn.label;
                button.title = btn.title;
                
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    executeCommand(btn.command, btn.value);
                });
                
                toolbar.appendChild(button);
            }
        });

        return toolbar;
    }

    function setupContentEditing(textarea) {
        // Add paste handling for rich content
        textarea.addEventListener('paste', function(e) {
            // Allow default paste behavior but clean up afterwards
            setTimeout(function() {
                cleanupContent(textarea);
            }, 10);
        });

        // Add keyboard shortcuts
        textarea.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key.toLowerCase()) {
                    case 'b':
                        e.preventDefault();
                        insertAtCursor(textarea, '<strong>', '</strong>');
                        break;
                    case 'i':
                        e.preventDefault();
                        insertAtCursor(textarea, '<em>', '</em>');
                        break;
                }
            }
        });
    }

    function executeCommand(command, value) {
        const textarea = document.activeElement;
        if (!textarea || !textarea.classList.contains('simple-rich-text')) return;

        switch(command) {
            case 'bold':
                insertAtCursor(textarea, '<strong>', '</strong>');
                break;
            case 'italic':
                insertAtCursor(textarea, '<em>', '</em>');
                break;
            case 'underline':
                insertAtCursor(textarea, '<u>', '</u>');
                break;
            case 'formatBlock':
                if (value === 'h2') insertAtCursor(textarea, '<h2>', '</h2>');
                else if (value === 'h3') insertAtCursor(textarea, '<h3>', '</h3>');
                else if (value === 'blockquote') insertAtCursor(textarea, '<blockquote>', '</blockquote>');
                else if (value === 'p') insertAtCursor(textarea, '<p>', '</p>');
                break;
            case 'insertUnorderedList':
                insertAtCursor(textarea, '<ul><li>', '</li></ul>');
                break;
            case 'insertOrderedList':
                insertAtCursor(textarea, '<ol><li>', '</li></ol>');
                break;
            case 'createLink':
                const url = prompt('Enter URL:');
                if (url) insertAtCursor(textarea, `<a href="${url}">`, '</a>');
                break;
            case 'insertImage':
                const imgUrl = prompt('Enter image URL:');
                if (imgUrl) insertAtCursor(textarea, `<img src="${imgUrl}" alt="Image" />`, '');
                break;
            case 'removeFormat':
                // Simple cleanup - remove common tags
                const selection = getSelection(textarea);
                if (selection) {
                    const cleaned = selection.replace(/<[^>]*>/g, '');
                    replaceSelection(textarea, cleaned);
                }
                break;
        }
    }

    function insertAtCursor(textarea, openTag, closeTag) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selection = textarea.value.substring(start, end);
        
        const replacement = openTag + selection + closeTag;
        textarea.value = textarea.value.substring(0, start) + replacement + textarea.value.substring(end);
        
        // Move cursor to end of inserted content
        const newPos = start + replacement.length;
        textarea.setSelectionRange(newPos, newPos);
        textarea.focus();
    }

    function getSelection(textarea) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        return textarea.value.substring(start, end);
    }

    function replaceSelection(textarea, replacement) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        textarea.value = textarea.value.substring(0, start) + replacement + textarea.value.substring(end);
        textarea.setSelectionRange(start, start + replacement.length);
    }

    function cleanupContent(textarea) {
        // Basic cleanup of pasted content
        let content = textarea.value;
        
        // Remove style attributes
        content = content.replace(/style="[^"]*"/gi, '');
        
        // Remove class attributes except our own
        content = content.replace(/class="[^"]*"/gi, '');
        
        // Remove id attributes
        content = content.replace(/id="[^"]*"/gi, '');
        
        // Clean up Microsoft Word artifacts
        content = content.replace(/<o:p[^>]*>.*?<\/o:p>/gi, '');
        content = content.replace(/<span[^>]*>(\s*)<\/span>/gi, '$1');
        
        textarea.value = content;
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSimpleRichText);
    } else {
        initSimpleRichText();
    }

    // Re-initialize when new textareas are added (for Django admin inlines)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const textareas = node.querySelectorAll('.simple-rich-text');
                        if (textareas.length > 0) {
                            initSimpleRichText();
                        }
                    }
                });
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

})();