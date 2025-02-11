const nav = document.querySelector("nav"),
  toggleBtn = nav.querySelector(".toggle-btn");
const recordBtn = document.getElementById("recordBtn");
const fileInput = document.createElement("input"); // Create an input element dynamically
fileInput.type = "file"; // Set type to file
fileInput.accept = "audio/mp3"; // Allow only MP3 files

toggleBtn.addEventListener("click", () => {
  nav.classList.toggle("open");
});

recordBtn.addEventListener("click", () => {
  // Trigger file input when "Record" button is clicked
  fileInput.click();
});

// When a file is selected by the user
fileInput.addEventListener("change", (event) => {
  event.preventDefault()
  const file = event.target.files[0]; // Get the selected file
 
    // Send the selected audio file to the backend directly
    sendAudioToBackend(file);
  
});

// Function to send the audio file to the backend
function sendAudioToBackend(audioFile) {

  const formData = new FormData();
  formData.append("file", audioFile, audioFile.name); // Append the selected audio file

  // Send the audio file to the backend via POST request
  fetch("http://localhost:8080/process-audio", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      console.log(response)
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.blob(); // Get the processed audio as a Blob
    })
    .then((processedAudioBlob) => {
      console.log("Audio processed successfully");

      // Optionally, you can process the returned audio here
      const processedAudioURL = URL.createObjectURL(processedAudioBlob);
      // Handle processed audio, e.g., create an audio element
      const audioElement = new Audio(processedAudioURL);
      audioElement.play();
    })
    .catch((error) => {
      console.error("Error uploading or processing audio:", error);
    });
}



