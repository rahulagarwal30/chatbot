// Enable pusher logging - don't include this in production
Pusher.logToConsole = true;

var pusher_subscriber = new Pusher('7ee8ea85e9273be48499', {
    cluster: 'ap2'
});

var channel = pusher_subscriber.subscribe('my-channel');

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.querySelector('.chat-messages');
    const messageInput = document.getElementById('message-input');
    
    // Focus input field when page loads
    messageInput.focus();
    
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
        
        // Clear input and refocus
        input.value = '';
        input.focus();
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}
