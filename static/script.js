document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('prediction-form');
    const stateSelect = document.getElementById('state');
    const companySelect = document.getElementById('company');
    const modelSelect = document.getElementById('model');
    const fuelSelect = document.getElementById('fuel_type');
    
    const accidentSlider = document.getElementById('accident_score');
    const accidentVal = document.getElementById('accident_val');
    
    const resultPlaceholder = document.getElementById('result-placeholder');
    const resultContent = document.getElementById('result-content');
    const predictedPriceDisplay = document.getElementById('predicted-price');
    const meterFill = document.getElementById('meter-fill');
    const depreciationInfo = document.getElementById('depreciation-info');
    
    const r2ScoreDisplay = document.getElementById('r2-score');
    const maeScoreDisplay = document.getElementById('mae-score');
    
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = submitBtn.querySelector('.loader');

    let apiOptions = null;

    // Format currency
    const formatCurrency = (value) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(value);
    };

    // Initialize Options
    const initializeOptions = async () => {
        try {
            const response = await fetch('/options');
            apiOptions = await response.json();
            
            // Populate States
            apiOptions.locations.forEach(state => {
                const option = document.createElement('option');
                option.value = state;
                option.textContent = state;
                stateSelect.appendChild(option);
            });
            
            // Populate Companies
            Object.keys(apiOptions.companies_and_models).forEach(company => {
                const option = document.createElement('option');
                option.value = company;
                option.textContent = company;
                companySelect.appendChild(option);
            });
            
            // Populate Fuel Types
            apiOptions.fuel_types.forEach(fuel => {
                const option = document.createElement('option');
                option.value = fuel;
                option.textContent = fuel;
                fuelSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Failed to load options', error);
        }
    };

    // Initialize Metrics
    const initializeMetrics = async () => {
        try {
            const response = await fetch('/metrics');
            const data = await response.json();
            if(data.R2) r2ScoreDisplay.textContent = data.R2;
            if(data.MAE) maeScoreDisplay.textContent = `₹ ${data.MAE}`;
        } catch (error) {
            console.error('Failed to load metrics', error);
        }
    };

    // Events
    accidentSlider.addEventListener('input', (e) => {
        accidentVal.textContent = e.target.value;
    });

    companySelect.addEventListener('change', (e) => {
        const company = e.target.value;
        const models = apiOptions.companies_and_models[company] || [];
        
        modelSelect.innerHTML = '<option value="" disabled selected>Select Model</option>';
        modelSelect.disabled = false;
        
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            modelSelect.appendChild(option);
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // UI State
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        submitBtn.disabled = true;
        
        const formData = new FormData(form);
        const requestData = Object.fromEntries(formData.entries());
        
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Formatting results
                predictedPriceDisplay.textContent = formatCurrency(result.predicted_price);
                
                // Meter Logic (Rough heuristic of condition based on retention)
                const originalPrice = parseFloat(requestData.original_price);
                const retention = result.predicted_price / originalPrice;
                // Cap retention mapping (10% to 90% mapping to 0-100% width)
                let pct = ((retention - 0.1) / 0.8) * 100;
                pct = Math.max(5, Math.min(100, pct));
                meterFill.style.width = `${pct}%`;
                
                // Color Logic
                if (pct < 30) meterFill.style.background = 'var(--danger-color)';
                else if (pct < 60) meterFill.style.background = '#f59e0b';
                else meterFill.style.background = 'var(--accent-color)';

                // Depreciation logic note
                // Using 2024 as the baseline year for dataset generation
                const age = 2024 - parseInt(requestData.year);
                const lostValue = originalPrice - result.predicted_price;
                const pctLost = ((lostValue/originalPrice)*100).toFixed(0);
                
                depreciationInfo.innerHTML = `Your car has depreciated by <strong>${pctLost}%</strong> (₹ ${formatCurrency(lostValue)}) over ${age} years due to age, mileage, and condition.`;

                resultPlaceholder.classList.add('hidden');
                resultContent.classList.remove('hidden');
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error(error);
            alert("An error occurred during prediction.");
        } finally {
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            submitBtn.disabled = false;
        }
    });

    // Boot
    initializeOptions();
    initializeMetrics();
});
