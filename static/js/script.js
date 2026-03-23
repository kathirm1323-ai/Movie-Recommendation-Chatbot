document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    const escapeHtml = (unsafe) => {
        return String(unsafe)
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    };

    const renderRichText = (text) => {
        const escaped = escapeHtml(text);
        return escaped
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
    };

    const addMessage = (text, isUser = false, movies = []) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        let movieHtml = '';
        if (movies.length > 0) {
            movieHtml = `<div class="movie-results">
                ${movies.map(m => `
                    ${(() => {
                        const title = escapeHtml(m.title ?? '');
                        const genre = escapeHtml(m.genre ?? '');
                        const rating = escapeHtml(m.rating ?? '');
                        const description = escapeHtml(m.description ?? '');
                        const imdbLink = escapeHtml(m.link ?? '#');

                        const rawPoster = typeof m.poster === 'string' ? m.poster.trim() : '';
                        const fallbackPoster = `/static/img/poster-placeholder.svg`;
                        const poster = rawPoster || fallbackPoster;

                        return `
                    <div class="movie-card">
                        <div class="poster-box">
                            <img
                                class="poster-img"
                                src="${poster}"
                                alt="${title}"
                                loading="lazy"
                                referrerpolicy="no-referrer"
                                onerror="this.onerror=null;this.src='${fallbackPoster}';"
                            >
                        </div>
                        <div class="movie-info">
                            <h4>${title}</h4>
                            <div class="meta">
                                <span>${genre}</span>
                                <span class="rating">★ ${rating}</span>
                            </div>
                            <p>${description}</p>
                            <div class="action-row">
                                <a
                                    href="https://www.google.com/search?q=${encodeURIComponent(`watch ${m.title || ''} online`)}"
                                    class="action-btn secondary"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >Watch</a>
                                <a href="${imdbLink}" class="action-btn primary" target="_blank" rel="noopener noreferrer">View</a>
                            </div>
                        </div>
                    </div>
                        `;
                    })()}
                `).join('')}
            </div>`;
        }

        messageDiv.innerHTML = `
            <div class="bubble">
                ${renderRichText(text)}
                ${movieHtml}
            </div>
        `;
        
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };

    const showTypingIndicator = () => {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="bubble typing">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        `;
        chatWindow.appendChild(typingDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return typingDiv;
    };

    const handleSend = async () => {
        const message = userInput.value.trim();
        if (!message) return;

        // Clear input
        userInput.value = '';
        
        // Add user message to UI
        addMessage(message, true);

        // Show typing indicator
        const typingIndicator = showTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message }),
            });

            const data = await response.json();
            
            // Remove typing indicator after a short delay for realism
            setTimeout(() => {
                typingIndicator.remove();
                addMessage(data.response, false, data.movies);
            }, 800);

        } catch (error) {
            console.error('Error:', error);
            typingIndicator.remove();
            addMessage("Sorry, I'm having trouble connecting to my movie database right now.");
        }
    };

    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });
});
