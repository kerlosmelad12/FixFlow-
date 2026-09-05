const API_BASE = "http://localhost:5000/Fixflow-V1";

async function uploadError() {
  const query = document.getElementById("errorInput").value;
  const res = await fetch(`${API_BASE}/data/upload/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query })
  });
  const data = await res.json();
  document.getElementById("uploadResult").textContent = JSON.stringify(data, null, 2);
}

async function searchError() {
  const errorId = document.getElementById("searchId").value;
  const res = await fetch(`${API_BASE}/data/search/${errorId}`);
  const data = await res.json();
  document.getElementById("searchResult").textContent = JSON.stringify(data, null, 2);
}

async function getAnswer(forceRefresh = false, errorIdOverride = null) {
  // Allows callers like submitFeedback() to trigger a regenerate for a
  // specific error id without depending on whatever happens to be typed
  // into the separate "Get Answer" section's input field.
  const errorId = errorIdOverride ?? document.getElementById("answerId").value;

  if (!errorId) {
    document.getElementById("answerResult").textContent =
      "Error: no Error ID provided to getAnswer().";
    return;
  }

  // force_refresh is a plain bool query param on the FastAPI route (not part
  // of the SimilarErrorsRequest body model), so it must be sent in the URL,
  // not inside the JSON body — otherwise the backend always sees the default
  // (False) and "Generate New Answer" silently behaves like "Get Answer".
  const url = `${API_BASE}/nlp/answer/${errorId}?force_refresh=${forceRefresh}`;

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        pagesize: 5,
        min_similarity: 0.5,
        limit: 10
      })
    });
    const data = await res.json();
    document.getElementById("answerResult").textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    document.getElementById("answerResult").textContent = `Request failed: ${err.message}`;
  }
}

async function submitFeedback() {
  const errorId = document.getElementById("feedbackId").value;
  const feedbackText = document.getElementById("feedbackText").value;
  const score = parseInt(document.getElementById("feedbackScore").value, 10);

  const res = await fetch(`${API_BASE}/nlp/answer/${errorId}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ feedback_text: feedbackText, score })
  });
  const data = await res.json();

  document.getElementById("feedbackResult").textContent = JSON.stringify(data, null, 2);

  if (data.rating && data.rating < 3) {
    document.getElementById("feedbackResult").textContent += "\n\nFeedback is poor → Generating new answer...";
    await getAnswer(true, errorId);
  }
}

async function getSimilarErrors() {
  const errorId = document.getElementById("similarId").value;
  // Fixed typo: backend route is /nlp/similar/{error_id}, not /nlp/similer/{error_id}
  const res = await fetch(`${API_BASE}/nlp/similar/${errorId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pagesize: 5, min_similarity: 0.5, limit: 10 })
  });
  const data = await res.json();
  document.getElementById("similarResult").textContent = JSON.stringify(data, null, 2);
}