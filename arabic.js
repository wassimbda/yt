// Arabic.js - Arabic Language Support and RTL Enhancements
document.addEventListener('DOMContentLoaded', function() {
    initializeArabicSupport();
    initializeRTLEnhancements();
    initializeArabicValidation();
    initializeArabicFormatting();
});

// Initialize Arabic language support
function initializeArabicSupport() {
    // Set document direction and language
    document.documentElement.setAttribute('dir', 'rtl');
    document.documentElement.setAttribute('lang', 'ar');
    
    // Add Arabic font classes to body
    document.body.classList.add('arabic-text');
    
    // Initialize Arabic number formatting
    initializeArabicNumbers();
    
    // Setup Arabic input handling
    setupArabicInputs();
}

// Initialize RTL enhancements
function initializeRTLEnhancements() {
    // Fix Bootstrap components for RTL
    fixBootstrapRTL();
    
    // Enhance modals for RTL
    enhanceModalsRTL();
    
    // Fix chart tooltips for RTL
    fixChartTooltipsRTL();
    
    // Enhance forms for RTL
    enhanceFormsRTL();
}

// Fix Bootstrap components for RTL
function fixBootstrapRTL() {
    // Fix dropdowns
    const dropdowns = document.querySelectorAll('.dropdown-menu');
    dropdowns.forEach(dropdown => {
        dropdown.style.right = '0';
        dropdown.style.left = 'auto';
    });
    
    // Fix tooltips positioning
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(element => {
        if (!element.getAttribute('data-bs-placement')) {
            element.setAttribute('data-bs-placement', 'right');
        }
    });
    
    // Fix carousel controls
    const carouselPrevs = document.querySelectorAll('.carousel-control-prev');
    const carouselNexts = document.querySelectorAll('.carousel-control-next');
    
    carouselPrevs.forEach(prev => {
        prev.style.right = '0';
        prev.style.left = 'auto';
    });
    
    carouselNexts.forEach(next => {
        next.style.left = '0';
        next.style.right = 'auto';
    });
}

// Enhance modals for RTL
function enhanceModalsRTL() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        // Fix close button position
        const closeBtn = modal.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.style.marginLeft = '0';
            closeBtn.style.marginRight = 'auto';
        }
        
        // Fix modal header alignment
        const modalHeader = modal.querySelector('.modal-header');
        if (modalHeader) {
            modalHeader.style.textAlign = 'right';
        }
    });
}

// Fix chart tooltips for RTL
function fixChartTooltipsRTL() {
    if (typeof Chart !== 'undefined') {
        Chart.defaults.plugins.tooltip.rtl = true;
        Chart.defaults.plugins.tooltip.textDirection = 'rtl';
        
        // Custom positioning for RTL
        Chart.defaults.plugins.tooltip.position = 'average';
        Chart.defaults.plugins.tooltip.caretPadding = 2;
    }
}

// Enhance forms for RTL
function enhanceFormsRTL() {
    // Fix input group positioning
    const inputGroups = document.querySelectorAll('.input-group');
    inputGroups.forEach(group => {
        const addon = group.querySelector('.input-group-text');
        if (addon) {
            addon.style.borderRadius = '0.375rem 0 0 0.375rem';
        }
        
        const input = group.querySelector('.form-control');
        if (input) {
            input.style.borderRadius = '0 0.375rem 0.375rem 0';
        }
    });
    
    // Fix checkbox and radio alignment
    const formChecks = document.querySelectorAll('.form-check');
    formChecks.forEach(check => {
        check.style.paddingRight = '1.25em';
        check.style.paddingLeft = '0';
        
        const input = check.querySelector('.form-check-input');
        if (input) {
            input.style.marginRight = '-1.25em';
            input.style.marginLeft = '0';
        }
    });
}

// Initialize Arabic number formatting
function initializeArabicNumbers() {
    // Format numbers in Arabic locale
    window.formatArabicNumber = function(number) {
        return new Intl.NumberFormat('ar-SA').format(number);
    };
    
    // Convert Western numbers to Arabic-Indic if needed
    window.toArabicIndic = function(number) {
        const arabicNumbers = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
        return number.toString().replace(/[0-9]/g, (w) => arabicNumbers[+w]);
    };
    
    // Convert Arabic-Indic to Western numbers
    window.toWesternNumbers = function(str) {
        const arabicNumbers = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
        return str.replace(/[٠-٩]/g, (w) => arabicNumbers.indexOf(w));
    };
}

// Setup Arabic input handling
function setupArabicInputs() {
    const textInputs = document.querySelectorAll('input[type="text"], textarea');
    
    textInputs.forEach(input => {
        // Auto-detect Arabic text and adjust alignment
        input.addEventListener('input', function() {
            const text = this.value;
            if (isArabicText(text)) {
                this.style.textAlign = 'right';
                this.style.direction = 'rtl';
            } else if (isEnglishText(text)) {
                this.style.textAlign = 'left';
                this.style.direction = 'ltr';
            }
        });
        
        // Handle paste events
        input.addEventListener('paste', function(e) {
            setTimeout(() => {
                const text = this.value;
                if (isArabicText(text)) {
                    this.style.textAlign = 'right';
                    this.style.direction = 'rtl';
                }
            }, 10);
        });
    });
}

// Initialize Arabic validation
function initializeArabicValidation() {
    // Arabic text validation patterns
    window.ArabicValidation = {
        // Check if text contains Arabic characters
        isArabic: function(text) {
            return /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/.test(text);
        },
        
        // Check if text is primarily Arabic
        isPrimarilyArabic: function(text) {
            const arabicChars = text.match(/[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/g);
            const totalChars = text.replace(/\s/g, '').length;
            return arabicChars && (arabicChars.length / totalChars) > 0.5;
        },
        
        // Validate Arabic name
        isValidArabicName: function(name) {
            return /^[\u0600-\u06FF\u0750-\u077F\s]+$/.test(name.trim());
        },
        
        // Clean Arabic text (remove extra spaces, normalize)
        cleanArabicText: function(text) {
            return text
                .replace(/\s+/g, ' ') // Replace multiple spaces with single space
                .replace(/[\u064B-\u0652]/g, '') // Remove diacritics
                .trim();
        }
    };
}

// Initialize Arabic formatting utilities
function initializeArabicFormatting() {
    // Arabic date formatting
    window.formatArabicDate = function(date, format = 'long') {
        const options = {
            year: 'numeric',
            month: format === 'long' ? 'long' : 'short',
            day: 'numeric'
        };
        
        return new Intl.DateTimeFormat('ar-SA', options).format(new Date(date));
    };
    
    // Arabic time formatting
    window.formatArabicTime = function(date) {
        const options = {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        };
        
        return new Intl.DateTimeFormat('ar-SA', options).format(new Date(date));
    };
    
    // Format Arabic currency
    window.formatArabicCurrency = function(amount, currency = 'SAR') {
        return new Intl.NumberFormat('ar-SA', {
            style: 'currency',
            currency: currency
        }).format(amount);
    };
    
    // Format Arabic percentage
    window.formatArabicPercentage = function(value) {
        return new Intl.NumberFormat('ar-SA', {
            style: 'percent',
            minimumFractionDigits: 1,
            maximumFractionDigits: 1
        }).format(value / 100);
    };
}

// Helper function to detect Arabic text
function isArabicText(text) {
    const arabicPattern = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
    return arabicPattern.test(text);
}

// Helper function to detect English text
function isEnglishText(text) {
    const englishPattern = /[A-Za-z]/;
    return englishPattern.test(text) && !isArabicText(text);
}

// Arabic text utilities
window.ArabicUtils = {
    // Normalize Arabic text for better comparison
    normalizeArabic: function(text) {
        return text
            .replace(/[إأآا]/g, 'ا') // Normalize Alef variants
            .replace(/ة/g, 'ه') // Normalize Teh Marbuta
            .replace(/ي/g, 'ى') // Normalize Yeh variants
            .replace(/[\u064B-\u0652]/g, '') // Remove diacritics
            .trim();
    },
    
    // Count Arabic words
    countArabicWords: function(text) {
        const words = text.trim().split(/\s+/);
        return words.filter(word => isArabicText(word)).length;
    },
    
    // Extract Arabic keywords
    extractArabicKeywords: function(text, minLength = 3) {
        const words = text.split(/\s+/);
        return words
            .filter(word => isArabicText(word) && word.length >= minLength)
            .map(word => this.normalizeArabic(word))
            .filter((word, index, arr) => arr.indexOf(word) === index); // Remove duplicates
    },
    
    // Check if text is a question in Arabic
    isArabicQuestion: function(text) {
        const questionWords = ['ما', 'ماذا', 'من', 'متى', 'أين', 'كيف', 'لماذا', 'هل', 'أي'];
        const hasQuestionMark = text.includes('؟');
        const hasQuestionWord = questionWords.some(word => text.includes(word));
        return hasQuestionMark || hasQuestionWord;
    },
    
    // Suggest Arabic alternatives for common English words
    suggestArabicAlternatives: function(text) {
        const suggestions = {
            'video': 'فيديو',
            'channel': 'قناة',
            'youtube': 'يوتيوب',
            'content': 'محتوى',
            'subscribe': 'اشترك',
            'like': 'إعجاب',
            'comment': 'تعليق',
            'share': 'مشاركة',
            'tutorial': 'درس تعليمي',
            'review': 'مراجعة',
            'tips': 'نصائح',
            'guide': 'دليل',
            'how to': 'كيفية',
            'best': 'أفضل',
            'new': 'جديد',
            'update': 'تحديث'
        };
        
        let arabicText = text;
        Object.keys(suggestions).forEach(english => {
            const regex = new RegExp(english, 'gi');
            arabicText = arabicText.replace(regex, suggestions[english]);
        });
        
        return arabicText;
    }
};

// Keyboard layout detection and switching
function initializeKeyboardSupport() {
    let isArabicMode = true;
    
    // Toggle between Arabic and English input
    window.toggleKeyboard = function() {
        isArabicMode = !isArabicMode;
        const activeInput = document.activeElement;
        
        if (activeInput && (activeInput.tagName === 'INPUT' || activeInput.tagName === 'TEXTAREA')) {
            if (isArabicMode) {
                activeInput.style.direction = 'rtl';
                activeInput.style.textAlign = 'right';
                activeInput.setAttribute('lang', 'ar');
            } else {
                activeInput.style.direction = 'ltr';
                activeInput.style.textAlign = 'left';
                activeInput.setAttribute('lang', 'en');
            }
        }
        
        // Update keyboard indicator if exists
        const indicator = document.getElementById('keyboard-indicator');
        if (indicator) {
            indicator.textContent = isArabicMode ? 'ع' : 'EN';
            indicator.title = isArabicMode ? 'اضغط لتغيير للإنجليزية' : 'Click to switch to Arabic';
        }
    };
    
    // Add keyboard shortcut (Alt + Shift)
    document.addEventListener('keydown', function(e) {
        if (e.altKey && e.shiftKey) {
            e.preventDefault();
            toggleKeyboard();
        }
    });
}

// Initialize spell check for Arabic
function initializeArabicSpellCheck() {
    // Common Arabic misspellings and corrections
    const arabicCorrections = {
        'اللة': 'الله',
        'انشاء': 'إنشاء',
        'بناء': 'بناء',
        'مساء': 'مساء',
        'اصدقاء': 'أصدقاء'
    };
    
    window.correctArabicSpelling = function(text) {
        let corrected = text;
        Object.keys(arabicCorrections).forEach(wrong => {
            const regex = new RegExp(wrong, 'g');
            corrected = corrected.replace(regex, arabicCorrections[wrong]);
        });
        return corrected;
    };
}

// Initialize Arabic search enhancement
function initializeArabicSearch() {
    window.ArabicSearch = {
        // Normalize search terms for better matching
        normalizeSearchTerm: function(term) {
            return ArabicUtils.normalizeArabic(term.toLowerCase());
        },
        
        // Search with Arabic text normalization
        searchArabicText: function(text, searchTerm) {
            const normalizedText = this.normalizeSearchTerm(text);
            const normalizedTerm = this.normalizeSearchTerm(searchTerm);
            return normalizedText.includes(normalizedTerm);
        },
        
        // Highlight Arabic search results
        highlightArabicResults: function(text, searchTerm) {
            if (!searchTerm) return text;
            
            const normalizedTerm = this.normalizeSearchTerm(searchTerm);
            const regex = new RegExp(`(${normalizedTerm})`, 'gi');
            return text.replace(regex, '<mark class="bg-warning">$1</mark>');
        }
    };
}

// Performance optimization for Arabic text
function initializeArabicPerformance() {
    // Debounced Arabic text processing
    window.debouncedArabicProcess = debounce(function(text, callback) {
        // Process Arabic text
        const processed = {
            normalized: ArabicUtils.normalizeArabic(text),
            wordCount: ArabicUtils.countArabicWords(text),
            keywords: ArabicUtils.extractArabicKeywords(text),
            isQuestion: ArabicUtils.isArabicQuestion(text)
        };
        
        if (callback) {
            callback(processed);
        }
    }, 300);
}

// Export all Arabic utilities
window.Arabic = {
    Utils: window.ArabicUtils,
    Validation: window.ArabicValidation,
    Search: window.ArabicSearch,
    formatNumber: window.formatArabicNumber,
    formatDate: window.formatArabicDate,
    formatTime: window.formatArabicTime,
    formatCurrency: window.formatArabicCurrency,
    formatPercentage: window.formatArabicPercentage,
    toggleKeyboard: window.toggleKeyboard,
    correctSpelling: window.correctArabicSpelling
};

// Initialize all Arabic features
document.addEventListener('DOMContentLoaded', function() {
    initializeKeyboardSupport();
    initializeArabicSpellCheck();
    initializeArabicSearch();
    initializeArabicPerformance();
    
    // Add Arabic support indicator to UI
    const body = document.body;
    if (!document.getElementById('arabic-support-indicator')) {
        const indicator = document.createElement('div');
        indicator.id = 'arabic-support-indicator';
        indicator.className = 'position-fixed bottom-0 start-0 p-2 bg-primary text-white small rounded-top-end';
        indicator.innerHTML = '<i class="fas fa-language me-1"></i>دعم عربي مُحسّن';
        indicator.style.zIndex = '1000';
        indicator.style.fontSize = '0.75rem';
        body.appendChild(indicator);
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            indicator.style.opacity = '0';
            indicator.style.transition = 'opacity 0.5s';
            setTimeout(() => indicator.remove(), 500);
        }, 3000);
    }
});

// Utility function for debouncing (reused from main.js)
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
