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

app.post("/process-audio", upload.single("file"), (req, res) => {
  if (!req.file) {
    return res
      .status(400)
      .json({ status: "error", message: "No file uploaded" });
  }

  const inputPath = req.file.path;
  const wavPath = `uploads/${Date.now()}_audio.wav`;

  // ✅ Convert to WAV
  ffmpeg(inputPath)
    .output(wavPath)
    .audioCodec("pcm_s16le")
    .toFormat("wav")
    .on("end", () => {
      console.log(`Conversion successful: ${wavPath}`);

      // ✅ Call Python script to process audio
      const pythonProcess = spawn("python", ["audio_processing.py", wavPath]);

      let enhancedPath = "";
      let pitchValue = 0;
      let amplitudeValue = 0;
      let meanFrequency = 0;
      let tempoValue = 0; // ✅ Added tempo value

      pythonProcess.stdout.on("data", (data) => {
        enhancedPath = data.toString().trim();
      });

      pythonProcess.stderr.on("data", (data) => {
        const stderrMessage = data.toString().trim();

        const pitchMatch = stderrMessage.match(/Estimated Pitch \(Hz\): ([\d.]+)/);
        const ampMatch = stderrMessage.match(/Estimated Amplitude \(RMS\): ([\d.]+)/);
        const freqMatch = stderrMessage.match(/Mean Frequency \(Hz\): ([\d.]+)/);
        const tempoMatch = stderrMessage.match(/Estimated Tempo \(BPM\): ([\d.]+)/); // ✅ Extract tempo

        if (pitchMatch) pitchValue = parseFloat(pitchMatch[1]);
        if (ampMatch) amplitudeValue = parseFloat(ampMatch[1]);
        if (freqMatch) meanFrequency = parseFloat(freqMatch[1]);
        if (tempoMatch) tempoValue = parseFloat(tempoMatch[1]); // ✅ Set tempo
      });

      pythonProcess.stderr.on("data", (err) => {
        console.error("Python Error:", err.toString());
      });

      pythonProcess.on("close", (code) => {
        if (code !== 0 || !enhancedPath) {
          return sendError(res, "Processing failed", [wavPath, inputPath]);
        }

        res.json({
          status: "success",
          enhancedAudio: enhancedPath,
          pitch: pitchValue || 0,
          amplitude: amplitudeValue || 0,
          meanFrequency: meanFrequency || 0,
          tempo: tempoValue || 0, // ✅ Return tempo value
        });

        cleanupFiles([wavPath, inputPath]); // Keep enhanced file for download
      });
    })
    .on("error", (err) => {
      console.error("FFmpeg error:", err);
      sendError(res, "Conversion failed", [inputPath]);
    })
    .run();
});


// ✅ Helper function to delete files
function cleanupFiles(paths) {
  paths.forEach((file) => {
    fs.unlink(file, (err) => {
      if (err) console.error(`Error deleting ${file}:`, err);
    });
  });
}

// ✅ Helper function to send error response and clean up files
function sendError(res, message, filesToDelete = []) {
  if (!res.headersSent) {
    res.status(500).json({ status: "error", message });
  }
  cleanupFiles(filesToDelete);
}

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
