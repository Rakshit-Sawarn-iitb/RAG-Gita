import React, { useState } from "react";
import { Button, Form } from "react-bootstrap";
import TextareaAutosize from "react-textarea-autosize";
import { useDispatch } from "react-redux";
import { v4 as uuidv4 } from "uuid";
import { addMessage } from "../../redux/slices/chatSlice";
import { API } from "../../services/api";
import toast from "./toast";
import "../../assets/css/input.css";

const InputField: React.FC = () => {
  const [inputValue, setInputValue] = useState("");
  const dispatch = useDispatch();

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(event.target.value);
  };

  const handleGyanRequest = async () => {
    if (!inputValue.trim()) return;

    // Add user message to Redux
    dispatch(
      addMessage({
        id: uuidv4(),
        sender: "user",
        message: inputValue,
      })
    );

    try {
      const response = await API.question({ query: inputValue });

      // Add bot response to Redux
      dispatch(
        addMessage({
          id: uuidv4(),
          sender: "bot",
          message: response.response,
        })
      );

      toast({ content: "Response Fetched", status: "success" });
    } catch (error) {
      toast({ content: { message: "An error occurred" }, status: "error" });
    } finally {
      setInputValue(""); // Clear input field
    }
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
          maxRows={5}
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
            resize: "none",
          }}
        />
      </Form>
      <Button
        variant="primary"
        onClick={handleGyanRequest}
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

export default InputField;
