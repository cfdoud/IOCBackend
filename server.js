import React, { useState, useEffect } from "react";

function OfficeSelectionPage() {
  const [offices, setOffices] = useState([]);
  const [selectedOffice, setSelectedOffice] = useState("");
  const [newOffice, setNewOffice] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Fetch the list of offices from your API

  const serverUrl = "http://localhost:3000";

  useEffect(() => {
    fetch("serverUrl")
      .then((response) => response.json())
      .then((data) => setOffices(data))
      .catch((error) => console.error("Error fetching offices:", error));
  }, []);

  // Handle office selection
  const handleOfficeSelect = () => {
    if (selectedOffice) {
      // Log the user in and redirect to the dashboard or main page
      fetch(`/api/login/${selectedOffice}`)
        .then((response) => response.json())
        .then((data) => {
          // Redirect or show user info
          console.log(data);
          // Redirect to the next page (for example, the dashboard)
        })
        .catch((error) => console.error("Error during login:", error));
    } else {
      setErrorMessage("Please select an office.");
    }
  };

  // Handle office creation if the office doesn't exist
  const handleCreateOffice = () => {
    if (newOffice) {
      // Check if the new office already exists in the list
      if (offices.some((office) => office.name.toLowerCase() === newOffice.toLowerCase())) {
        setErrorMessage("This hospital already exists in the list.");
      } else {
        // Proceed to create the office
        fetch("/api/create-office", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ name: newOffice }),
        })
          .then((response) => response.json())
          .then((data) => {
            // Update the offices list to include the new hospital
            setOffices((prevOffices) => [...prevOffices, data]);
            setNewOffice(""); // Clear input
            setSuccessMessage(`Hospital "${newOffice}" created successfully!`);
            setErrorMessage(""); // Clear any previous error message
          })
          .catch((error) => {
            console.error("Error creating office:", error);
            setErrorMessage("Error creating the hospital.");
          });
      }
    } else {
      setErrorMessage("Please enter a new office name.");
    }
  };

  return (
    <div>
      <h1>Choose your office</h1>
      <div>
        <h2>Select an existing office:</h2>
        <select
          value={selectedOffice}
          onChange={(e) => setSelectedOffice(e.target.value)}
        >
          <option value="">Select an office</option>
          {offices.map((office) => (
            <option key={office.id} value={office.name}>
              {office.name}
            </option>
          ))}
        </select>
        <button onClick={handleOfficeSelect}>Log in</button>
      </div>

      <div>
        <h2>Or create a new office:</h2>
        <input
          type="text"
          value={newOffice}
          onChange={(e) => setNewOffice(e.target.value)}
          placeholder="Enter office name"
        />
        <button onClick={handleCreateOffice}>Create Office</button>
      </div>

      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
      {successMessage && <p style={{ color: "green" }}>{successMessage}</p>}
    </div>
  );
}

export default OfficeSelectionPage;
