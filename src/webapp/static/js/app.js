document.addEventListener("DOMContentLoaded", () => {
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const previewContainer = document.getElementById("preview-container");
  const previewImage = document.getElementById("preview-image");
  const copyButtons = document.querySelectorAll(".copy-button");

  if (dropZone && fileInput) {
    const resetHighlight = () => dropZone.classList.remove("drag-over");

    dropZone.addEventListener("dragover", (event) => {
      event.preventDefault();
      dropZone.classList.add("drag-over");
    });

    dropZone.addEventListener("dragleave", resetHighlight);
    dropZone.addEventListener("dragend", resetHighlight);

    dropZone.addEventListener("drop", (event) => {
      event.preventDefault();
      resetHighlight();
      const files = event.dataTransfer?.files;
      if (!files || !files.length) return;
      const file = files[0];
      if (!file.type.startsWith("image/")) {
        alert("Please drop a valid image file.");
        return;
      }
      fileInput.files = files;
      renderPreview(file);
    });

    fileInput.addEventListener("change", () => {
      const [file] = fileInput.files ?? [];
      if (file) {
        renderPreview(file);
      }
    });
  }

  const renderPreview = (file) => {
    if (!previewContainer || !previewImage) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      previewImage.src = event.target?.result ?? "";
      previewContainer.hidden = false;
    };
    reader.readAsDataURL(file);
  };

  copyButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const text = button.dataset.copyTarget ?? "";
      if (!text.trim()) {
        alert("Nothing to copy yet. Submit an image first.");
        return;
      }
      navigator.clipboard
        .writeText(text)
        .then(() => {
          button.textContent = "Copied!";
          setTimeout(() => {
            button.textContent = "Copy text";
          }, 2000);
        })
        .catch(() => {
          alert("Could not copy text. Please copy manually.");
        });
    });
  });
});
