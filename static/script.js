function predict() {
    fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            temperature: document.getElementById("temperature").value,
            humidity: document.getElementById("humidity").value,
            rainfall: document.getElementById("rainfall").value,
            soil_pH: document.getElementById("soil_pH").value
        })
    })
    .then(res => res.json())
    .then(data => {

    if (data.error) {
        alert("Backend Error: " + data.error);
        return;
    }
    // 🩺 Disease Status Agent
const diseaseEl = document.getElementById("diseaseStatus");
diseaseEl.innerText = data.disease_status;
diseaseEl.style.color = data.disease_status === "Diseased" ? "red" : "green";

// ⚠️ Risk Decision Agent
const statusText = document.getElementById("statusText");
statusText.innerText = data.status;
statusText.style.color = data.color;

// 📊 Confidence Agent
const confidenceEl = document.getElementById("confidenceText");
confidenceEl.innerText = data.confidence;
confidenceEl.style.color =
    data.confidence === "High" ? "green" :
    data.confidence === "Medium" ? "orange" : "red";



    // 📈 Risk Bar
    const riskFill = document.getElementById("riskFill");
    riskFill.style.width = data.risk_percentage + "%";
    riskFill.style.backgroundColor = data.color;

    document.getElementById("riskText").innerText =
        "Risk Percentage: " + data.risk_percentage + "%";

    // 🤖 Recommendation Agent
    const recList = document.getElementById("recommendations");
    recList.innerHTML = "";
    data.recommendations.forEach(r => {
        const li = document.createElement("li");
        li.innerText = r;
        recList.appendChild(li);
    });

})

    .catch(err => {
        console.error(err);
        alert("Frontend error. Check console.");
    });
}
