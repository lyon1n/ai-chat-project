import { useState } from "react";
import App from "./App.jsx";
import Login from "./Login.jsx";
import { getToken } from "./api.js";

export default function Root() {
  const [authed, setAuthed] = useState(!!getToken());

  if (!authed) {
    return (
      <Login
        onLogin={() => {
          setAuthed(true);
        }}
      />
    );
  }

  return (
    <App
      onLogout={() => {
        setAuthed(false);
      }}
    />
  );
}
