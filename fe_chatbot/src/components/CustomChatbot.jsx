import ChatBot from "react-chatbotify";

const MyChatBot = () => {
    let hasError = false;

    // Function to stream from FastAPI endpoint
    const fastapi_stream = async (params) => {
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'accept': 'application/json'
                },
                // Send user input as "message"
                body: JSON.stringify({ message: params.userInput }),
            });

            if (!response.ok) {
                throw new Error("Error fetching from FastAPI");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            //let text = ""; // Buffer for full message
            //let offset = 0;

            // Buffer for streaming message
            // Stream response from the server
            let chunk = "";
            while (true) {
                const { done, value } = await reader.read();

                chunk += decoder.decode(value, { stream: !done });
                await params.streamMessage(chunk);
                if (done) break;
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
                await new Promise(async (resolve) => {
                    await fastapi_stream(params);
                    resolve();
                });
            },
            path: () => {
                if (hasError) {
                    return "start";
                }
                return "loop";
            },
        },
    };

    const themes = [
        {id: "simple_blue", version: "0.1.0"}
    ]

    return (
        <ChatBot
            settings={{ general: { embedded: true }, chatHistory: { storageKey: "example_real_time_stream" }, botBubble: { simStream: true } }}
            flow={flow}
            themes={themes}
        />
    );
};

export default MyChatBot;
