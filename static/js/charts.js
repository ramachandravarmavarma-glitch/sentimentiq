/**
 * SENTIMENTIQ - Chart.js Visualization Engine
 * Renders data-driven analytics powered by REAL SQLite database records.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Only execute on pages containing analytics charts
    const distCanvas = document.getElementById('sentimentDistChart');
    const polCanvas = document.getElementById('polarityDistChart');
    const subCanvas = document.getElementById('subjectivityDistChart');
    const timelineCanvas = document.getElementById('activityTimelineChart');

    if (!distCanvas && !polCanvas && !subCanvas && !timelineCanvas) {
        return;
    }

    // Set Chart.js Global Dark Theme Defaults
    if (window.Chart) {
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15, 23, 42, 0.92)';
        Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.12)';
        Chart.defaults.plugins.tooltip.borderWidth = 1;
        Chart.defaults.plugins.tooltip.titleFont = { weight: '600', family: "'Outfit', sans-serif" };
        Chart.defaults.plugins.tooltip.padding = 12;
        Chart.defaults.plugins.tooltip.cornerRadius = 8;
    }

    // Fetch live metrics from API
    fetch('/api/analytics-data')
        .then(response => {
            if (!response.ok) throw new Error('Failed to load analytics metrics.');
            return response.json();
        })
        .then(data => {
            initCharts(data);
        })
        .catch(err => {
            console.error('Error fetching analytics data:', err);
        });

    function initCharts(data) {
        // 1. Sentiment Distribution (Doughnut)
        if (distCanvas) {
            new Chart(distCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['Positive', 'Negative', 'Neutral'],
                    datasets: [{
                        data: [data.positive, data.negative, data.neutral],
                        backgroundColor: [
                            'rgba(16, 185, 129, 0.85)',
                            'rgba(244, 63, 94, 0.85)',
                            'rgba(6, 182, 212, 0.85)'
                        ],
                        borderColor: [
                            '#10b981',
                            '#f43f5e',
                            '#06b6d4'
                        ],
                        borderWidth: 2,
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '72%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true,
                                pointStyle: 'circle'
                            }
                        }
                    }
                }
            });
        }

        // 2. Polarity Distribution (Bar Chart)
        if (polCanvas && data.polarity_buckets) {
            const labels = Object.keys(data.polarity_buckets);
            const values = Object.values(data.polarity_buckets);

            new Chart(polCanvas, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Analysis Count',
                        data: values,
                        backgroundColor: [
                            'rgba(244, 63, 94, 0.75)',
                            'rgba(251, 146, 60, 0.75)',
                            'rgba(6, 182, 212, 0.75)',
                            'rgba(59, 130, 246, 0.75)',
                            'rgba(16, 185, 129, 0.75)'
                        ],
                        borderRadius: 8,
                        borderWidth: 1,
                        borderColor: 'rgba(255, 255, 255, 0.1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { font: { size: 11 } }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            beginAtZero: true,
                            ticks: { precision: 0 }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }

        // 3. Subjectivity Distribution (Bar Chart)
        if (subCanvas && data.subjectivity_buckets) {
            const labels = Object.keys(data.subjectivity_buckets);
            const values = Object.values(data.subjectivity_buckets);

            new Chart(subCanvas, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Count',
                        data: values,
                        backgroundColor: [
                            'rgba(14, 165, 233, 0.75)',
                            'rgba(99, 102, 241, 0.75)',
                            'rgba(139, 92, 246, 0.75)',
                            'rgba(168, 85, 247, 0.75)',
                            'rgba(217, 70, 239, 0.75)'
                        ],
                        borderRadius: 8,
                        borderWidth: 1,
                        borderColor: 'rgba(255, 255, 255, 0.1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { font: { size: 11 } }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            beginAtZero: true,
                            ticks: { precision: 0 }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }

        // 4. Analysis Activity Over Time (Smooth Line Chart)
        if (timelineCanvas && data.timeline) {
            const ctx = timelineCanvas.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            gradient.addColorStop(0, 'rgba(99, 102, 241, 0.45)');
            gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

            new Chart(timelineCanvas, {
                type: 'line',
                data: {
                    labels: data.timeline.labels.length > 0 ? data.timeline.labels : ['No Activity Recorded'],
                    datasets: [{
                        label: 'Analyses Logged',
                        data: data.timeline.counts.length > 0 ? data.timeline.counts : [0],
                        borderColor: '#818cf8',
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.35,
                        pointBackgroundColor: '#6366f1',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: { color: 'rgba(255, 255, 255, 0.04)' }
                        },
                        y: {
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            beginAtZero: true,
                            ticks: { precision: 0 }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }
    }
});
