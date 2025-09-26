document.addEventListener("DOMContentLoaded", () => {
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const previewContainer = document.getElementById("preview-container");
  const previewImage = document.getElementById("preview-image");
  const copyButtons = document.querySelectorAll(".copy-button");
  const PLACEHOLDER_SRC = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==";
  let currentPreviewUrl;

  const resetPreview = () => {
    if (!previewContainer || !previewImage) return;
    if (currentPreviewUrl) {
      URL.revokeObjectURL(currentPreviewUrl);
      currentPreviewUrl = undefined;
    }
    previewImage.onload = null;
    previewImage.onerror = null;
    previewImage.classList.remove("has-source");
    previewImage.src = PLACEHOLDER_SRC;
    previewContainer.hidden = true;
  };

  resetPreview();

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
        resetPreview();
        return;
      }
      fileInput.files = files;
      renderPreview(file);
    });

    fileInput.addEventListener("change", () => {
      const [file] = fileInput.files ?? [];
      if (file) {
        renderPreview(file);
        return;
      }
      resetPreview();
    });
  }

  const renderPreview = (file) => {
    if (!previewContainer || !previewImage) return;
    resetPreview();

    if (!file.type || !file.type.startsWith("image/")) {
      alert("Please select a valid image file.");
      return;
    }

    currentPreviewUrl = URL.createObjectURL(file);

    previewImage.onload = () => {
      previewContainer.hidden = false;
      previewImage.classList.add("has-source");
    };

    previewImage.onerror = () => {
      alert("We couldn't generate a preview for this file. Please try another image.");
      resetPreview();
    };

    previewImage.src = currentPreviewUrl;
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
