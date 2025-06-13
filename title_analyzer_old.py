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
        
        # Arabic emotional keywords
        self.emotional_keywords = {
            'positive': ['مذهل', 'رائع', 'أفضل', 'سر', 'أسرار', 'مجاني', 'حصري', 'جديد', 'ممتاز', 'مدهش'],
            'negative': ['خطأ', 'فشل', 'مشكلة', 'تحذير', 'خطر', 'صعب', 'مستحيل'],
            'curiosity': ['كيف', 'لماذا', 'ماذا', 'أين', 'متى', 'من', 'سر', 'خفي', 'غير معروف'],
            'urgency': ['الآن', 'اليوم', 'سريع', 'عاجل', 'فوري', '2024', 'جديد', 'أخيراً'],
            'numbers': r'\d+',
            'questions': ['؟', 'كيف', 'لماذا', 'هل', 'ماذا', 'أين', 'متى', 'من']
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
            
            # Combine all analyses
            result = {
                'attractiveness_score': ai_analysis.get('attractiveness_score', 0),
                'emotional_impact': emotional_analysis['emotional_score'],
                'keyword_strength': basic_metrics['keyword_strength'],
                'strengths': ai_analysis.get('strengths', []),
                'weaknesses': ai_analysis.get('weaknesses', []),
                'suggestions': ai_analysis.get('suggestions', []),
                'detailed_metrics': {
                    'length': basic_metrics['length'],
                    'word_count': basic_metrics['word_count'],
                    'emotional_keywords': emotional_analysis['emotional_keywords'],
                    'curiosity_factors': emotional_analysis['curiosity_factors'],
                    'urgency_indicators': emotional_analysis['urgency_indicators'],
                    'question_format': basic_metrics['has_question'],
                    'numbers_present': basic_metrics['has_numbers']
                },
                'optimization_tips': ai_analysis.get('optimization_tips', []),
                'target_audience_alignment': ai_analysis.get('target_audience_alignment', 0)
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error in title analysis: {str(e)}")
            return self._get_demo_title_analysis(title)
    
    def quick_analyze(self, title):
        """Quick analysis for API endpoints"""
        basic_metrics = self._calculate_basic_metrics(title)
        emotional_analysis = self._analyze_emotional_content(title)
        
        return {
            'attractiveness_score': (basic_metrics['keyword_strength'] + emotional_analysis['emotional_score']) / 2 * 10,
            'emotional_impact': emotional_analysis['emotional_score'],
            'length_score': 10 if 40 <= basic_metrics['length'] <= 70 else 5,
            'has_emotional_keywords': len(emotional_analysis['emotional_keywords']) > 0,
            'has_numbers': basic_metrics['has_numbers'],
            'is_question': basic_metrics['has_question']
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
            
            # Standardize field names
            standardized = {
                'attractiveness_score': result.get('attractiveness_score', result.get('درجة_الجاذبية', 50)),
                'strengths': result.get('strengths', result.get('نقاط_القوة', [])),
                'weaknesses': result.get('weaknesses', result.get('نقاط_الضعف', [])),
                'suggestions': result.get('suggestions', result.get('اقتراحات_التحسين', [])),
                'optimization_tips': result.get('optimization_tips', result.get('نصائح_التحسين', [])),
                'target_audience_alignment': result.get('target_audience_alignment', result.get('ملاءمة_الجمهور', 5))
            }
            
            return standardized
            
        except Exception as e:
            logging.error(f"Error in AI analysis: {str(e)}")
            return {
                'attractiveness_score': 50,
                'strengths': ['تحليل تلقائي غير متاح'],
                'weaknesses': ['يتطلب مراجعة يدوية'],
                'suggestions': ['تحسين الكلمات المفتاحية'],
                'optimization_tips': ['إضافة عناصر عاطفية'],
                'target_audience_alignment': 5
            }
    
    def _calculate_basic_metrics(self, title):
        """Calculate basic linguistic metrics"""
        length = len(title)
        word_count = len(title.split())
        
        # Check for numbers
        has_numbers = bool(re.search(r'\d+', title))
        
        # Check for questions
        has_question = '؟' in title or any(q in title for q in self.emotional_keywords['questions'])
        
        # Calculate keyword strength based on emotional words
        total_emotional = 0
        for category, keywords in self.emotional_keywords.items():
            if category != 'numbers':
                total_emotional += sum(1 for keyword in keywords if keyword in title)
        
        keyword_strength = min(10, total_emotional * 2)
        
        return {
            'length': length,
            'word_count': word_count,
            'has_numbers': has_numbers,
            'has_question': has_question,
            'keyword_strength': keyword_strength
        }
    
    def _analyze_emotional_content(self, title):
        """Analyze emotional content and appeal"""
        emotional_keywords = []
        curiosity_factors = []
        urgency_indicators = []
        
        # Check for emotional keywords
        for category, keywords in self.emotional_keywords.items():
            if category in ['positive', 'negative']:
                found = [kw for kw in keywords if kw in title]
                emotional_keywords.extend(found)
            elif category == 'curiosity':
                found = [kw for kw in keywords if kw in title]
                curiosity_factors.extend(found)
            elif category == 'urgency':
                found = [kw for kw in keywords if kw in title]
                urgency_indicators.extend(found)
        
        # Calculate emotional score
        emotional_score = min(10, len(emotional_keywords) * 2 + len(curiosity_factors) * 1.5 + len(urgency_indicators) * 1.5)
        
        return {
            'emotional_score': emotional_score,
            'emotional_keywords': emotional_keywords,
            'curiosity_factors': curiosity_factors,
            'urgency_indicators': urgency_indicators
        }
    
    def _get_demo_title_analysis(self, title):
        """Demo analysis for testing purposes"""
        basic_metrics = self._calculate_basic_metrics(title)
        emotional_analysis = self._analyze_emotional_content(title)
        
        # Calculate demo scores
        length_score = 10 if 30 <= basic_metrics['length'] <= 80 else 6
        emotional_score = emotional_analysis['emotional_score']
        attractiveness_score = (length_score + emotional_score + basic_metrics['keyword_strength']) / 3 * 10
        
        return {
            'attractiveness_score': min(100, attractiveness_score),
            'emotional_impact': emotional_score,
            'keyword_strength': basic_metrics['keyword_strength'],
            'strengths': [
                'طول العنوان مناسب' if 30 <= basic_metrics['length'] <= 80 else None,
                'يحتوي على كلمات عاطفية' if emotional_analysis['emotional_keywords'] else None,
                'يثير الفضول' if emotional_analysis['curiosity_factors'] else None,
                'يحتوي على أرقام' if basic_metrics['has_numbers'] else None
            ],
            'weaknesses': [
                'العنوان طويل جداً' if basic_metrics['length'] > 80 else None,
                'العنوان قصير جداً' if basic_metrics['length'] < 30 else None,
                'يفتقر للكلمات العاطفية' if not emotional_analysis['emotional_keywords'] else None,
                'لا يثير الفضول بما فيه الكفاية' if not emotional_analysis['curiosity_factors'] else None
            ],
            'suggestions': [
                'إضافة كلمات عاطفية أكثر',
                'تحسين الكلمات المفتاحية',
                'جعل العنوان أكثر إثارة للفضول',
                'استخدام أرقام محددة إذا أمكن'
            ],
            'detailed_metrics': {
                'length': basic_metrics['length'],
                'word_count': basic_metrics['word_count'],
                'emotional_keywords': emotional_analysis['emotional_keywords'],
                'curiosity_factors': emotional_analysis['curiosity_factors'],
                'urgency_indicators': emotional_analysis['urgency_indicators'],
                'question_format': basic_metrics['has_question'],
                'numbers_present': basic_metrics['has_numbers']
            },
            'optimization_tips': [
                'استخدم كلمات تثير الفضول مثل "سر" أو "كيف"',
                'أضف عنصر الإلحاح مثل "2024" أو "جديد"',
                'استخدم أرقام محددة لزيادة المصداقية',
                'اجعل العنوان بين 40-70 حرف للأداء الأمثل'
            ],
            'target_audience_alignment': 7
        }
