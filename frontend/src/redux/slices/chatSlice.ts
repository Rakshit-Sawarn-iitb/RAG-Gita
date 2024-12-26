import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface ChatMessage {
  id: string; // Unique identifier for each message
  sender: "user" | "bot"; // Identify the sender
  message: string; // The message content
}

interface ChatState {
  messages: ChatMessage[]; // Array to store messages
}

const initialState: ChatState = {
  messages: [],
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload); // Add a new message
    },
    clearChat: (state) => {
      state.messages = []; // Clear chat history
    },
  },
});

export const { addMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
