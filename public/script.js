const fileInput = document.getElementById("fileInput");
const rawOutput = document.getElementById("rawOutput");
const formattedOutput = document.getElementById("formattedOutput");
const statusText = document.getElementById("status");
const downloadButton = document.getElementById("downloadButton");
const copyButton = document.getElementById("copyButton");
const clearButton = document.getElementById("clearButton");
const expandButton = document.getElementById("expandButton");
const collapseButton = document.getElementById("collapseButton");

const STORAGE_KEY = "savedOsuContent";
const FILE_NAME_KEY = "savedOsuFileName";

function escapeHTML(text) {
  return text.replace(/[&<>"']/g, function(char) {
    return {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "\"": "&quot;",
      "'": "&#039;"
    }[char];
  });
}

function parseOsuSections(content) {
  const lines = content.split(/\r?\n/);
  const sections = {};
  let currentSection = "Header";
  sections[currentSection] = [];

  for (const line of lines) {
    const sectionMatch = line.match(/^\[(.+)\]$/);

    if (sectionMatch) {
      currentSection = sectionMatch[1];
      sections[currentSection] = [];
    } else {
      sections[currentSection].push(line);
    }
  }

  return sections;
}

function createDropdown(title, bodyHTML, openByDefault = false) {
  return `
    <details class="section-dropdown" ${openByDefault ? "open" : ""}>
      <summary>${escapeHTML(title)}</summary>
      <div class="section-body">
        ${bodyHTML}
      </div>
    </details>
  `;
}

function renderKeyValueSection(title, lines, openByDefault) {
  const rows = lines
    .filter(line => line.trim() && !line.trim().startsWith("//"))
    .map(line => {
      const colonIndex = line.indexOf(":");

      if (colonIndex === -1) {
        return `
          <div class="key">Line</div>
          <div class="value">${escapeHTML(line)}</div>
        `;
      }

      const key = line.slice(0, colonIndex).trim();
      const value = line.slice(colonIndex + 1).trim();

      return `
        <div class="key">${escapeHTML(key)}</div>
        <div class="value">${escapeHTML(value)}</div>
      `;
    })
    .join("");

  const body = `
    <div class="key-value-list">
      ${rows || `<div class="empty-state">No visible values in this section.</div>`}
    </div>
  `;

  return createDropdown(title, body, openByDefault);
}

function renderLineSection(title, lines, openByDefault) {
  const items = lines
    .filter(line => line.trim() && !line.trim().startsWith("//"))
    .map(line => `<li>${escapeHTML(line)}</li>`)
    .join("");

  const body = items
    ? `<ol class="line-list">${items}</ol>`
    : `<div class="empty-state">No visible lines in this section.</div>`;

  return createDropdown(title, body, openByDefault);
}

function renderFormattedContent(content) {
  const sections = parseOsuSections(content);

  const html = Object.entries(sections).map(([title, lines], index) => {
    const keyValueSections = ["Header", "General", "Editor", "Metadata", "Difficulty", "Colours"];
    const openByDefault = index === 0 || title === "Metadata";

    if (keyValueSections.includes(title)) {
      return renderKeyValueSection(title, lines, openByDefault);
    }

    return renderLineSection(title, lines, openByDefault);
  }).join("");

  formattedOutput.innerHTML = html || `<div class="card empty-state">No content found.</div>`;
}

function loadSavedContent() {
  const savedContent = localStorage.getItem(STORAGE_KEY);
  const savedFileName = localStorage.getItem(FILE_NAME_KEY);

  if (savedContent) {
    rawOutput.textContent = savedContent;
    renderFormattedContent(savedContent);
    statusText.textContent = `Loaded saved content from: ${savedFileName || "unknown file"}`;
  } else {
    rawOutput.textContent = "";
    formattedOutput.innerHTML = `<div class="card empty-state">Upload a .osu file to see dropdown sections here.</div>`;
    statusText.textContent = "No saved content yet.";
  }
}

fileInput.addEventListener("change", function(event) {
  const file = event.target.files[0];

  if (!file) return;

  if (!file.name.toLowerCase().endsWith(".osu")) {
    alert("Please upload a .osu file.");
    fileInput.value = "";
    return;
  }

  const reader = new FileReader();

  reader.onload = function(e) {
    const fileContent = e.target.result;

    localStorage.setItem(STORAGE_KEY, fileContent);
    localStorage.setItem(FILE_NAME_KEY, file.name);

    rawOutput.textContent = fileContent;
    renderFormattedContent(fileContent);
    statusText.textContent = `Saved content updated from: ${file.name}`;
  };

  reader.readAsText(file);
});

expandButton.addEventListener("click", function() {
  document.querySelectorAll(".section-dropdown").forEach(section => {
    section.open = true;
  });
});

collapseButton.addEventListener("click", function() {
  document.querySelectorAll(".section-dropdown").forEach(section => {
    section.open = false;
  });
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

copyButton.addEventListener("click", async function() {
  const savedContent = localStorage.getItem(STORAGE_KEY);

  if (!savedContent) {
    alert("There is no saved content to copy.");
    return;
  }

  await navigator.clipboard.writeText(savedContent);
  alert("Saved content copied.");
});

clearButton.addEventListener("click", function() {
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(FILE_NAME_KEY);
  fileInput.value = "";
  loadSavedContent();
});

loadSavedContent();

// document.getElementById("runButton").addEventListener("click", () => {
//   const savedContent = localStorage.getItem(STORAGE_KEY);
//   // fetch("http://localhost:5000/run", {
//   //   method: "POST",
//   //   headers: {
//   //     "Content-Type": "application/json"
//   //   },
//   //   body: JSON.stringify({
//   //     content: savedContent
//   //   })
//   // })
//   //   .then(res => res.json())
//   //   .then(data => {
//   //     document.getElementById("output").innerText = data.output;
//   //   })
//   //   .catch(err => {
//   //     console.error(err);
//   //   });
//   fetch("/api/run", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ content: savedContent })
//   })
//     .then(res => res.json())
//     .then(data => {
//       document.getElementById("output").innerText = data.output;
//     })
//     .catch(err => {
//       console.error(err);
//     });
// });
document.getElementById("runButton").addEventListener("click", async () => {
  const output = document.getElementById("output");
  output.innerText = "Button clicked. Sending request...";

  const savedContent = localStorage.getItem(STORAGE_KEY);

  // if (!savedContent) {
  //   output.innerText = "No savedContent found in localStorage.";
  //   return;
  // }

  // try {
  //   const res = await fetch("/api/run", {
  //     method: "POST",
  //     headers: { "Content-Type": "application/json" },
  //     body: JSON.stringify({ content: savedContent })
  //   });

  //   const text = await res.text();

  //   output.innerText =
  //     "Status: " + res.status + "\n\n" +
  //     "Raw response:\n" + text;

  // } catch (err) {
  //   output.innerText = "Fetch failed:\n" + err;
  // }

    fetch("/api/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: savedContent })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("output").innerText = data.output;
  });
  //   fetch("/api/run", {
  //   method: "POST",
  //   headers: { "Content-Type": "application/json" },
  //   body: JSON.stringify({ content: savedContent })
  // })
  // .then(async res => {
  //   const text = await res.text();
  //   console.log("STATUS:", res.status);
  //   console.log("RAW:", text);

  //   document.getElementById("output").innerText = text;
  // });
});