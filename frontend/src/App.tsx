import ResponsiveAppBar from "./components/shared/navbar";
import './App.css';
import ResponsiveInputField from "./components/shared/input";
import ChatBubble from "./components/shared/bot";
function App() {
  return (
    <>
      <ResponsiveAppBar />
      <ResponsiveInputField />
      <ChatBubble message="Hello, I am a bot!" isUser={false}/>
      <ChatBubble message="Hello, I am a bot!" isUser={true}/>
    </>
  );
}

export default App;
