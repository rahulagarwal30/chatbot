// Enable pusher logging - don't include this in production
//Pusher.logToConsole = true;

var pusher_subscriber = new Pusher('7ee8ea85e9273be48499', {
    cluster: 'ap2'
});

// Get channel name from server or use default
const channelName = window.PUSHER_CHANNEL || 'dev-channel';
console.log('Subscribing to Pusher channel:', channelName);
var channel = pusher_subscriber.subscribe(channelName);

// Variables for pull to refresh
let touchStart = 0;
let touchEnd = 0;
const REFRESH_THRESHOLD = 150;
let isRefreshing = false;

// Add at the top of the file
function markdownToHtml(text) {
    return text
        // Code blocks with language
        .replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => 
            `<pre><code class="language-${lang || ''}">${code.trim()}</code></pre>`)
        // Inline code
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // Headers
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        // Bold
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        // Italic
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
        // Links
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
        // Unordered lists
        .replace(/^\s*[-*+]\s+(.+)/gm, '<li>$1</li>')
        .split(/(?:\r?\n){2,}/)
        .map(para => {
            if (para.startsWith('<li>')) {
                return `<ul>${para}</ul>`;
            }
            if (para.startsWith('<h')) {
                return para;
            }
            return `<p>${para}</p>`;
        })
        .join('\n');
}

// Add this function before the DOMContentLoaded event listener
function getTimeBasedGreeting() {
    const hour = new Date().getHours();
    
    if (hour >= 5 && hour < 12) {
        return "Good morning";
    } else if (hour >= 12 && hour < 17) {
        return "Good afternoon";
    } else {
        return "Good evening";
    }
}

// Add this at the beginning of your chat.js file
function getDeviceId() {
    let deviceId = localStorage.getItem('deviceId');
    if (!deviceId) {
        deviceId = 'device_' + Math.random().toString(36).slice(2, 11);
        localStorage.setItem('deviceId', deviceId);
    }
    return deviceId;
}

// Add this function at the top with other function declarations
async function clearSession() {
    try {
        await fetch('/clear_session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
    } catch (error) {
        console.error('Error clearing session:', error);
    }
}

// Add event listener for page refresh/unload
window.addEventListener('beforeunload', async (event) => {
    await clearSession();
});

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.querySelector('.chat-messages');
    const messageInput = document.getElementById('message-input');
    
    // Clear any existing messages
    messagesContainer.innerHTML = '';
    
    // Add initial bot message with a slight delay to ensure proper rendering
    setTimeout(() => {
        const initialMessage = document.createElement('div');
        initialMessage.classList.add('message', 'received', 'initial-message');
        initialMessage.textContent = `${getTimeBasedGreeting()}! How can I assist you today?`;
        messagesContainer.appendChild(initialMessage);
        
        // Ensure initial message is visible
        messagesContainer.scrollTop = 0;
    }, 100);
    
    // Add pull to refresh handlers
    messagesContainer.addEventListener('touchstart', function(e) {
        touchStart = e.touches[0].clientY;
    }, { passive: true });

    messagesContainer.addEventListener('touchmove', function(e) {
        if (isRefreshing) return;
        
        touchEnd = e.touches[0].clientY;
        const distance = touchEnd - touchStart;
        
        // Only allow pull to refresh when at top of container
        if (messagesContainer.scrollTop === 0 && distance > 0) {
            // Add visual feedback class if past threshold
            if (distance > REFRESH_THRESHOLD) {
                messagesContainer.classList.add('pull-to-refresh');
            } else {
                messagesContainer.classList.remove('pull-to-refresh');
            }
        }
    }, { passive: true });

    messagesContainer.addEventListener('touchend', async function() {
        if (isRefreshing) return;
        
        const distance = touchEnd - touchStart;
        
        if (messagesContainer.scrollTop === 0 && distance > REFRESH_THRESHOLD) {
            isRefreshing = true;
            messagesContainer.classList.add('refreshing');
            
            try {
                await clearSession();
                window.location.reload();
            } catch (error) {
                console.error('Error during refresh:', error);
                window.location.reload();
            }
        } else {
            messagesContainer.classList.remove('pull-to-refresh');
        }
        
        touchStart = 0;
        touchEnd = 0;
    }, { passive: true });
    
    channel.bind('event-bot-response', function(data) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'received');
        
        // Convert markdown to HTML
        const messageText = data.message || JSON.stringify(data);
        messageElement.innerHTML = markdownToHtml(messageText);
        
        const messagesContainer = document.querySelector('.chat-messages');
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });

    // Handle send button click
    document.getElementById('send-button').addEventListener('click', sendMessage);
    
    // Handle enter key press
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Focus input field after a slight delay to prevent mobile keyboard from affecting layout
    setTimeout(() => {
        messageInput.focus();
    }, 300);
});

// Update your message sending function to include the device ID
async function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (!message) return;  // Don't send empty messages
    
    try {
        // Add user message to chat immediately
        addMessageToChat('sent', message);
        
        // Clear input right after sending
        messageInput.value = '';
        
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Device-ID': getDeviceId()
            },
            body: JSON.stringify({ message: message })
        });
        
        // Log response details for debugging
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server response:', errorText);
            throw new Error(`Server error: ${response.status} - ${errorText}`);
        }
        
        // Wait for the bot response to come through Pusher
        
    } catch (error) {
        console.error('Full error details:', error);
        addMessageToChat('received', 'Sorry, there was an error processing your message. Please try again.');
    }
}

function addMessageToChat(type, message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', type);
    
    // Convert markdown to HTML for received messages
    if (type === 'received') {
        messageElement.innerHTML = markdownToHtml(message);
    } else {
        messageElement.textContent = message;
    }
    
    const messagesContainer = document.querySelector('.chat-messages');
    messagesContainer.appendChild(messageElement);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}
