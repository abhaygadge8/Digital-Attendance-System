async function postJson(url) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" }
    });
    return response.json();
}

async function refreshCameraStatus() {
    if (!window.cameraStatusUrl) {
        return;
    }

    const response = await fetch(window.cameraStatusUrl);
    const data = await response.json();

    const statusElement = document.getElementById("recognitionStatus");
    if (statusElement) {
        statusElement.textContent = data.last_event;
    }

    const present = document.getElementById("presentCount");
    const absent = document.getElementById("absentCount");
    const records = document.getElementById("recordsCount");

    if (present) present.textContent = data.summary.present_count;
    if (absent) absent.textContent = data.summary.absent_count;
    if (records) records.textContent = data.summary.records_count;
}

document.addEventListener("DOMContentLoaded", () => {
    const startBtn = document.getElementById("startRecognition");
    const stopBtn = document.getElementById("stopRecognition");

    if (startBtn) {
        startBtn.addEventListener("click", async () => {
            await postJson(window.cameraStartUrl);
            refreshCameraStatus();
        });
    }

    if (stopBtn) {
        stopBtn.addEventListener("click", async () => {
            await postJson(window.cameraStopUrl);
            refreshCameraStatus();
        });
    }

    if (window.cameraStatusUrl) {
        refreshCameraStatus();
        setInterval(refreshCameraStatus, 3000);
    }
});
