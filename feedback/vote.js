(function () {
  const params = new URLSearchParams(window.location.search);
  const topic = params.get("topic");
  const vote = params.get("vote");
  const date = params.get("date");

  const statusEl = document.getElementById("status");

  if (!topic || !vote || !date) {
    statusEl.textContent = "Invalid vote link.";
    return;
  }

  const OWNER = "crackerhands";
  const REPO = "daily-news-digest";
  const WORKFLOW_ID = "record_vote.yml";
  // This token is a fine-grained PAT with only actions:write on this repo.
  // Worst case: someone triggers your personal digest vote workflow.
  const TOKEN = window.__VOTE_TOKEN__;

  if (!TOKEN) {
    statusEl.textContent = "Vote token not configured.";
    return;
  }

  statusEl.textContent = "Recording your vote...";

  fetch(
    `https://api.github.com/repos/${OWNER}/${REPO}/actions/workflows/${WORKFLOW_ID}/dispatches`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${TOKEN}`,
        "Content-Type": "application/json",
        Accept: "application/vnd.github+json",
      },
      body: JSON.stringify({
        ref: "main",
        inputs: { topic, vote },
      }),
    }
  )
    .then((res) => {
      if (res.status === 204) {
        const emoji = vote === "up" ? "👍" : "👎";
        statusEl.textContent = `${emoji} Vote recorded for "${topic}". Thanks!`;
      } else {
        statusEl.textContent = `Error recording vote (status ${res.status}).`;
      }
    })
    .catch(() => {
      statusEl.textContent = "Network error. Vote not recorded.";
    });
})();
