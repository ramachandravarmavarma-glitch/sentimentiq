/**
 * SENTIMENTIQ - Text Analysis Workspace Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('analysisInput');
    const charCountEl = document.getElementById('charCount');
    const wordCountEl = document.getElementById('wordCount');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const clearBtn = document.getElementById('clearBtn');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const resultPanel = document.getElementById('resultPanel');
    const emptyStatePanel = document.getElementById('emptyStatePanel');

    // Example Presets
    const examples = {
        positive: "SentimentIQ delivers extraordinary accuracy and an incredibly sleek analytics experience! The real-time telemetry is brilliant, intuitive, and genuinely delightful to work with.",
        negative: "This is a terribly disappointing and frustrating bug-ridden system. It constantly crashed during execution, ruined my report, and customer assistance was exceptionally rude.",
        neutral: "The quarterly operational review was submitted by the data processing division at 15:30 UTC. The document covers departmental expenditures across the past six calendar months."
    };

    // Update Counters
    function updateCounters() {
        if (!textInput) return;
        const text = textInput.value;
        const chars = text.length;
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;

        if (charCountEl) charCountEl.textContent = chars.toLocaleString();
        if (wordCountEl) wordCountEl.textContent = words.toLocaleString();

        if (analyzeBtn) {
            analyzeBtn.disabled = text.trim().length === 0;
        }
    }

    if (textInput) {
        textInput.addEventListener('input', updateCounters);
        updateCounters();
    }

    // Example Chip Buttons
    document.querySelectorAll('.example-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const type = chip.getAttribute('data-example');
            if (examples[type] && textInput) {
                textInput.value = examples[type];
                updateCounters();
                textInput.focus();
                // Smooth highlight pulse
                textInput.style.borderColor = '#6366f1';
                setTimeout(() => {
                    textInput.style.borderColor = '';
                }, 800);
            }
        });
    });

    // Clear Workspace Button
    if (clearBtn && textInput) {
        clearBtn.addEventListener('click', () => {
            textInput.value = '';
            updateCounters();
            textInput.focus();
        });
    }

    // Analyze Action
    if (analyzeBtn && textInput) {
        analyzeBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const text = textInput.value.trim();
            if (!text) {
                showToast("Please enter or paste text to analyze.", "warning");
                return;
            }

            // Show Loading Animation
            if (loadingOverlay) loadingOverlay.style.display = 'flex';
            analyzeBtn.disabled = true;

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ text: text })
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.error || "Unable to analyze the text.");
                }

                // Render dynamic results
                renderResults(data);

                // Success Toast
                showToast("Sentiment analysis completed.", "success");

            } catch (err) {
                console.error(err);
                showToast(err.message || "Unable to analyze the text.", "danger");
            } finally {
                if (loadingOverlay) loadingOverlay.style.display = 'none';
                analyzeBtn.disabled = false;
            }
        });
    }

    // Render Analysis Result into the DOM
    function renderResults(data) {
        if (emptyStatePanel) emptyStatePanel.style.display = 'none';
        if (resultPanel) {
            resultPanel.style.display = 'block';
            resultPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        // Sentiment Badge
        const badgeEl = document.getElementById('resSentimentBadge');
        if (badgeEl) {
            badgeEl.className = 'badge-sentiment';
            if (data.sentiment === 'POSITIVE') {
                badgeEl.classList.add('badge-pos');
            } else if (data.sentiment === 'NEGATIVE') {
                badgeEl.classList.add('badge-neg');
            } else {
                badgeEl.classList.add('badge-neu');
            }
            badgeEl.textContent = data.sentiment;
        }

        // Polarity Score & Nuance
        const polValEl = document.getElementById('resPolarityVal');
        const polNuanceEl = document.getElementById('resPolarityNuance');
        const polPinEl = document.getElementById('resPolarityPin');

        if (polValEl) {
            polValEl.textContent = data.polarity_display;
            polValEl.style.color = data.polarity > 0.1 ? '#10b981' : (data.polarity < -0.1 ? '#f43f5e' : '#06b6d4');
        }
        if (polNuanceEl) polNuanceEl.textContent = data.polarity_nuance;
        if (polPinEl) polPinEl.style.left = `${data.polarity_percent}%`;

        // Subjectivity Score & Nuance
        const subValEl = document.getElementById('resSubjectivityVal');
        const subNuanceEl = document.getElementById('resSubjectivityNuance');
        const subPinEl = document.getElementById('resSubjectivityPin');

        if (subValEl) subValEl.textContent = data.subjectivity_display;
        if (subNuanceEl) subNuanceEl.textContent = data.subjectivity_nuance;
        if (subPinEl) subPinEl.style.left = `${data.subjectivity_percent}%`;

        // Metadata Counts
        const wordEl = document.getElementById('resWordCount');
        const charEl = document.getElementById('resCharCount');
        const sentEl = document.getElementById('resSentenceCount');
        const timeEl = document.getElementById('resTimestamp');

        if (wordEl) wordEl.textContent = data.word_count;
        if (charEl) charEl.textContent = data.char_count;
        if (sentEl) sentEl.textContent = data.sentence_count;
        if (timeEl) timeEl.textContent = data.date_formatted || 'Just now';

        // Sentence-by-sentence Breakdown
        const sentenceListEl = document.getElementById('resSentenceList');
        if (sentenceListEl && data.sentences && data.sentences.length > 0) {
            let html = '';
            data.sentences.forEach((s, idx) => {
                let badgeClass = s.sentiment === 'POSITIVE' ? 'badge-pos' : (s.sentiment === 'NEGATIVE' ? 'badge-neg' : 'badge-neu');
                html += `
                    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 0.85rem 1rem; margin-bottom: 0.65rem;">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <span style="font-size: 0.78rem; font-weight: 600; color: #94a3b8;">Sentence #${idx + 1}</span>
                            <span class="badge-sentiment ${badgeClass}" style="font-size: 0.7rem; padding: 0.2rem 0.5rem;">${s.sentiment} (${s.polarity_display})</span>
                        </div>
                        <p style="margin: 0; font-size: 0.9rem; color: #e2e8f0; line-height: 1.5;">"${escapeHtml(s.sentence)}"</p>
                    </div>
                `;
            });
            sentenceListEl.innerHTML = html;
        }

        // Re-run Lucide icons
        if (window.lucide) {
            window.lucide.createIcons();
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});
