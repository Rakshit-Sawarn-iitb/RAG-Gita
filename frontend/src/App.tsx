import ResponsiveAppBar from "./components/shared/navbar";
import './App.css';
import ChatPage from "./components/Home/chatpage";
import InputField from "./components/shared/input";
function App() {
  return (
    <>
      <ResponsiveAppBar />
      <ChatPage />
      <InputField />
    </>
  );
}

export default App;