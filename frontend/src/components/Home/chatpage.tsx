import React from "react";
import { useSelector } from "react-redux";
import { RootState } from "../../redux/store";
import ChatBubble from "../shared/bot";

const ChatPage: React.FC = () => {
  const messages = useSelector((state: RootState) => state.chat.messages);

  return (
    <>
    <div className="chat-page" style={{ padding: "2rem", marginBottom: "5rem", maxHeight: "calc(100vh - 12rem)", overflowY: "scroll"}}>
      {messages.map((msg) => (
        <ChatBubble key={msg.id} message={msg.sender === "user"?msg.message:msg.message.answer} isUser={msg.sender === "user"} />
      ))}
    </div>
    </>
  );
};

export default ChatPage;
