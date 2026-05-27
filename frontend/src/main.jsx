import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import Login from "./Login.jsx";
import { getToken } from "./api.js";

function Root() {
  const [authed, setAuthed] = useState(!!getToken());
  const [username, setUsername] = useState("");

  if (!authed) {
    return (
      <Login
        onLogin={(data) => {
          setUsername(data.username || "");
          setAuthed(true);
        }}
      />
    );
  }

  return (
    <App
      username={username}
      onLogout={() => {
        setAuthed(false);
        setUsername("");
      }}
    />
  );
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Root />
  </StrictMode>
);
