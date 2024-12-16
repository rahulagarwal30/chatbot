// Enable pusher logging - don't include this in production
Pusher.logToConsole = true;

var pusher_subscriber = new Pusher('7ee8ea85e9273be48499', {
    cluster: 'ap2'
});

var channel = pusher_subscriber.subscribe('my-channel');

// Variables for pull to refresh
let touchStart = 0;
let touchEnd = 0;
const REFRESH_THRESHOLD = 150;
let isRefreshing = false;

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
        initialMessage.textContent = "Hey there! How can I assist you today?";
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

    messagesContainer.addEventListener('touchend', function() {
        if (isRefreshing) return;
        
        const distance = touchEnd - touchStart;
        
        if (messagesContainer.scrollTop === 0 && distance > REFRESH_THRESHOLD) {
            isRefreshing = true;
            messagesContainer.classList.add('refreshing');
            
            // Perform refresh
            window.location.reload();
        } else {
            messagesContainer.classList.remove('pull-to-refresh');
        }
        
        touchStart = 0;
        touchEnd = 0;
    }, { passive: true });
    
    channel.bind('event-bot-response', function(data) {
        // Create new message element
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'received');
        messageElement.textContent = data.message || JSON.stringify(data);
        
        // Add message to container
        messagesContainer.appendChild(messageElement);
        
        // Scroll to bottom
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

function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (message) {
        // Create new message element
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'sent');
        messageElement.textContent = message;
        
        // Add message to container
        const messagesContainer = document.querySelector('.chat-messages');
        messagesContainer.appendChild(messageElement);
        
        // Send message to search endpoint
        fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        // Clear input
        input.value = '';
        
        // Close keyboard on mobile
        input.blur();
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}
