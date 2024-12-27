import React from "react";
import { Card } from "react-bootstrap";
import "../../assets/css/bot.css";

interface ChatBubbleProps {
  message: string;
  isUser: boolean; // Determines if the bubble is from the user or bot
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ message, isUser }) => {
  return (
    <div
      className={`d-flex ${
        isUser ? "justify-content-end" : "justify-content-start"
      } my-2`}
    >
      <Card
        className={`shadow-sm p-3 ${
          isUser ? "bg-primary text-white" : "bg-secondary text-light"
        }`}
        style={{
          maxWidth: "75%", // Ensure responsiveness
          borderRadius: "1rem",
          borderTopRightRadius: isUser ? "0" : "1rem",
          borderTopLeftRadius: isUser ? "1rem" : "0",
        }}
      >
        <Card.Text style={{ margin: 0 }}>{message}</Card.Text>
      </Card>
    </div>
  );
};

export default ChatBubble;
