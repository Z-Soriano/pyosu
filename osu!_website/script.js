const fileInput = document.getElementById("fileInput");
const output = document.getElementById("output");
const statusText = document.getElementById("status");
const downloadButton = document.getElementById("downloadButton");
const clearButton = document.getElementById("clearButton");

const STORAGE_KEY = "savedOsuContent";
const FILE_NAME_KEY = "savedOsuFileName";

function loadSavedContent() {
  const savedContent = localStorage.getItem(STORAGE_KEY);
  const savedFileName = localStorage.getItem(FILE_NAME_KEY);

  if (savedContent) {
    output.textContent = savedContent;
    statusText.textContent = `Saved content loaded from: ${savedFileName || "unknown file"}`;
  } else {
    output.textContent = "";
    statusText.textContent = "No saved content yet.";
  }
}

fileInput.addEventListener("change", function(event) {
  const file = event.target.files[0];

  if (!file) return;

  if (!file.name.endsWith(".osu")) {
    alert("Please upload a .osu file.");
    fileInput.value = "";
    return;
  }

  const reader = new FileReader();

  reader.onload = function(e) {
    const fileContent = e.target.result;

    // This overwrites the old saved osu! file content.
    localStorage.setItem(STORAGE_KEY, fileContent);
    localStorage.setItem(FILE_NAME_KEY, file.name);

    output.textContent = fileContent;
    statusText.textContent = `Saved content updated from: ${file.name}`;
  };

  reader.readAsText(file);
});

downloadButton.addEventListener("click", function() {
  const savedContent = localStorage.getItem(STORAGE_KEY);
  const savedFileName = localStorage.getItem(FILE_NAME_KEY) || "saved-osu-file.osu";

  if (!savedContent) {
    alert("There is no saved content to download.");
    return;
  }

  const txtFileName = savedFileName.replace(/\.osu$/i, "") + ".txt";
  const blob = new Blob([savedContent], { type: "text/plain" });
  const link = document.createElement("a");

  link.href = URL.createObjectURL(blob);
  link.download = txtFileName;
  link.click();

  URL.revokeObjectURL(link.href);
});

clearButton.addEventListener("click", function() {
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(FILE_NAME_KEY);
  loadSavedContent();
});

loadSavedContent();
