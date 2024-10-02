const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
const chatContainer = document.querySelector(".chat-container");
// const deleteButton = document.querySelector("#delete-btn");
const refreshButton = document.querySelector("#refresh-btn");
const uploadButton = document.querySelector("#upload-btn");
const uploadInput = document.querySelector("#upload-input");

// Load previous chats from localStorage
const loadDataFromLocalStorage = () => {
    const savedChats = localStorage.getItem("all-chats");

    if (savedChats) {
        chatContainer.innerHTML = savedChats;
    }
    
    // Always show the default text
    showDefaultText();
};

// Show default text if no chat history is found
const showDefaultText = () => {
    const defaultText = `<div class="default-text">
                            <h1>টিয়া আপা</h1>
                            <p>আপাকে জিজ্ঞেস করুন।<br> আপনার চ্যাট এখানে প্রদর্শিত হবে।</p>
                        </div>`;
    chatContainer.innerHTML = defaultText;
};

// Create a chat element (for both user and assistant messages)
const createChatElement = (content, className) => {
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = content;
    return chatDiv;
};

// Function to send the message to the Flask backend and display the response
const sendMessage = async () => {
    const userText = chatInput.value.trim();
    if (!userText) return;

    // Display user's question
    const userChat = createChatElement(`<div class="chat-content">
                                            <div class="chat-details">
                                                <img src="/static/images/user.jpg" alt="user-img">
                                                <p>${userText}</p>
                                            </div>
                                        </div>`, "outgoing");
    chatContainer.appendChild(userChat);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    // Clear the input field
    chatInput.value = "";

    // Send request to the server
    const response = await fetch('/ask', {  // Use the correct endpoint
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userText }),  // Simplified to match your example
    });

    if (!response.ok) {
        console.error("Error while sending message:", response.statusText);
        return;
    }

    const data = await response.json();
    // Display assistant's response
    const botChat = createChatElement(`<div class="chat-content">
                                            <div class="chat-details">
                                                <img src="/static/images/FixedPinwheel.png" alt="assistant-img">
                                                <p>${data.response}</p>
                                            </div>
                                        </div>`, "incoming");
    chatContainer.appendChild(botChat);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    // Store the conversation in localStorage
    localStorage.setItem("all-chats", chatContainer.innerHTML);
};

// Handle file upload functionality
const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Display the file upload message in the chat
    const userChat = createChatElement(`<div class="chat-content">
                                            <div class="chat-details">
                                                <img src="/static/images/user.jpg" alt="user-img">
                                                <p>File uploaded: ${file.name}</p>
                                            </div>
                                        </div>`, "outgoing");
    chatContainer.appendChild(userChat);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        const botResponse = data.message;

        const botChat = createChatElement(`<div class="chat-content">
                                                <div class="chat-details">
                                                    <img src="/static/images/FixedPinwheel.png" alt="assistant-img">
                                                    <p>${botResponse}</p>
                                                </div>
                                            </div>`, "incoming");
        chatContainer.appendChild(botChat);
        chatContainer.scrollTo(0, chatContainer.scrollHeight);

        localStorage.setItem("all-chats", chatContainer.innerHTML);
    } catch (error) {
        console.error("Error while uploading file:", error);
        const errorChat = createChatElement(`<div class="chat-content">
                                                 <div class="chat-details">
                                                     <img src="/static/images/FixedPinwheel.png" alt="assistant-img">
                                                     <p class="error">Error: Unable to upload file.</p>
                                                 </div>
                                             </div>`, "incoming");
        chatContainer.appendChild(errorChat);
        chatContainer.scrollTo(0, chatContainer.scrollHeight);
    }
};

// Delete chat history
// const deleteChats = () => {
//     if (confirm("Are you sure you want to delete all the chats?")) {
//         localStorage.removeItem("all-chats");
//         showDefaultText();
//     }
// };
const refreshChats = () => {
    // Clear the chat container and show the default text
    chatContainer.innerHTML = "";
    showDefaultText();
};
// Event listeners for sending messages and handling chat actions
sendButton.addEventListener("click", sendMessage);
// deleteButton.addEventListener("click", deleteChats);
refreshButton.addEventListener("click", refreshChats);
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Handle file uploads
uploadButton.addEventListener("click", () => uploadInput.click());
uploadInput.addEventListener("change", handleFileUpload);

// Image upload button behavior
document.querySelector("#add-btn").addEventListener("click", () => {
    document.querySelector("#image-input").click();
});
document.querySelector("#image-input").addEventListener("change", handleImageUpload);

// Load previous chats from localStorage
loadDataFromLocalStorage();
