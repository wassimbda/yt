// Charts.js - Advanced Chart Implementations for YouTube Title Analyzer
document.addEventListener('DOMContentLoaded', function() {
    // Set up Chart.js defaults for Arabic
    Chart.defaults.font.family = 'Tajawal, Cairo, sans-serif';
    Chart.defaults.plugins.legend.rtl = true;
    Chart.defaults.plugins.legend.textDirection = 'rtl';
});

// Initialize performance radar chart
function initializePerformanceChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');
    
    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['صورة القناة', 'الصور المصغرة', 'تحسين العناوين', 'استراتيجية المحتوى'],
            datasets: [{
                label: 'درجة الأداء',
                data: [
                    data.channelArt || 0,
                    data.thumbnails || 0,
                    data.titles || 0,
                    ((data.channelArt || 0) + (data.thumbnails || 0) + (data.titles || 0)) / 3
                ],
                backgroundColor: 'rgba(37, 99, 235, 0.2)',
                borderColor: 'rgba(37, 99, 235, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(37, 99, 235, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(37, 99, 235, 1)',
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    pointLabels: {
                        font: {
                            family: 'Tajawal',
                            size: 12
                        },
                        color: '#374151'
                    },
                    ticks: {
                        display: true,
                        stepSize: 2,
                        min: 0,
                        max: 10,
                        backdropColor: 'transparent',
                        color: '#6b7280',
                        font: {
                            family: 'Tajawal',
                            size: 10
                        }
                    },
                    suggestedMin: 0,
                    suggestedMax: 10
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    titleFont: {
                        family: 'Tajawal'
                    },
                    bodyFont: {
                        family: 'Tajawal'
                    },
                    callbacks: {
                        label: function(context) {
                            return context.parsed.r.toFixed(1) + '/10';
                        }
                    }
                }
            },
            elements: {
                line: {
                    tension: 0.2
                }
            }
        }
    });
}

// Initialize score distribution doughnut chart
function initializeScoreDistributionChart(canvasId, data = null) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');
    
    // Default distribution if no data provided
    const defaultData = [25, 35, 30, 10];
    const chartData = data || defaultData;
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['ممتاز (8-10)', 'جيد (6-8)', 'متوسط (4-6)', 'ضعيف (0-4)'],
            datasets: [{
                data: chartData,
                backgroundColor: [
                    '#10b981', // Green for excellent
                    '#3b82f6', // Blue for good  
                    '#f59e0b', // Yellow for average
                    '#ef4444'  // Red for poor
                ],
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverBorderWidth: 3,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    rtl: true,
                    labels: {
                        font: {
                            family: 'Tajawal',
                            size: 12
                        },
                        color: '#374151',
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    titleFont: {
                        family: 'Tajawal'
                    },
                    bodyFont: {
                        family: 'Tajawal'
                    },
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return label + ': ' + percentage + '%';
                        }
                    }
                }
            }
        }
    });
}

// Initialize title analysis radar chart
function initializeTitleAnalysisChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');
    
    return new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['الجاذبية', 'التأثير العاطفي', 'قوة الكلمات', 'الشمولية'],
            datasets: [{
                label: 'درجة التحليل',
                data: [
                    (data.attractiveness || 0) / 10, // Convert to 0-10 scale
                    data.emotional || 0,
                    data.keyword || 0,
                    ((data.attractiveness || 0) / 10 + (data.emotional || 0) + (data.keyword || 0)) / 3
                ],
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(59, 130, 246, 1)',
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    pointLabels: {
                        font: {
                            family: 'Tajawal',
                            size: 12
                        },
                        color: '#374151'
                    },
                    ticks: {
                        display: true,
                        stepSize: 2,
                        min: 0,
                        max: 10,
                        backdropColor: 'transparent',
                        color: '#6b7280',
                        font: {
                            family: 'Tajawal',
                            size: 10
                        }
                    },
                    suggestedMin: 0,
                    suggestedMax: 10
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    titleFont: {
                        family: 'Tajawal'
                    },
                    bodyFont: {
                        family: 'Tajawal'
                    },
                    callbacks: {
                        label: function(context) {
                            return context.parsed.r.toFixed(1) + '/10';
                        }
                    }
                }
            }
        }
    });
}

// Initialize success probability gauge chart
function initializeSuccessProbabilityChart(canvasId, probability) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');
    const percentage = Math.round(probability * 100);
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [percentage, 100 - percentage],
                backgroundColor: [
                    getSuccessColor(probability),
                    '#e5e7eb'
                ],
                borderWidth: 0,
                cutout: '75%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        },
        plugins: [{
            id: 'centerText',
            beforeDraw: function(chart) {
                const ctx = chart.ctx;
                const centerX = chart.chartArea.left + (chart.chartArea.right - chart.chartArea.left) / 2;
                const centerY = chart.chartArea.top + (chart.chartArea.bottom - chart.chartArea.top) / 2;
                
                ctx.save();
                ctx.font = 'bold 28px Tajawal';
                ctx.fillStyle = getSuccessColor(probability);
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(percentage + '%', centerX, centerY);
                ctx.restore();
            }
        }]
    });
}

// Initialize timing analysis chart
function initializeTimingChart(canvasId, timingData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');
    
    // Prepare data for best hours
    const hours = timingData.best_hours || [20, 21, 22];
    const engagement = hours.map((hour, index) => {
        // Simulate engagement data based on hour
        const baseEngagement = 100;
        const hourFactor = hour >= 19 && hour <= 23 ? 1.5 : 1;
        const randomFactor = 0.8 + Math.random() * 0.4;
        return Math.round(baseEngagement * hourFactor * randomFactor);
    });
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours.map(h => h + ':00'),
            datasets: [{
                label: 'مستوى التفاعل المتوقع',
                data: engagement,
                borderColor: 'rgba(16, 185, 129, 1)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgba(16, 185, 129, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        font: {
                            family: 'Tajawal'
                        },
                        color: '#374151'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        font: {
                            family: 'Tajawal'
                        },
                        color: '#374151'
                    },
                    title: {
                        display: true,
                        text: 'مستوى التفاعل',
                        font: {
                            family: 'Tajawal',
                            size: 12
                        },
                        color: '#374151'
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: {
                            family: 'Tajawal'
                        },
                        color: '#374151'
                    }
                },
                tooltip: {
                    titleFont: {
                        family: 'Tajawal'
                    },
                    bodyFont: {
                        family: 'Tajawal'
                    }
                }
            }
        }
    });
}

// Initialize niche distribution chart
function initializeNicheChart(canvasId, nicheData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');
    
    // Default niche distribution
    const defaultNiches = ['تعليم وتطوير', 'تقنية وبرمجة', 'ترفيه وكوميديا', 'أخرى'];
    const defaultValues = [40, 25, 20, 15];
    
    const niches = nicheData?.labels || defaultNiches;
    const values = nicheData?.data || defaultValues;
    
    return new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: niches,
            datasets: [{
                data: values,
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(139, 92, 246, 0.8)'
                ],
                borderColor: [
                    'rgba(59, 130, 246, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(139, 92, 246, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    pointLabels: {
                        font: {
                            family: 'Tajawal',
                            size: 11
                        },
                        color: '#374151'
                    },
                    ticks: {
                        display: false
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: {
                            family: 'Tajawal',
                            size: 12
                        },
                        color: '#374151',
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    titleFont: {
                        family: 'Tajawal'
                    },
                    bodyFont: {
                        family: 'Tajawal'
                    },
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.r + '%';
                        }
                    }
                }
            }
        }
    });
}

// Utility function to get success color based on probability
function getSuccessColor(probability) {
    if (probability >= 0.8) {
        return '#10b981'; // Green
    } else if (probability >= 0.6) {
        return '#3b82f6'; // Blue
    } else if (probability >= 0.4) {
        return '#f59e0b'; // Yellow
    } else {
        return '#ef4444'; // Red
    }
}

// Utility function to create animated number counter for charts
function animateChartValue(element, endValue, duration = 2000, suffix = '') {
    const startValue = 0;
    const startTime = performance.now();
    
    function updateValue(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOutCubic = 1 - Math.pow(1 - progress, 3);
        const currentValue = startValue + (endValue - startValue) * easeOutCubic;
        
        element.textContent = Math.round(currentValue) + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    }
    
    requestAnimationFrame(updateValue);
}

// Export functions for global use
window.ChartUtils = {
    initializePerformanceChart,
    initializeScoreDistributionChart,
    initializeTitleAnalysisChart,
    initializeSuccessProbabilityChart,
    initializeTimingChart,
    initializeNicheChart,
    animateChartValue,
    getSuccessColor
};

// Auto-initialize charts if data attributes are present
document.addEventListener('DOMContentLoaded', function() {
    // Performance chart
    const performanceCanvas = document.getElementById('performanceChart');
    if (performanceCanvas) {
        const data = {
            channelArt: parseFloat(performanceCanvas.dataset.channelArt || 0),
            thumbnails: parseFloat(performanceCanvas.dataset.thumbnails || 0),
            titles: parseFloat(performanceCanvas.dataset.titles || 0)
        };
        initializePerformanceChart('performanceChart', data);
    }
    
    // Score distribution chart
    const scoreCanvas = document.getElementById('scoreDistributionChart');
    if (scoreCanvas) {
        initializeScoreDistributionChart('scoreDistributionChart');
    }
    
    // Title analysis chart
    const titleCanvas = document.getElementById('titleAnalysisChart');
    if (titleCanvas) {
        const data = {
            attractiveness: parseFloat(titleCanvas.dataset.attractiveness || 0),
            emotional: parseFloat(titleCanvas.dataset.emotional || 0),
            keyword: parseFloat(titleCanvas.dataset.keyword || 0)
        };
        initializeTitleAnalysisChart('titleAnalysisChart', data);
    }
});
