import React, { useState } from "react";
import { Button, Form } from "react-bootstrap";
import TextareaAutosize from "react-textarea-autosize";
import "../../assets/css/input.css";

const ChatGPTInputField: React.FC = () => {
  const [inputValue, setInputValue] = useState("");

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(event.target.value);
  };

  const handleSubmit = () => {
    alert(`Input Value: ${inputValue}`);
  };

  return (
    <div
      className="chat-input-container bg-light"
      style={{
        position: "fixed",
        bottom: "1.5rem",
        padding: "1rem 2rem",
        boxShadow: "0 -2px 5px rgba(0, 0, 0, 0.1)",
      }}
    >
      <Form className="d-flex">
        <TextareaAutosize
          minRows={1}
          maxRows={5} // Adjust the maximum height before scrolling
          placeholder="Type your message here..."
          value={inputValue}
          onChange={handleInputChange}
          className="flex-grow-1"
          style={{
            borderRadius: "20px",
            padding: "0.75rem 1.25rem",
            fontSize: "1rem",
            border: "1px solid #ced4da",
            outline: "none",
            overflowY: "auto",
            resize: "none", // Prevent manual resizing
          }}
        />
      </Form>
      <Button
          variant="primary"
          onClick={handleSubmit}
          className="mt-2"
          style={{
            marginLeft: "1rem",
            borderRadius: "20px",
            padding: "0.75rem 1.5rem",
            fontSize: "1rem",
          }}
        >
          Send
        </Button>
    </div>
  );
};

export default ChatGPTInputField;
