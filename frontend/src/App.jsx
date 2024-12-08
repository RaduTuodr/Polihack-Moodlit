import React, { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
  const [language, setLanguage] = useState("ro-RO"); // Selected language
  const [wakeUpHour, setWakeUpHour] = useState("07:00"); // Default wake-up hour

  // Send language change to the backend
  useEffect(() => {
    axios
      .post("http://localhost:5000/api/set-language", { language: language })
      .catch((error) => {
        console.log("Error updating language:", error);
      });
  }, [language]);

useEffect(() => {
    axios
      .post("http://localhost:5000/api/set-hour",{ hour: wakeUpHour})
      .catch((error) => {
        console.log("Error updating wake-up hour:", error);
      });
    },[wakeUpHour]);

  return (
    <div className="App">
      <h1>Text-to-Speech Controller</h1>
      <div>
        <label>
          Select Language:
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="ro-RO">Romanian</option>
            <option value="en-US">English</option>
            <option value="fr-FR">French</option>
          </select>
        </label>
      </div>
      <div>
        <label>
          Wake-up Hour:
          <input
            type="time"
            value={wakeUpHour}
            onChange={(e) => setWakeUpHour(e.target.value)}
          />
        </label>
      </div>
    </div>
  );
};

export default App;
