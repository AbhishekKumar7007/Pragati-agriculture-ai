const input = document.getElementById("crop-image");
const preview = document.getElementById("image-preview");
if (input && preview) {
  input.addEventListener("change", () => {
    preview.innerHTML = "";
    const file = input.files && input.files[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      preview.textContent = "Please select an image file.";
      return;
    }
    const img = document.createElement("img");
    img.alt = "Selected crop photo preview";
    img.src = URL.createObjectURL(file);
    preview.appendChild(img);
  });
}
