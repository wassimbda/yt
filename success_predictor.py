import os
import json
import logging
import re
from openai import OpenAI
import math

class SuccessPredictor:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', 'sk-fallback-key'))
        self.demo_mode = not os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY') == 'sk-fallback-key'
        
        # Success factors and their weights
        self.success_factors = {
            'title_length': {'optimal_range': (40, 70), 'weight': 0.15},
            'emotional_words': {'weight': 0.20},
            'numbers': {'weight': 0.15},
            'curiosity_gap': {'weight': 0.25},
            'trending_keywords': {'weight': 0.10},
            'clickbait_elements': {'weight': 0.15}
        }
        
        # High-performing keywords in Arabic
        self.trending_keywords = [
            '2024', 'جديد', 'حصري', 'مجاني', 'سر', 'أسرار', 'كيف', 'أفضل',
            'تحدي', 'مراجعة', 'تجربة', 'نصائح', 'دليل', 'شرح', 'تعلم'
        ]
        
        self.emotional_triggers = [
            'مذهل', 'رائع', 'مدهش', 'لا يصدق', 'صادم', 'مفاجئ', 'غريب',
            'خطير', 'مهم', 'عاجل', 'حصري', 'نادر', 'فريد', 'استثنائي'
        ]
    
    def predict_success(self, title, category='عام', thumbnail_description=''):
        """Predict video success probability using multiple factors"""
        if self.demo_mode:
            return self._get_demo_success_prediction(title)
        
        try:
            # Calculate individual factor scores
            factors = self._analyze_success_factors(title)
            
            # Get AI-powered prediction
            ai_prediction = self._get_ai_success_prediction(title, category, thumbnail_description)
            
            # Combine scores with weights
            weighted_score = sum(factors[factor] * self.success_factors[factor]['weight'] 
                               for factor in factors if factor in self.success_factors)
            
            # Average with AI prediction
            final_probability = (weighted_score + ai_prediction.get('probability', 0.5)) / 2
            
            result = {
                'success_probability': min(1.0, final_probability),
                'confidence_level': ai_prediction.get('confidence', 0.7),
                'success_factors': factors,
                'predicted_performance': self._categorize_performance(final_probability),
                'improvement_suggestions': ai_prediction.get('suggestions', []),
                'risk_factors': ai_prediction.get('risks', []),
                'optimal_conditions': ai_prediction.get('optimal_conditions', {}),
                'expected_metrics': self._predict_metrics(final_probability, category)
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error in success prediction: {str(e)}")
            return self._get_demo_success_prediction(title)
    
    def _analyze_success_factors(self, title):
        """Analyze individual success factors"""
        factors = {}
        
        # Title length factor
        length = len(title)
        optimal_range = self.success_factors['title_length']['optimal_range']
        if optimal_range[0] <= length <= optimal_range[1]:
            factors['title_length'] = 1.0
        else:
            # Penalty for being outside optimal range
            distance = min(abs(length - optimal_range[0]), abs(length - optimal_range[1]))
            factors['title_length'] = max(0.3, 1.0 - (distance / 50))
        
        # Emotional words factor
        emotional_count = sum(1 for word in self.emotional_triggers if word in title)
        factors['emotional_words'] = min(1.0, emotional_count * 0.3)
        
        # Numbers factor
        factors['numbers'] = 1.0 if re.search(r'\d+', title) else 0.3
        
        # Curiosity gap factor
        curiosity_indicators = ['كيف', 'لماذا', 'ماذا', 'سر', 'أسرار', '؟', 'خفي', 'غير معروف']
        curiosity_count = sum(1 for indicator in curiosity_indicators if indicator in title)
        factors['curiosity_gap'] = min(1.0, curiosity_count * 0.4)
        
        # Trending keywords factor
        trending_count = sum(1 for keyword in self.trending_keywords if keyword in title)
        factors['trending_keywords'] = min(1.0, trending_count * 0.25)
        
        # Clickbait elements (balanced approach)
        clickbait_indicators = ['لن تصدق', 'مفاجأة', 'صادم', 'أخيراً', 'حصري', 'مجاني']
        clickbait_count = sum(1 for indicator in clickbait_indicators if indicator in title)
        factors['clickbait_elements'] = min(0.8, clickbait_count * 0.2)  # Cap at 0.8 to avoid over-clickbait
        
        return factors
    
    def _get_ai_success_prediction(self, title, category, thumbnail_description):
        """Get AI-powered success prediction"""
        try:
            context = {
                'title': title,
                'category': category,
                'thumbnail_description': thumbnail_description
            }
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """أنت خبير تحليل أداء فيديوهات يوتيوب متخصص في التنبؤ بنجاح المحتوى.
                        
                        قم بتحليل العنوان المعطى وتوقع احتمالية نجاحه بناءً على:
                        1. جاذبية العنوان
                        2. إثارة الفضول
                        3. استخدام الكلمات المفتاحية
                        4. طول العنوان
                        5. العوامل العاطفية
                        6. ملاءمة الفئة
                        
                        أعط:
                        - احتمالية النجاح (0-1)
                        - مستوى الثقة (0-1)
                        - اقتراحات التحسين
                        - عوامل المخاطرة
                        - الظروف المثلى للنشر
                        
                        أرجع النتيجة بصيغة JSON."""
                    },
                    {
                        "role": "user",
                        "content": f"توقع نجاح هذا المحتوى: {json.dumps(context, ensure_ascii=False)}"
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                'probability': result.get('probability', result.get('احتمالية_النجاح', 0.5)),
                'confidence': result.get('confidence', result.get('مستوى_الثقة', 0.7)),
                'suggestions': result.get('suggestions', result.get('اقتراحات_التحسين', [])),
                'risks': result.get('risks', result.get('عوامل_المخاطرة', [])),
                'optimal_conditions': result.get('optimal_conditions', result.get('الظروف_المثلى', {}))
            }
            
        except Exception as e:
            logging.error(f"Error in AI success prediction: {str(e)}")
            return {
                'probability': 0.6,
                'confidence': 0.5,
                'suggestions': ['تحسين العنوان', 'إضافة كلمات مفتاحية'],
                'risks': ['منافسة عالية'],
                'optimal_conditions': {'timing': 'مساء', 'day': 'نهاية الأسبوع'}
            }
    
    def _categorize_performance(self, probability):
        """Categorize expected performance based on probability"""
        if probability >= 0.8:
            return {
                'category': 'ممتاز',
                'description': 'احتمالية نجاح عالية جداً',
                'color': 'success',
                'icon': 'fas fa-star'
            }
        elif probability >= 0.6:
            return {
                'category': 'جيد',
                'description': 'احتمالية نجاح جيدة',
                'color': 'info',
                'icon': 'fas fa-thumbs-up'
            }
        elif probability >= 0.4:
            return {
                'category': 'متوسط',
                'description': 'احتمالية نجاح متوسطة',
                'color': 'warning',
                'icon': 'fas fa-balance-scale'
            }
        else:
            return {
                'category': 'ضعيف',
                'description': 'احتمالية نجاح منخفضة',
                'color': 'danger',
                'icon': 'fas fa-exclamation-triangle'
            }
    
    def _predict_metrics(self, probability, category):
        """Predict expected video metrics"""
        # Base metrics for different categories
        base_metrics = {
            'تعليم': {'views': 50000, 'engagement': 0.05},
            'ترفيه': {'views': 100000, 'engagement': 0.08},
            'تقنية': {'views': 30000, 'engagement': 0.04},
            'رياضة': {'views': 80000, 'engagement': 0.06},
            'موسيقى': {'views': 120000, 'engagement': 0.10},
            'عام': {'views': 40000, 'engagement': 0.05}
        }
        
        base = base_metrics.get(category, base_metrics['عام'])
        multiplier = 1 + (probability - 0.5) * 2  # Scale based on success probability
        
        return {
            'expected_views': int(base['views'] * multiplier),
            'expected_likes': int(base['views'] * multiplier * base['engagement']),
            'expected_comments': int(base['views'] * multiplier * base['engagement'] * 0.1),
            'expected_shares': int(base['views'] * multiplier * base['engagement'] * 0.05),
            'confidence_interval': f"±{int(base['views'] * multiplier * 0.3)}"
        }
    
    def _get_demo_success_prediction(self, title):
        """Demo prediction for testing purposes"""
        # Simple scoring based on title characteristics
        factors = self._analyze_success_factors(title)
        probability = sum(factors.values()) / len(factors)
        
        return {
            'success_probability': probability,
            'confidence_level': 0.75,
            'success_factors': factors,
            'predicted_performance': self._categorize_performance(probability),
            'improvement_suggestions': [
                'تحسين العنوان لجذب المزيد من النقرات',
                'إضافة كلمات مفتاحية قوية',
                'استخدام عناصر تثير الفضول',
                'تحسين طول العنوان ليكون بين 40-70 حرف'
            ],
            'risk_factors': [
                'منافسة عالية في هذا المجال',
                'قد يحتاج وقت أطول للانتشار',
                'يتطلب محتوى عالي الجودة'
            ],
            'optimal_conditions': {
                'best_time': 'من 7-9 مساءً',
                'best_days': ['الخميس', 'الجمعة', 'السبت'],
                'target_audience': 'الشباب 18-35 سنة',
                'recommended_length': '8-12 دقيقة'
            },
            'expected_metrics': self._predict_metrics(probability, 'عام')
        }
