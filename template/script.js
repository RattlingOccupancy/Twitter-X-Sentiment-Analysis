// initialize state variables for chart visibility and timers
let currentVisibleIndividualChart = false;
let hideTimeoutRef = null;
let hoverTimer = null;

// handle all frontend functionalities after the dom is loaded
document.addEventListener('DOMContentLoaded', function () {
    // get canvas element for starfield animation
    const canvas = document.getElementById('starfield');
    const ctx = canvas.getContext('2d');

    // set canvas dimensions to match window size
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // define star properties
    const stars = [];
    const starCount = Math.floor((window.innerWidth * window.innerHeight) / 1000);
    let mouseX = 0;
    let mouseY = 0;

    // initialize stars with random positions, sizes, and speeds
    function initStars() {
        stars.length = 0; 
        const newStarCount = Math.floor((window.innerWidth * window.innerHeight) / 1000);
        for (let i = 0; i < newStarCount; i++) {
            stars.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                size: Math.random() * 2 + 0.5,
                opacity: Math.random() * 0.8 + 0.2,
                speed: (Math.random() * 0.05 + 0.01) * 0.2
            });
        }
    }

    // draw stars on canvas with glow and parallax effect
    function drawStars() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // create gradient background
        const gradientBg = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradientBg.addColorStop(0, '#0c0c16');
        gradientBg.addColorStop(1, '#1a1a2e');
        ctx.fillStyle = gradientBg;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // draw each star and update position
        for (let i = 0; i < stars.length; i++) {
            const star = stars[i];

            // move stars based on mouse position to create parallax effect
            star.x += (mouseX - canvas.width / 2) * star.speed;
            star.y += (mouseY - canvas.height / 2) * star.speed;

            // wrap stars around the screen when they go out of bounds
            if (star.x < 0) star.x = canvas.width;
            if (star.x > canvas.width) star.x = 0;
            if (star.y < 0) star.y = canvas.height;
            if (star.y > canvas.height) star.y = 0;

            // create glowing star effect
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);

            const starGradient = ctx.createRadialGradient(
                star.x, star.y, 0,
                star.x, star.y, star.size * 2
            );
            starGradient.addColorStop(0, `rgba(255, 255, 255, ${star.opacity})`);
            starGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

            ctx.fillStyle = starGradient;
            ctx.fill();
        }

        // add ambient glow effect based on mouse position
        const ambientGlow = ctx.createRadialGradient(
            mouseX, mouseY, 0,
            mouseX, mouseY, canvas.width / 2
        );
        ambientGlow.addColorStop(0, 'rgba(0, 219, 222, 0.03)');
        ambientGlow.addColorStop(0.5, 'rgba(252, 0, 255, 0.01)');
        ambientGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');

        ctx.fillStyle = ambientGlow;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        requestAnimationFrame(drawStars);
    }

    // track mouse position and update search box glow accordingly
    document.addEventListener('mousemove', function (e) {
        mouseX = e.clientX;
        mouseY = e.clientY;

        const searchBox = document.getElementById('searchBox');
        if (searchBox) {
            const glowEffect = searchBox.querySelector('.glow-effect');
            if (glowEffect) {
                glowEffect.style.setProperty('--x', mouseX + 'px');
                glowEffect.style.setProperty('--y', mouseY + 'px');
            }
        }
    });

    // handle window resizing by reinitializing stars
    window.addEventListener('resize', function () {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        initStars();
    });

    // initialize and start starfield animation
    initStars();
    drawStars();

    // get references to ui elements
    const analyzeBtn = document.getElementById('analyzeBtn');
    const topicInput = document.getElementById('topicInput');
    const loadingBox = document.getElementById('loadingBox');
    const resultsBox = document.getElementById('resultsBox');
    const errorBox = document.getElementById('errorBox');
    const sentimentSummaryContainer = document.getElementById('sentimentSummary');
    const hashtagEl = resultsBox.querySelector('.hashtag');
    const dominantSentimentEl = resultsBox.querySelector('.dominant-sentiment');

    // individual emotion chart elements
    const individualEmotionChartEl = document.getElementById('individualEmotionChart');
    const individualEmotionNameEl = document.getElementById('individualEmotionName');
    const individualEmotionBarEl = document.getElementById('individualEmotionBar');
    const individualEmotionPercentageEl = document.getElementById('individualEmotionPercentage');

    // keep the chart visible if mouse enters chart container
    individualEmotionChartEl.addEventListener('mouseenter', () => {
        if (hoverTimer) clearTimeout(hoverTimer);
    });

    // hide the chart when mouse leaves chart container
    individualEmotionChartEl.addEventListener('mouseleave', () => {
        hideIndividualEmotionGraph();
    });

    // show individual emotion chart with animation
    function showIndividualEmotionGraph(emotionName, percentage) {
        if (hideTimeoutRef) {
            clearTimeout(hideTimeoutRef);
            hideTimeoutRef = null;
        }

        const capitalizedEmotion = emotionName.charAt(0).toUpperCase() + emotionName.slice(1);
        individualEmotionNameEl.textContent = `${capitalizedEmotion} Detail`;
        individualEmotionBarEl.style.height = `${percentage}%`;
        individualEmotionPercentageEl.textContent = `${percentage.toFixed(2)}%`;

        individualEmotionChartEl.style.display = 'block';

        setTimeout(() => {
            individualEmotionChartEl.style.opacity = '1';
            individualEmotionChartEl.style.transform = 'translateY(0)';
        }, 10);

        currentVisibleIndividualChart = true;
    }

    // hide individual emotion chart with delay
    function hideIndividualEmotionGraph() {
        hoverTimer = setTimeout(() => {
            individualEmotionChartEl.style.opacity = '0';
            individualEmotionChartEl.style.transform = 'translateY(10px)';
            setTimeout(() => {
                individualEmotionChartEl.style.display = 'none';
            }, 300);
        }, 100);
    }

    // handle analyze button click and fetch results from backend
    analyzeBtn.addEventListener('click', function () {
        const topic = topicInput.value.trim();

        if (topic) {
            // show loader and reset ui
            loadingBox.style.display = 'block';
            resultsBox.style.display = 'none';
            errorBox.style.display = 'none';
            if (individualEmotionChartEl) individualEmotionChartEl.style.display = 'none';
            currentVisibleIndividualChart = false;

            fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: topic })
            })
                .then(response => response.json())
                .then(data => {
                    loadingBox.style.display = 'none';

                    if (data.success) {
                        resultsBox.style.display = 'block';
                        hashtagEl.textContent = ' result for #' + topic.replace(/\s+/g, '');

                        sentimentSummaryContainer.innerHTML = ''; 

                        const emotions = data.emotion_percentages;
                        const counts = data.emotion_counts;

                        // dynamically generate sentiment cards
                        for (const emotion in emotions) {
                            const percent = emotions[emotion];
                            const count = counts[emotion];

                            const card = document.createElement('div');
                            card.className = 'sentiment-card';
                            card.dataset.emotion = emotion;
                            card.dataset.percentage = percent.toFixed(2);

                            card.innerHTML = `
                                <div class="percent">${percent.toFixed(2)}%</div>
                                <div class="count">${count} ${emotion.charAt(0).toUpperCase() + emotion.slice(1)} Tweets</div>
                            `;

                            // show graph on hover
                            card.addEventListener('mouseenter', () => {
                                if (hoverTimer) clearTimeout(hoverTimer);
                                showIndividualEmotionGraph(card.dataset.emotion, parseFloat(card.dataset.percentage));
                            });

                            // hide graph when leaving card
                            card.addEventListener('mouseleave', () => {
                                hideIndividualEmotionGraph();
                            });

                            // on mobile, show graph on click instead
                            card.addEventListener('click', () => {
                                showIndividualEmotionGraph(card.dataset.emotion, parseFloat(card.dataset.percentage));
                            });

                            sentimentSummaryContainer.appendChild(card);
                        }

                        // show dominant emotion
                        dominantSentimentEl.textContent =
                            'dominant emotion: ' + data.dominant.charAt(0).toUpperCase() + data.dominant.slice(1);

                        // add smooth transition effect
                        resultsBox.style.opacity = '0';
                        resultsBox.style.transform = 'translateY(20px)';
                        setTimeout(() => {
                            resultsBox.style.transition = 'opacity 0.5s, transform 0.5s';
                            resultsBox.style.opacity = '1';
                            resultsBox.style.transform = 'translateY(0)';
                        }, 50);

                    } else {
                        // show error if backend returns failure
                        errorBox.style.display = 'block';
                        errorBox.textContent = data.error || 'error analyzing the topic. please try again.';

                        setTimeout(() => {
                            errorBox.style.display = 'none';
                        }, 5000);
                    }
                })
                .catch(error => {
                    // handle network failures gracefully
                    loadingBox.style.display = 'none';
                    errorBox.style.display = 'block';
                    errorBox.textContent = 'network error. please check your connection and try again.';

                    setTimeout(() => {
                        errorBox.style.display = 'none';
                    }, 5000);
                });
        } else {
            // show error if topic input is empty
            errorBox.style.display = 'block';
            errorBox.textContent = 'please enter a topic to analyze';

            setTimeout(() => {
                errorBox.style.display = 'none';
            }, 3000);
        }
    });

    // add focus/blur styles for input field
    const input = document.getElementById('topicInput');
    input.addEventListener('focus', function () {
        this.parentElement.classList.add('input-focus');
    });

    input.addEventListener('blur', function () {
        this.parentElement.classList.remove('input-focus');
    });
});
