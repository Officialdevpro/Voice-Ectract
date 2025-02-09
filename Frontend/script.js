// getting HTML elements
const nav = document.querySelector("nav"),
  toggleBtn = nav.querySelector(".toggle-btn");

toggleBtn.addEventListener("click", () => {
  nav.classList.toggle("open");
});

const recordBtn = document.getElementById("recordBtn");
const livePreview = document.getElementById("livePreview");
const recordedVideo = document.getElementById("recordedVideo");

let mediaRecorder;
let recordedChunks = [];
let isRecording = false;
let stream = null;

recordBtn.addEventListener("click", async () => {
  if (!isRecording) {
    recordBtn.firstElementChild.firstElementChild.setAttribute(
      "class",
      "bx bx-stop"
    );
    try {
      // Get Camera Access
      stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      livePreview.srcObject = stream;

      livePreview.muted = true;
      livePreview.play();
      // Start Recording
      recordedChunks = [];
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();
      isRecording = true;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.push(event.data);
        }
      };
    } catch (error) {
      console.error("Error accessing camera:", error);
    }
  } else {
    // Stop Recording
    mediaRecorder.stop();
    isRecording = false;
    recordBtn.firstElementChild.firstElementChild.setAttribute(
      "class",
      "bx bx-video"
    );
    nav.classList.toggle("open");

    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunks, { type: "video/webm" });
      const videoURL = URL.createObjectURL(blob);
      recordedVideo.src = videoURL;
      recordedVideo.style.display = "block"; // Show recorded video
      livePreview.style.display = "none"; // Hide live preview

      // Stop camera stream
      stream.getTracks().forEach((track) => track.stop());
    };
  }
});
