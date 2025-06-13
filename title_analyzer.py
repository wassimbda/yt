import os
import json
import logging
import re
from openai import OpenAI
from collections import Counter

class TitleAnalyzer:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', 'sk-fallback-key'))
        self.demo_mode = not os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY') == 'sk-fallback-key'
        self.last_error = None
        
        # Arabic emotional keywords
        self.emotional_keywords = {
            'positive': ['مذهل', 'رائع', 'أفضل', 'سر', 'أسرار', 'مجاني', 'حصري', 'جديد', 'ممتاز', 'مدهش', 'لا يصدق', 'مضمون', 'فعال'],
            'negative': ['خطأ', 'فشل', 'مشكلة', 'تحذير', 'خطر', 'صعب', 'مستحيل', 'كارثة', 'مشكلة'],
            'curiosity': ['كيف', 'لماذا', 'ماذا', 'أين', 'متى', 'من', 'سر', 'خفي', 'غير معروف', 'لن تصدق', 'مفاجأة'],
            'urgency': ['الآن', 'اليوم', 'سريع', 'عاجل', 'فوري', '2024', 'جديد', 'أخيراً', 'قبل فوات الأوان', 'محدود'],
            'numbers': r'\d+',
            'questions': ['؟', 'كيف', 'لماذا', 'هل', 'ماذا', 'أين', 'متى', 'من']
        }
        
        # Enhanced keyword categories for better analysis
        self.seo_keywords = {
            'high_value': ['تعلم', 'طريقة', 'شرح', 'درس', 'كيفية', 'أفضل', 'مجاني', 'سهل', 'بسيط'],
            'trending': ['2024', 'جديد', 'حديث', 'آخر', 'عاجل', 'حصري', 'مباشر'],
            'engagement': ['تحدي', 'مسابقة', 'تجربة', 'اختبار', 'لعبة', 'مقارنة', 'مراجعة']
        }
    
    def analyze_title(self, title, category='عام', target_audience=''):
        """Comprehensive title analysis using AI and linguistic analysis"""
        if self.demo_mode:
            return self._get_demo_title_analysis(title)
        
        try:
            # Basic metrics
            basic_metrics = self._calculate_basic_metrics(title)
            
            # Emotional analysis
            emotional_analysis = self._analyze_emotional_content(title)
            
            # AI-powered analysis
            ai_analysis = self._get_ai_analysis(title, category, target_audience)
            
            # SEO analysis
            seo_analysis = self._analyze_seo_factors(title)
            
            # Combine all analyses
            result = {
                'title': title,
                'category': category,
                'target_audience': target_audience,
                'attractiveness_score': ai_analysis.get('attractiveness_score', 70),
                'success_probability': ai_analysis.get('success_probability', 0.7),
                'emotional_impact': ai_analysis.get('emotional_impact', emotional_analysis['emotional_score']),
                'keyword_strength': ai_analysis.get('keyword_strength', seo_analysis['keyword_score']),
                'clickability_score': ai_analysis.get('clickability_score', 7),
                'retention_potential': ai_analysis.get('retention_potential', 7),
                'seo_optimization': ai_analysis.get('seo_optimization', seo_analysis['seo_score']),
                'trending_potential': ai_analysis.get('trending_potential', 6),
                'predicted_ctr': ai_analysis.get('predicted_ctr', 8.5),
                'strengths': ai_analysis.get('strengths', []),
                'weaknesses': ai_analysis.get('weaknesses', []),
                'suggestions': ai_analysis.get('suggestions', []),
                'alternative_titles': ai_analysis.get('alternative_titles', []),
                'detailed_metrics': {
                    'length': basic_metrics['length'],
                    'word_count': basic_metrics['word_count'],
                    'emotional_keywords': emotional_analysis['emotional_keywords'],
                    'curiosity_factors': emotional_analysis['curiosity_factors'],
                    'urgency_indicators': emotional_analysis['urgency_indicators'],
                    'question_format': basic_metrics['has_question'],
                    'numbers_present': basic_metrics['has_numbers'],
                    'seo_keywords': seo_analysis['found_keywords']
                },
                'best_posting_time': ai_analysis.get('best_posting_time', 'مساءً 7-9 بتوقيت مكة'),
                'competitor_analysis': ai_analysis.get('competitor_analysis', 'تحليل منافسين غير متوفر'),
                'improvement_priority': ai_analysis.get('improvement_priority', 'تحسين الكلمات المفتاحية'),
                'detailed_explanation': ai_analysis.get('detailed_explanation', 'تحليل شامل للعنوان'),
                'viral_factors': ai_analysis.get('viral_factors', ['استخدام أرقام', 'كلمات عاطفية'])
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error in enhanced title analysis: {str(e)}")
            return self._get_demo_title_analysis(title)
    
    def quick_analyze(self, title):
        """Quick analysis for API endpoints"""
        basic_metrics = self._calculate_basic_metrics(title)
        emotional_analysis = self._analyze_emotional_content(title)
        seo_analysis = self._analyze_seo_factors(title)
        
        return {
            'attractiveness_score': (basic_metrics['keyword_strength'] + emotional_analysis['emotional_score'] + seo_analysis['seo_score']) / 3 * 10,
            'emotional_impact': emotional_analysis['emotional_score'],
            'length_score': 10 if 40 <= basic_metrics['length'] <= 70 else 5,
            'has_emotional_keywords': len(emotional_analysis['emotional_keywords']) > 0,
            'has_numbers': basic_metrics['has_numbers'],
            'is_question': basic_metrics['has_question'],
            'seo_score': seo_analysis['seo_score']
        }
    
    def _get_ai_analysis(self, title, category, target_audience):
        """Get AI-powered analysis from GPT-4o with enhanced accuracy"""
        try:
            prompt = f"""
            أنت خبير محترف في تحليل عناوين يوتيوب العربية مع خبرة 10 سنوات في تحسين المحتوى الرقمي.
            
            حلل العنوان التالي بدقة عالية وعمق تحليلي:
            
            العنوان: "{title}"
            الفئة: {category}
            الجمهور المستهدف: {target_audience}
            
            قم بتحليل شامل ودقيق يشمل:
            
            1. تحليل الجاذبية النفسية والعاطفية
            2. قوة الكلمات المفتاحية ومدى بحثها
            3. توقع الأداء بناءً على خوارزمية يوتيوب
            4. التحليل اللغوي والبلاغي
            5. مناسبة المحتوى للجمهور العربي
            6. عوامل SEO والاكتشاف
            
            أرجع النتيجة في صيغة JSON مع هذا التنسيق الدقيق:
            {{
                "attractiveness_score": (رقم دقيق من 1-100 بناءً على الجاذبية الحقيقية),
                "success_probability": (رقم دقيق من 0-1 بناءً على توقع الأداء الفعلي),
                "emotional_impact": (رقم من 1-10 بناءً على التأثير النفسي),
                "keyword_strength": (رقم من 1-10 بناءً على قوة SEO والبحث),
                "clickability_score": (رقم من 1-10 لاحتمالية النقر),
                "retention_potential": (رقم من 1-10 لاحتمالية استمرار المشاهدة),
                "strengths": ["نقاط القوة المحددة بدقة"],
                "weaknesses": ["نقاط الضعف الحقيقية"],
                "suggestions": ["اقتراحات عملية ومحددة للتحسين"],
                "category_optimization": (رقم من 1-10 لمناسبة الفئة),
                "audience_resonance": (رقم من 1-10 لصدى الجمهور المستهدف),
                "seo_optimization": (رقم من 1-10 لتحسين محركات البحث),
                "trending_potential": (رقم من 1-10 لإمكانية الانتشار),
                "best_posting_time": "أفضل وقت محدد للنشر مع السبب",
                "competitor_analysis": "مقارنة مع العناوين المنافسة",
                "improvement_priority": "أولوية التحسين الأهم",
                "detailed_explanation": "تفسير تحليلي مفصل وعلمي",
                "alternative_titles": ["3 عناوين بديلة محسنة"],
                "predicted_ctr": (رقم توقع معدل النقر من 0-20),
                "viral_factors": ["عوامل الانتشار الموجودة أو المفقودة"]
            }}
            
            كن دقيقاً وواقعياً في التقييم. لا تبالغ في النتائج.
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "أنت خبير تحليل محتوى يوتيوب متخصص في السوق العربي مع قاعدة بيانات ضخمة من العناوين الناجحة."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and ensure all required fields exist
            required_fields = ['attractiveness_score', 'success_probability', 'emotional_impact', 
                             'keyword_strength', 'strengths', 'weaknesses', 'suggestions']
            
            for field in required_fields:
                if field not in result:
                    logging.warning(f"Missing field {field} in AI response")
                    result[field] = self._get_default_value(field)
            
            return result
            
        except Exception as e:
            logging.error(f"Error in enhanced AI analysis: {str(e)}")
            self.last_error = str(e)
            # Return advanced fallback analysis only if API fails
            return self._get_advanced_fallback_analysis(title, category, target_audience)
    
    def _get_default_value(self, field):
        """Get default value for missing fields"""
        defaults = {
            'attractiveness_score': 70,
            'success_probability': 0.7,
            'emotional_impact': 7,
            'keyword_strength': 7,
            'strengths': ['عنوان واضح'],
            'weaknesses': ['يحتاج تحسين'],
            'suggestions': ['تحسين الكلمات المفتاحية']
        }
        return defaults.get(field, 0)
    
    def _calculate_basic_metrics(self, title):
        """Calculate basic linguistic metrics"""
        try:
            length = len(title)
            words = title.split()
            word_count = len(words)
            
            # Check for numbers
            has_numbers = bool(re.search(r'\d+', title))
            
            # Check for questions
            has_question = '؟' in title or any(q in title for q in self.emotional_keywords['questions'])
            
            # Keyword strength based on length and structure
            keyword_strength = 5  # Base score
            if 40 <= length <= 70:
                keyword_strength += 2
            if has_numbers:
                keyword_strength += 1
            if has_question:
                keyword_strength += 1
            if word_count >= 5:
                keyword_strength += 1
            
            return {
                'length': length,
                'word_count': word_count,
                'has_numbers': has_numbers,
                'has_question': has_question,
                'keyword_strength': min(10, keyword_strength)
            }
            
        except Exception as e:
            logging.error(f"Error calculating basic metrics: {str(e)}")
            return {
                'length': len(title),
                'word_count': len(title.split()),
                'has_numbers': False,
                'has_question': False,
                'keyword_strength': 5
            }
    
    def _analyze_emotional_content(self, title):
        """Analyze emotional content and appeal"""
        try:
            emotional_score = 5  # Base score
            found_keywords = {
                'positive': [],
                'negative': [],
                'curiosity': [],
                'urgency': []
            }
            
            title_lower = title.lower()
            
            # Check for emotional keywords
            for category, keywords in self.emotional_keywords.items():
                if category == 'numbers' or category == 'questions':
                    continue
                    
                for keyword in keywords:
                    if keyword in title_lower:
                        found_keywords[category].append(keyword)
                        if category == 'positive':
                            emotional_score += 1
                        elif category == 'curiosity':
                            emotional_score += 1.5
                        elif category == 'urgency':
                            emotional_score += 1.2
                        elif category == 'negative':
                            emotional_score -= 0.5
            
            # Check for numbers (curiosity factor)
            numbers = re.findall(r'\d+', title)
            if numbers:
                emotional_score += 0.5 * len(numbers)
            
            return {
                'emotional_score': min(10, max(1, emotional_score)),
                'emotional_keywords': found_keywords,
                'curiosity_factors': found_keywords['curiosity'] + (numbers if numbers else []),
                'urgency_indicators': found_keywords['urgency']
            }
            
        except Exception as e:
            logging.error(f"Error analyzing emotional content: {str(e)}")
            return {
                'emotional_score': 6,
                'emotional_keywords': {'positive': [], 'negative': [], 'curiosity': [], 'urgency': []},
                'curiosity_factors': [],
                'urgency_indicators': []
            }
    
    def _analyze_seo_factors(self, title):
        """Analyze SEO and discoverability factors"""
        try:
            seo_score = 5  # Base score
            found_keywords = {
                'high_value': [],
                'trending': [],
                'engagement': []
            }
            
            title_lower = title.lower()
            
            # Check for SEO keywords
            for category, keywords in self.seo_keywords.items():
                for keyword in keywords:
                    if keyword in title_lower:
                        found_keywords[category].append(keyword)
                        if category == 'high_value':
                            seo_score += 1.5
                        elif category == 'trending':
                            seo_score += 1.2
                        elif category == 'engagement':
                            seo_score += 1
            
            # Length optimization for SEO
            length = len(title)
            if 40 <= length <= 60:  # Optimal length for YouTube titles
                seo_score += 1
            elif length > 100:  # Too long
                seo_score -= 1
            
            # Keyword density analysis
            words = title.split()
            if len(words) >= 5:  # Good keyword potential
                seo_score += 0.5
            
            return {
                'seo_score': min(10, max(1, seo_score)),
                'keyword_score': min(10, seo_score),
                'found_keywords': found_keywords,
                'length_optimization': 40 <= length <= 60
            }
            
        except Exception as e:
            logging.error(f"Error analyzing SEO factors: {str(e)}")
            return {
                'seo_score': 6,
                'keyword_score': 6,
                'found_keywords': {'high_value': [], 'trending': [], 'engagement': []},
                'length_optimization': False
            }
    
    def _get_advanced_fallback_analysis(self, title, category, target_audience):
        """Advanced fallback analysis when AI is not available"""
        basic_metrics = self._calculate_basic_metrics(title)
        emotional_analysis = self._analyze_emotional_content(title)
        seo_analysis = self._analyze_seo_factors(title)
        
        # Calculate attractiveness score
        attractiveness = (
            basic_metrics['keyword_strength'] * 10 +
            emotional_analysis['emotional_score'] * 8 +
            seo_analysis['seo_score'] * 7
        ) / 3
        
        # Generate analysis based on patterns
        strengths = []
        weaknesses = []
        suggestions = []
        
        if basic_metrics['has_numbers']:
            strengths.append("استخدام الأرقام يجذب الانتباه")
        if basic_metrics['has_question']:
            strengths.append("صيغة السؤال تثير الفضول")
        if len(emotional_analysis['emotional_keywords']['positive']) > 0:
            strengths.append("كلمات إيجابية جذابة")
        if seo_analysis['length_optimization']:
            strengths.append("طول مناسب لمحركات البحث")
        
        if basic_metrics['length'] > 100:
            weaknesses.append("العنوان طويل جداً")
            suggestions.append("اختصار العنوان لأقل من 100 حرف")
        if basic_metrics['length'] < 30:
            weaknesses.append("العنوان قصير جداً")
            suggestions.append("إضافة تفاصيل أكثر للعنوان")
        if len(emotional_analysis['emotional_keywords']['curiosity']) == 0:
            weaknesses.append("لا يحتوي على عوامل إثارة الفضول")
            suggestions.append("إضافة كلمات تثير الفضول مثل 'سر' أو 'كيف'")
        if seo_analysis['seo_score'] < 6:
            suggestions.append("تحسين الكلمات المفتاحية للبحث")
        
        if not strengths:
            strengths.append("عنوان واضح ومفهوم")
        if not suggestions:
            suggestions.append("العنوان جيد، يمكن تحسينه بإضافة كلمات جذابة")
        
        return {
            'attractiveness_score': min(100, max(30, int(attractiveness))),
            'success_probability': min(1.0, max(0.3, attractiveness / 100)),
            'emotional_impact': emotional_analysis['emotional_score'],
            'keyword_strength': seo_analysis['keyword_score'],
            'clickability_score': min(10, max(4, emotional_analysis['emotional_score'])),
            'retention_potential': min(10, max(5, basic_metrics['keyword_strength'])),
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions,
            'seo_optimization': seo_analysis['seo_score'],
            'trending_potential': min(10, max(4, len(emotional_analysis['curiosity_factors']) + len(emotional_analysis['urgency_indicators']))),
            'predicted_ctr': min(20, max(3, attractiveness / 5)),
            'best_posting_time': self._get_optimal_posting_time(category),
            'competitor_analysis': f"عنوان في مجال {category} - يحتاج مقارنة مع المنافسين",
            'improvement_priority': self._get_improvement_priority(weaknesses),
            'detailed_explanation': f"تحليل متقدم للعنوان بناءً على {len(title)} حرف و {basic_metrics['word_count']} كلمة",
            'alternative_titles': self._generate_alternative_titles(title, category),
            'viral_factors': self._identify_viral_factors(title, emotional_analysis, basic_metrics)
        }
    
    def _get_optimal_posting_time(self, category):
        """Get optimal posting time based on category"""
        timing_map = {
            'تقنية': 'مساءً 7-9 بتوقيت مكة (وقت العمل والتعلم)',
            'طبخ': 'بعد الظهر 2-4 أو مساءً 6-8 (أوقات تحضير الطعام)',
            'رياضة': 'مساءً 8-10 (بعد انتهاء اليوم)',
            'تعليم': 'صباحاً 9-11 أو مساءً 7-9 (أوقات الدراسة)',
            'ترفيه': 'مساءً 8-11 (وقت الراحة)',
            'أخبار': 'صباحاً 7-9 أو مساءً 6-8 (أوقات متابعة الأخبار)'
        }
        return timing_map.get(category, 'مساءً 7-9 بتوقيت مكة (الوقت الأمثل عموماً)')
    
    def _get_improvement_priority(self, weaknesses):
        """Determine improvement priority based on weaknesses"""
        if any('طول' in w for w in weaknesses):
            return 'تحسين طول العنوان'
        elif any('فضول' in w for w in weaknesses):
            return 'إضافة عوامل جذب وإثارة الفضول'
        elif any('كلمات' in w for w in weaknesses):
            return 'تحسين الكلمات المفتاحية'
        else:
            return 'تحسين الجاذبية العامة للعنوان'
    
    def _generate_alternative_titles(self, title, category):
        """Generate alternative title suggestions"""
        base_words = title.split()
        alternatives = []
        
        # Add numbers if not present
        if not re.search(r'\d+', title):
            alternatives.append(f"5 {' '.join(base_words[:3])} مذهلة")
        
        # Add question format if not present
        if '؟' not in title and not any(q in title for q in ['كيف', 'لماذا', 'ماذا']):
            alternatives.append(f"كيف {' '.join(base_words[:4])}؟")
        
        # Add urgency if not present
        if not any(u in title.lower() for u in ['الآن', 'اليوم', 'جديد', 'عاجل']):
            alternatives.append(f"{title} - جديد 2024")
        
        return alternatives[:3] if alternatives else [f"تحسين: {title}"]
    
    def _identify_viral_factors(self, title, emotional_analysis, basic_metrics):
        """Identify viral factors present or missing"""
        factors = []
        
        if basic_metrics['has_numbers']:
            factors.append("استخدام الأرقام")
        if basic_metrics['has_question']:
            factors.append("صيغة السؤال")
        if len(emotional_analysis['emotional_keywords']['positive']) > 0:
            factors.append("كلمات إيجابية")
        if len(emotional_analysis['curiosity_factors']) > 0:
            factors.append("عوامل إثارة الفضول")
        if len(emotional_analysis['urgency_indicators']) > 0:
            factors.append("مؤشرات الاستعجال")
        
        if not factors:
            factors = ["يحتاج إضافة عوامل انتشار مثل الأرقام والكلمات الجذابة"]
        
        return factors
    
    def _get_demo_title_analysis(self, title):
        """Demo analysis for testing purposes"""
        return {
            'title': title,
            'attractiveness_score': 75,
            'success_probability': 0.72,
            'emotional_impact': 7.5,
            'keyword_strength': 7,
            'clickability_score': 8,
            'retention_potential': 7,
            'seo_optimization': 7,
            'trending_potential': 6,
            'predicted_ctr': 12.5,
            'strengths': [
                'عنوان واضح ومفهوم',
                'طول مناسب للعرض',
                'يحتوي على كلمات مفتاحية'
            ],
            'weaknesses': [
                'يمكن إضافة المزيد من الكلمات الجذابة',
                'يحتاج تحسين عوامل الفضول'
            ],
            'suggestions': [
                'إضافة أرقام محددة للجذب',
                'استخدام كلمات تثير الفضول',
                'تحسين الكلمات المفتاحية'
            ],
            'alternative_titles': [
                f"5 أسرار حول {title}",
                f"كيف تحقق {title}؟",
                f"{title} - الطريقة الصحيحة 2024"
            ],
            'detailed_metrics': {
                'length': len(title),
                'word_count': len(title.split()),
                'emotional_keywords': [],
                'curiosity_factors': [],
                'urgency_indicators': [],
                'question_format': '؟' in title,
                'numbers_present': bool(re.search(r'\d+', title)),
                'seo_keywords': []
            },
            'best_posting_time': 'مساءً 7-9 بتوقيت مكة',
            'competitor_analysis': 'تحليل منافسين - وضع تجريبي',
            'improvement_priority': 'تحسين عوامل الجذب والفضول',
            'detailed_explanation': 'تحليل تجريبي شامل للعنوان مع توصيات للتحسين',
            'viral_factors': ['يحتاج عوامل انتشار إضافية'],
            'note': 'تحليل تجريبي - للحصول على تحليل دقيق، يُنصح بتوفير مفتاح OpenAI API'
        }