const express = require("express");
const multer = require("multer");
const cors = require("cors");
const ffmpeg = require("fluent-ffmpeg");
const fs = require("fs");
const { spawn } = require("child_process");
const path = require("path");

const app = express();
const port = 8080;

app.use(cors());
app.use(express.json());

// Multer setup for file uploads
const upload = multer({ dest: "uploads/" });

app.get("/",(req,res)=>{
  res.status(200).json({
    status:"success"
  })
})

app.post("/process-audio", upload.single("file"), (req, res) => {
  if (!req.file) {
    return res
      .status(400)
      .json({ status: "error", message: "No file uploaded" });
  }

  const inputPath = req.file.path;
  const wavPath = `uploads/${Date.now()}_audio.wav`;

  // Convert to WAV
  ffmpeg(inputPath)
    .output(wavPath)
    .audioCodec("pcm_s16le") // Convert to WAV format
    .toFormat("wav")
    .on("end", () => {
      console.log(`Conversion successful: ${wavPath}`);

      // Call Python script to clean noise
      const pythonProcess = spawn("python", ["audio_processing.py", wavPath]);

      pythonProcess.stdout.on("data", (data) => {
        const enhancedPath = data.toString().trim(); // Path of enhanced WAV file
        console.log(`Enhanced file: ${enhancedPath}`);

        // Send the cleaned audio file as a response

        res.download(enhancedPath, "processed_audio.wav", (err) => {
          if (err) {
            console.error("Error sending file:", err);
            res
              .status(500)
              .json({ status: "error", message: "File sending failed" });
          }

          // Cleanup: Delete processed and original files after sending
          fs.unlink(enhancedPath, (err) => {
            if (err) console.error("Error deleting enhanced file:", err);
          });

          fs.unlink(wavPath, (err) => {
            if (err) console.error("Error deleting WAV file:", err);
          });

          fs.unlink(inputPath, (err) => {
            if (err) console.error("Error deleting input file:", err);
          });
        });
      });

      pythonProcess.stderr.on("data", (err) => {
        console.error("Python Error:", err.toString());
        res.status(500).json({ status: "error", message: "Processing failed" });
      });
    })
    .on("error", (err) => {
      console.error("FFmpeg error:", err);
      res.status(500).json({ status: "error", message: "Conversion failed" });
    })
    .run();
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
