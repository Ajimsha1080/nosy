const BACKEND_URL = "https://nosy-nky9.onrender.com";

async function uploadAudio() {
  const fileInput = document.getElementById("audioFile");
  if (!fileInput.files.length) return alert("Select an audio file first.");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  document.getElementById("result").innerText = "Processing... ⏳";

  try {
    const response = await fetch(`${BACKEND_URL}/separate`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) throw new Error("Separation failed");

    const data = await response.json();
    document.getElementById("result").innerHTML = `
      <h3>✅ Separated Tracks</h3>
      <audio controls src="${data.vocals_url}"></audio>
      <p><a href="${data.vocals_url}" download>Download Vocals</a></p>
      <audio controls src="${data.background_url}"></audio>
      <p><a href="${data.background_url}" download>Download Instrumental</a></p>
    `;
  } catch (err) {
    document.getElementById("result").innerText = "❌ Error during separation.";
    console.error(err);
  }
}

window.uploadAudio = uploadAudio;

