import ChatBot from "react-chatbotify";

const MyChatBot = () => {
    let hasError = false;

    // Function to call the FastAPI endpoint for streaming response
    const call_fastapi = async (params) => {
        try {
            const response = await fetch('http://host.docker.internal:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message : params.userInput }),
            });

            if (!response.ok) {
                throw new Error("Error fetching from FastAPI");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let messageBuffer = '';

            // Read stream response
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                messageBuffer += chunk;

                // Inject each chunk into the chatbot message
                await params.injectMessage(messageBuffer);
            }
        } catch (error) {
            await params.injectMessage(`Unable to fetch response from the server: ${error.message}`);
            hasError = true;
        }
    };

    const flow = {
        start: {
            message: "Start asking away!",
            path: "loop",
        },
        loop: {
            message: async (params) => {
                await call_fastapi(params);
            },
            path: () => {
                if (hasError) {
                    return "start";
                }
                return "loop";
            },
        },
    };

    return (
        <ChatBot
            settings={{ general: { embedded: true }, chatHistory: { storageKey: "example_llm_conversation" } }}
            flow={flow}
        />
    );
};

export default MyChatBot;
