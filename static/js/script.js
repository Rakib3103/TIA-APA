const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
const chatContainer = document.querySelector(".chat-container");
const refreshButton = document.querySelector("#refresh-btn");
const microphoneButton = document.querySelector("#microphone-btn");
const imageInput = document.querySelector("#image-input");
const addButton = document.querySelector("#add-btn");

// Store the image globally for use later
let selectedImageFile = null;

// Show the selected image in the chatbox before sending
addButton.addEventListener("click", () => {
    imageInput.click();
});

imageInput.addEventListener("change", async () => {
    const file = imageInput.files[0];
    if (file) {
        selectedImageFile = await resizeAndCompressImage(file, 800, 800, 0.7); // Resize to 800x800 and compress at 70% quality

        // Create an image URL to display in the chat
        const imageUrl = URL.createObjectURL(selectedImageFile);
        
        // Display the image in the chatbox
        // const imagePreview = createChatElement(`<div class="chat-content">
        //                                             <div class="chat-details">
        //                                                 <img src="${imageUrl}" alt="uploaded-image" class="uploaded-image">
        //                                             </div>
        //                                         </div>`, "outgoing");
        // chatContainer.appendChild(imagePreview);
        // chatContainer.scrollTo(0, chatContainer.scrollHeight);

        sendMessage(); // Send the compressed image immediately
    }
});

const resizeAndCompressImage = async (file, maxWidth, maxHeight, quality) => {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        
        reader.onload = (event) => {
            const img = new Image();
            img.src = event.target.result;
            
            img.onload = () => {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;

                // Maintain aspect ratio
                if (width > height) {
                    if (width > maxWidth) {
                        height = Math.round((height * maxWidth) / width);
                        width = maxWidth;
                    }
                } else {
                    if (height > maxHeight) {
                        width = Math.round((width * maxHeight) / height);
                        height = maxHeight;
                    }
                }

                canvas.width = width;
                canvas.height = height;
                
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);

                // Compress and convert the canvas to a Blob
                canvas.toBlob((blob) => {
                    const compressedFile = new File([blob], file.name, { type: 'image/jpeg', lastModified: Date.now() });
                    resolve(compressedFile);
                }, 'image/jpeg', quality);
            };
        };
    });
};

let recognition;
let isRecognizing = false;

// Initialize the SpeechRecognition object
const initializeSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'en-US'; 
    recognition.interimResults = false; 
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
        isRecognizing = true;
        microphoneButton.classList.add('active');
    };

    recognition.onend = () => {
        isRecognizing = false;
        microphoneButton.classList.remove('active');
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        chatInput.value = transcript; // Insert the transcribed text into the chat input
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        recognition.stop();
    };
};

// Start and stop speech recognition
const toggleSpeechRecognition = () => {
    if (isRecognizing) {
        recognition.stop();
    } else {
        recognition.start();
    }
};

// Initialize the speech recognition when the page loads
initializeSpeechRecognition();

// Add event listener for the microphone button
microphoneButton.addEventListener("click", toggleSpeechRecognition);

// Clear previous chats from localStorage (no longer needed)
const loadDataFromLocalStorage = () => {
    chatContainer.innerHTML = ""; // Clear chat container on load
    showDefaultText(); // Show default text if no chat history is found
};

// Show default text if no chat history is found
const showDefaultText = () => {
    const defaultText = `<div class="default-text">
                            <h1>টিয়া আপা</h1>
                            <p>আপাকে জিজ্ঞেস করুন।<br> আপনার চ্যাট এখানে প্রদর্শিত হবে।</p>
                        </div>`;
    if (!chatContainer.innerHTML.trim()) {
        chatContainer.innerHTML = defaultText;
    }
};

// Create a chat element (for both user and assistant messages)
const createChatElement = (content, className) => {
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = content;
    return chatDiv;
};

const sendMessage = async () => {
    const userText = chatInput.value.trim();

    if (!userText && !selectedImageFile) return; // Don't send if there's no text or image

    let messageContent = '';
    if (selectedImageFile) {
        const imageUrl = URL.createObjectURL(selectedImageFile);
        messageContent += `<img src="${imageUrl}" alt="uploaded-image" class="uploaded-image">`;
    }
    if (userText) {
        messageContent += `<p>${userText}</p>`;
    }

    const userChat = createChatElement(`<div class="chat-content">
                                            <div class="chat-details">
                                                <img src="/static/images/user.jpg" alt="user-img">
                                                ${messageContent}
                                            </div>
                                        </div>`, "outgoing");
    chatContainer.appendChild(userChat);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    const formData = new FormData();
    if (userText) formData.append("question", userText);
    if (selectedImageFile) formData.append("image", selectedImageFile);

    chatInput.value = "";
    selectedImageFile = null;

    const response = await fetch('/ask', {
        method: 'POST',
        body: formData,
    });

    const data = await response.json();

    const botChat = createChatElement(`<div class="chat-content">
                                            <div class="chat-details">
                                                <img src="/static/images/FixedPinwheel.png" alt="assistant-img">
                                                <p>${data.response}</p>
                                            </div>
                                        </div>`, "incoming");
    chatContainer.appendChild(botChat);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
};

// Refresh chat history (reset chats)
const refreshChats = () => {
    // Clear the chat container and show the default text
    chatContainer.innerHTML = "";
    showDefaultText();
};

// Event listeners for sending messages and handling chat actions
sendButton.addEventListener("click", sendMessage);
refreshButton.addEventListener("click", refreshChats);
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Load default text on page load
loadDataFromLocalStorage();
