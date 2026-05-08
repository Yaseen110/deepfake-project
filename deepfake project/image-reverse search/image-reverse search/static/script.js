document.getElementById("upload-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const fileInput = document.getElementById("image-input");
    const uploadedImage = document.getElementById("uploaded-image");
    const previewBox = document.querySelector(".preview");
    const loading = document.getElementById("loading");
    const resultsContainer = document.getElementById("google-results");

    resultsContainer.innerHTML = ""; 
    loading.classList.remove("d-none");

    const formData = new FormData();
    formData.append("image", fileInput.files[0]);

    // Show uploaded image with animation
    const objectURL = URL.createObjectURL(fileInput.files[0]);
    uploadedImage.src = objectURL;
    previewBox.classList.remove("d-none");

    try {
        // Simulated delay for better UX
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Fetch response from Flask backend
        const response = await fetch("/search", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        loading.classList.add("d-none");
        displayResults(data);
    } catch (error) {
        console.error("Error:", error);
        loading.classList.add("d-none");
    }
});

function displayResults(data) {
    const resultsContainer = document.getElementById("google-results");
    resultsContainer.innerHTML = "";

    if (!data.google || data.google.length === 0) {
        resultsContainer.innerHTML = "<p class='text-danger'>No results found</p>";
        return;
    }

    data.google.forEach(result => {
        resultsContainer.innerHTML += `
            <div class="col-md-10 mb-4">
                <div class="card shadow-sm p-3">
                    <div class="row">
                        <div class="col-md-4">
                            <a href="${result.link}" target="_blank">
                                <img src="${result.thumbnail}" class="img-fluid">
                            </a>
                        </div>
                        <div class="col-md-8">
                            <h5>${result.title}</h5>
                            <table class="table table-bordered">
                                <tr><th>Domain</th><td>${result.whois.domain}</td></tr>
                                <tr><th>Registrar</th><td>${result.whois.registrar}</td></tr>
                                <tr><th>Created</th><td>${result.whois.creation_date}</td></tr>
                                <tr><th>Expires</th><td>${result.whois.expiration_date}</td></tr>
                                <tr><th>Updated</th><td>${result.whois.updated_date}</td></tr>
                                <tr><th>Emails</th><td>${result.whois.emails}</td></tr>
                                <tr><th>Country</th><td>${result.whois.country}</td></tr>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
}function displayResults(data) {
    const resultsContainer = document.getElementById("google-results");
    resultsContainer.innerHTML = "";

    if (!data.google || data.google.length === 0) {
        resultsContainer.innerHTML = "<p class='text-danger'>No results found</p>";
        return;
    }

    data.google.forEach(result => {
        resultsContainer.innerHTML += `
            <div class="col-md-10 mb-4">
                <div class="card shadow-lg p-4" style="background-color: #1e1e1e; color: #f1f1f1;">
                    <div class="row g-3 align-items-center">
                        <div class="col-md-4">
                            <a href="${result.link}" target="_blank">
                                <img src="${result.thumbnail || '/static/No_Image_Available.jpg'}" class="img-fluid rounded shadow" style="max-height: 250px; width: 100%; object-fit: cover;">
                            </a>
                        </div>
                        <div class="col-md-8">
                            <h5 class="fw-bold mb-2"><a href="${result.link}" target="_blank" style="color: #00bfff; text-decoration: none;">${result.title}</a></h5>
                            <table class="table table-dark table-striped table-bordered mt-2">
                                <tr><th scope="row">Domain</th><td>${result.whois.domain}</td></tr>
                                <tr><th scope="row">Registrar</th><td>${result.whois.registrar}</td></tr>
                                <tr><th scope="row">Emails</th><td>${Array.isArray(result.whois.emails) ? result.whois.emails.join(', ') : result.whois.emails}</td></tr>
                                <tr><th scope="row">Country</th><td>${result.whois.country}</td></tr>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
}


