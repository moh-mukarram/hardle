import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SignUpPage } from "./components/SignUpPage";
import { LoginPage } from "./components/LoginPage";
import { GamePage } from "./components/GamePage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SignUpPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/game" element={<GamePage />} />
      </Routes>
    </BrowserRouter>
  );
}