class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button button'), // Target the button itself
            chatBox: document.querySelector('.chatbox'), // Target the main chatbox container
            sendButton: document.querySelector('.send__button'),
            chatMessages: document.querySelector('.chatbox__messages'), // Cache messages area
            inputField: document.querySelector('.chatbox__footer input') // Cache input field
        };

        if (!this.args.openButton || !this.args.chatBox || !this.args.sendButton || !this.args.chatMessages || !this.args.inputField) {
            console.error("Chatbox initialization failed: One or more required elements not found.");
            return; // Stop initialization if elements are missing
        }

        this.state = false; // Is the chatbox open?
        this.messages = []; // History of messages { name: "User" | "Etheg", message: "text" }
        this.eventSource = null; // Holds the current EventSource object
        this.currentBotMessageElement = null; // Holds the DOM element for the message being streamed
    }

    display() {
        const { openButton, sendButton, inputField, chatBox } = this.args; // Use the chatBox variable

        openButton.addEventListener('click', () => this.toggleState(chatBox)); // Pass the main container
        sendButton.addEventListener('click', () => this.onSendButton());

        inputField.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton();
            }
        });
    }

    toggleState(chatbox) { // This now receives the main chatbox container
        this.state = !this.state;
        // Toggle the class on the main chatbox container
        chatbox.classList.toggle('chatbox--active', this.state);

        // Focus input field when chatbox opens
        if (this.state) {
            // Wait a moment for transition to finish before focusing
            setTimeout(() => {
                 this.args.inputField.focus();
            }, 500); // Match this delay with your CSS transition duration
        }
    }

    onSendButton() {
        const { inputField } = this.args;
        const messageText = inputField.value.trim();

        if (messageText === "") {
            return;
        }

        this.addMessageToChat("User", messageText);
        inputField.value = '';

        this.startStreaming(messageText);
    }

    startStreaming(messageText) {
         if (this.eventSource) {
            this.eventSource.close();
            console.log("Previous EventSource closed.");
         }

        this.currentBotMessageElement = this.createMessageElement("Etheg", "...");
        // Prepend the message element to the messages container
        this.args.chatMessages.prepend(this.currentBotMessageElement); // Use prepend for column-reverse layout
        this.scrollToBottom();

        const encodedMessage = encodeURIComponent(messageText);
        this.eventSource = new EventSource(` /stream?message=${encodedMessage}`);
        console.log(`Connecting to /stream?message=${encodedMessage}`);

        let firstTokenReceived = false;

        this.eventSource.onopen = () => {
            console.log("EventSource connection opened.");
        };

        this.eventSource.onmessage = (event) => {
             if (!firstTokenReceived && this.currentBotMessageElement) {
                 this.currentBotMessageElement.textContent = '';
                 firstTokenReceived = true;
             }

             if (this.currentBotMessageElement) {
                 const decodedToken = event.data.replace(/\\n/g, '\n');
                 this.currentBotMessageElement.textContent += decodedToken;
                 this.scrollToBottom();
             }
        };

        this.eventSource.onerror = (err) => {
            console.error("EventSource failed:", err);

             if (this.currentBotMessageElement && !firstTokenReceived) {
                 this.currentBotMessageElement.textContent = "Sorry, could not get a response.";
             } else if (this.currentBotMessageElement) {
                 // Keep partial response if any
             } else {
                 this.addMessageToChat("Etheg", "Sorry, an error occurred connecting to the server.");
             }

            if (this.eventSource) {
                 this.eventSource.close();
                 console.log("EventSource closed due to error or completion.");
            }
            this.eventSource = null;
            this.currentBotMessageElement = null;
        };
    }

    addMessageToChat(sender, message) {
        this.messages.push({ name: sender, message: message });

        const messageElement = this.createMessageElement(sender, message);
        // Prepend the message element to the messages container
        this.args.chatMessages.prepend(messageElement); // Use prepend for column-reverse layout
        this.scrollToBottom();
    }

    createMessageElement(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('messages__item');
        messageDiv.classList.add(sender === "Etheg" ? 'messages__item--visitor' : 'messages__item--operator');
        messageDiv.textContent = message;
        return messageDiv;
    }

    scrollToBottom() {
        // In column-reverse layout, scrolling to top shows the latest message
        this.args.chatMessages.scrollTop = 0;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const chatbox = new Chatbox();
    if (chatbox.args.chatBox) { // Check if the main container was found
         chatbox.display();
    }
});