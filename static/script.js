document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('textInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultContainer = document.getElementById('result');
    const sentimentBadge = document.getElementById('sentimentBadge');
    const polarityValue = document.getElementById('polarityValue');
    const analysisText = document.getElementById('analysisText');
    const historyList = document.getElementById('historyList');

    // Keyboard shortcut: Enter (Ctrl+Enter or Cmd+Enter) to analyze
    textInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            analyzeBtn.click();
        }
    });

    // Auto-resize textarea
    textInput.addEventListener('input', () => {
        textInput.style.height = 'auto';
        textInput.style.height = textInput.scrollHeight + 'px';
    });

    analyzeBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();

        if (!text) {
            showNotification('Please enter some text to analyze.', 'warning');
            textInput.focus();
            return;
        }

        // Loading state with animation
        analyzeBtn.innerText = '✨ Analyzing...';
        analyzeBtn.disabled = true;
        analyzeBtn.classList.add('loading');

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            displayResult(data);
            addToHistory(data);

            // Smooth scroll to results
            setTimeout(() => {
                resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 100);

        } catch (error) {
            console.error('Error:', error);
            showNotification('An error occurred while analyzing the text. Please try again.', 'error');
        } finally {
            analyzeBtn.innerText = '🔍 Analyze Sentiment';
            analyzeBtn.disabled = false;
            analyzeBtn.classList.remove('loading');
        }
    });

    function displayResult(data) {
        resultContainer.classList.remove('hidden');

        // Update values with animation
        animateValue(polarityValue, 0, data.polarity, 800);

        // Subjectivity
        const subjectivityValue = document.getElementById('subjectivityValue');
        if (subjectivityValue) {
            animateValue(subjectivityValue, 0, data.subjectivity !== undefined ? data.subjectivity : 0, 800);
        }

        sentimentBadge.textContent = data.sentiment;

        // Update text preview (truncated)
        analysisText.textContent = `Analyzed: "${data.text.substring(0, 80)}${data.text.length > 80 ? '...' : ''}"`;

        // Update Badge Styles with animation
        sentimentBadge.className = 'sentiment-badge'; // Reset classes
        if (data.sentiment === 'Positive') {
            sentimentBadge.classList.add('sentiment-positive');
        } else if (data.sentiment === 'Negative') {
            sentimentBadge.classList.add('sentiment-negative');
        } else {
            sentimentBadge.classList.add('sentiment-neutral');
        }

        // Handle Emotions
        const emotionsContainer = document.getElementById('emotionsContainer');
        const emotionsList = document.getElementById('emotionsList');
        emotionsList.innerHTML = ''; // Clear previous

        // Check if we have any complex emotions detected
        const emotions = data.emotions || {};
        const emotionKeys = Object.keys(emotions);

        if (emotionKeys.length > 0) {
            emotionsContainer.classList.remove('hidden');

            // Sort emotions by percentage (descending)
            emotionKeys.sort((a, b) => emotions[b] - emotions[a]);

            emotionKeys.forEach((emotion, index) => {
                const percentage = emotions[emotion];

                const emotionItem = document.createElement('div');
                emotionItem.className = 'emotion-item';
                emotionItem.style.animationDelay = `${index * 0.1}s`;

                emotionItem.innerHTML = `
                    <div class="emotion-info">
                        <span class="emotion-name">${emotion}</span>
                        <span class="emotion-percent">${percentage}%</span>
                    </div>
                    <div class="emotion-bar-bg">
                        <div class="emotion-bar-fill" style="width: 0%" data-width="${percentage}%"></div>
                    </div>
                `;
                emotionsList.appendChild(emotionItem);

                // Animate bar fill
                setTimeout(() => {
                    const barFill = emotionItem.querySelector('.emotion-bar-fill');
                    barFill.style.width = barFill.dataset.width;
                }, 50 + (index * 100));
            });
        } else {
            emotionsContainer.classList.add('hidden');
        }

        // Handle Sentence Breakdown
        const sentencesContainer = document.getElementById('sentencesContainer');
        const sentencesList = document.getElementById('sentencesList');
        if (sentencesContainer && sentencesList) {
            sentencesList.innerHTML = ''; // Clear previous

            const breakdown = data.sentence_breakdown || [];
            if (breakdown.length > 0) {
                sentencesContainer.classList.remove('hidden');

                breakdown.forEach((sentenceData, index) => {
                    const sentenceItem = document.createElement('div');
                    sentenceItem.className = 'sentence-item';
                    sentenceItem.style.animationDelay = `${index * 0.1}s`;

                    // Determine emotion string
                    const sentEmotions = sentenceData.emotions || {};
                    const sentEmotionKeys = Object.keys(sentEmotions);
                    let emotionStr = '';
                    if (sentEmotionKeys.length > 0) {
                        emotionStr = sentEmotionKeys.map(k => `${k} (${sentEmotions[k]}%)`).join(', ');
                    } else {
                        emotionStr = 'No specific emotions detected';
                    }

                    sentenceItem.innerHTML = `
                        <p class="sentence-text">"${sentenceData.text}"</p>
                        <div class="sentence-meta">
                            <span class="sentence-badge ${sentenceData.sentiment === 'Positive' ? 'pos' : sentenceData.sentiment === 'Negative' ? 'neg' : 'neu'}">${sentenceData.sentiment}</span>
                            <span class="sentence-emotion">${emotionStr}</span>
                        </div>
                    `;
                    sentencesList.appendChild(sentenceItem);
                });

            } else {
                sentencesContainer.classList.add('hidden');
            }
        }
    }

    function addToHistory(data) {
        const noHistoryMsg = document.querySelector('.no-history');
        if (noHistoryMsg) {
            noHistoryMsg.remove();
        }

        const item = document.createElement('div');
        item.className = 'history-item';

        // Short label
        let label = 'Neu';
        if (data.sentiment === 'Positive') label = 'Pos';
        if (data.sentiment === 'Negative') label = 'Neg';

        item.innerHTML = `
            <span class="history-text" title="${data.text}">${data.text}</span>
            <span class="history-badge ${label}">${data.sentiment}</span>
        `;

        // Click to reanalyze
        item.addEventListener('click', () => {
            textInput.value = data.text;
            textInput.focus();
            textInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });

        // Prepend to list
        historyList.insertBefore(item, historyList.firstChild);

        // Limit history to 10 items
        const historyItems = historyList.querySelectorAll('.history-item');
        if (historyItems.length > 10) {
            historyItems[historyItems.length - 1].remove();
        }
    }

    // Utility: Animate number values
    function animateValue(element, start, end, duration) {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = current.toFixed(2);
        }, 16);
    }

    // Utility: Show notification
    function showNotification(message, type = 'info') {
        // Simple alert for now - can be enhanced with custom toast notifications
        alert(message);
    }
});
