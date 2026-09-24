document.addEventListener("DOMContentLoaded", function () {
    // -----------------------------------------------------------------
    // 1. Automatically hide alert messages smoothly
    // -----------------------------------------------------------------
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-6px)";
            setTimeout(function () {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, 400);
        }, 4000);
    });

    // -----------------------------------------------------------------
    // 2. Real-time Unit & Cost Calculation Preview in Bill Generator
    // -----------------------------------------------------------------
    const prevInput = document.getElementById("previous_reading");
    const currInput = document.getElementById("current_reading");
    const previewBox = document.getElementById("livePreview");
    const previewUnits = document.getElementById("previewUnits");
    const previewAmount = document.getElementById("previewAmount");
    const previewError = document.getElementById("previewError");

    function calculateBillAmount(units) {
        let amount = 0;
        if (units <= 100) {
            amount = units * 1.50;
        } else if (units <= 200) {
            amount = (100 * 1.50) + ((units - 100) * 2.50);
        } else if (units <= 400) {
            amount = (100 * 1.50) + (100 * 2.50) + ((units - 200) * 4.00);
        } else {
            amount = (100 * 1.50) + (100 * 2.50) + (200 * 4.00) + ((units - 400) * 6.00);
        }
        return Math.round(amount * 100) / 100;
    }

    function updateLiveCalculation() {
        if (!prevInput || !currInput || !previewBox) return;

        const prevVal = parseFloat(prevInput.value);
        const currVal = parseFloat(currInput.value);

        if (!isNaN(prevVal) && !isNaN(currVal)) {
            previewBox.style.display = "block";

            if (currVal < prevVal) {
                previewError.style.display = "block";
                previewUnits.textContent = "0.00";
                previewAmount.textContent = "₹0.00";
            } else {
                previewError.style.display = "none";
                const units = Math.round((currVal - prevVal) * 100) / 100;
                const cost = calculateBillAmount(units);
                previewUnits.textContent = units.toFixed(2);
                previewAmount.textContent = "₹" + cost.toFixed(2);
            }
        } else {
            previewBox.style.display = "none";
        }
    }

    if (prevInput && currInput) {
        prevInput.addEventListener("input", updateLiveCalculation);
        currInput.addEventListener("input", updateLiveCalculation);
    }
});