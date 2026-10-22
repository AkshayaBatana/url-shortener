const API_URL = "https://rdch2zylwh.execute-api.ap-south-1.amazonaws.com";

const urlInput = document.getElementById("url");
const button = document.getElementById("shorten-btn");
const result = document.getElementById("result");

async function shorten() {
  const url = urlInput.value.trim();
  result.innerHTML = "";

  if (!url) {
    result.innerHTML = '<span class="error">Please enter a URL.</span>';
    return;
  }

  button.disabled = true;
  button.textContent = "Shortening...";

  try {
    const response = await fetch(API_URL + "/shorten", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url })
    });

    const text = await response.text();
    let data = {};
    try { data = JSON.parse(text); } catch (e) {}

    if (!response.ok) {
      const message = data.error || data.message || text || "Something went wrong.";
      result.innerHTML = '<span class="error"></span>';
      result.firstChild.textContent = message;
      return;
    }

    const link = document.createElement("a");
    link.href = data.short_url;
    link.target = "_blank";
    link.textContent = data.short_url;

    result.textContent = "Your short link: ";
    result.appendChild(link);
  } catch (err) {
    result.innerHTML = '<span class="error">Network error. Please try again.</span>';
  } finally {
    button.disabled = false;
    button.textContent = "Shorten";
  }
}

button.addEventListener("click", shorten);
urlInput.addEventListener("keydown", function (e) {
  if (e.key === "Enter") shorten();
});
