import os
import json
import logging
from openai import OpenAI
from clip_analyzer import CLIPVisualAnalyzer
import requests
import re
from datetime import datetime

class AIAnalyzer:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', 'sk-fallback-key'))
        self.demo_mode = not os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY') == 'sk-fallback-key'
        self.clip_analyzer = CLIPVisualAnalyzer()
        self.last_error = None
    
    def analyze_channel(self, channel_info, videos):
        """Comprehensive channel analysis using AI"""
        if self.demo_mode:
            return self._get_demo_channel_analysis(channel_info)
        
        try:
            # Prepare data for analysis
            channel_data = {
                'title': channel_info.get('title', ''),
                'description': channel_info.get('description', ''),
                'subscriber_count': channel_info.get('subscriber_count', 0),
                'video_count': channel_info.get('video_count', 0),
                'videos': [
                    {
                        'title': video.get('title', ''),
                        'description': video.get('description', '')[:200],
                        'view_count': video.get('view_count', 0)
                    }
                    for video in videos[:10]
                ]
            }
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """أنت خبير تحليل قنوات يوتيوب متخصص في تقييم الأداء والمحتوى. 
                        قم بتحليل القناة المعطاة وتقديم تقييم شامل باللغة العربية.
                        
                        يجب أن يشمل تحليلك:
                        1. تقييم جودة العناوين (1-10)
                        2. تقييم جاذبية الصور المصغرة (1-10)
                        3. تحليل استراتيجية المحتوى
                        4. التقييم العام (1-10)
                        5. توصيات للتحسين
                        
                        أرجع النتيجة بصيغة JSON."""
                    },
                    {
                        "role": "user",
                        "content": f"تحليل هذه القناة: {json.dumps(channel_data, ensure_ascii=False)}"
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Process and standardize the result
            processed_result = {
                'channel_art_score': result.get('channel_art_score', result.get('تقييم_صورة_القناة', 5)),
                'thumbnail_score': result.get('thumbnail_score', result.get('تقييم_الصور_المصغرة', 5)),
                'title_optimization_score': result.get('title_optimization_score', result.get('تقييم_العناوين', 5)),
                'overall_rating': result.get('overall_rating', result.get('التقييم_العام', 5)),
                'details': result,
                'recommendations': result.get('recommendations', result.get('توصيات', []))
            }
            
            return processed_result
            
        except Exception as e:
            logging.error(f"Error in AI channel analysis: {str(e)}")
            return self._get_demo_channel_analysis(channel_info)
    
    def generate_advanced_video_ideas(self, niche, channel_name, analysis):
        """Generate advanced video ideas using AI"""
        if self.demo_mode:
            return self._get_demo_video_ideas(niche)
        
        try:
            context = {
                'niche': niche,
                'channel_name': channel_name,
                'subscriber_count': analysis.subscriber_count,
                'overall_rating': analysis.overall_rating,
                'detected_niche': analysis.detected_niche
            }
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """أنت خبير إنتاج محتوى يوتيوب متخصص في توليد أفكار فيديوهات مبتكرة وجذابة.
                        
                        قم بإنشاء 8 أفكار فيديوهات متنوعة ومبتكرة للمجال المحدد.
                        
                        لكل فكرة اشمل:
                        1. عنوان جذاب ومحسن للبحث
                        2. وصف مفصل للمحتوى
                        3. نقاط رئيسية يجب تغطيتها
                        4. توقع نسبة النجاح (1-10)
                        5. نوع الفيديو (تعليمي، ترفيهي، تحليلي، إلخ)
                        
                        أرجع النتيجة بصيغة JSON مع مصفوفة من الأفكار."""
                    },
                    {
                        "role": "user",
                        "content": f"أنشئ أفكار فيديوهات للمجال: {niche}\nمعلومات القناة: {json.dumps(context, ensure_ascii=False)}"
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            ideas = result.get('ideas', result.get('أفكار', []))
            
            # Process ideas to ensure consistent format
            processed_ideas = []
            for idea in ideas:
                processed_idea = {
                    'title': idea.get('title', idea.get('عنوان', 'فكرة فيديو')),
                    'description': idea.get('description', idea.get('وصف', 'وصف الفيديو')),
                    'success_score': idea.get('success_score', idea.get('نسبة_النجاح', 5)),
                    'video_type': idea.get('video_type', idea.get('نوع_الفيديو', 'عام')),
                    'key_points': idea.get('key_points', idea.get('نقاط_رئيسية', []))
                }
                processed_ideas.append(processed_idea)
            
            return processed_ideas[:8]  # Limit to 8 ideas
            
        except Exception as e:
            logging.error(f"Error generating video ideas: {str(e)}")
            return self._get_demo_video_ideas(niche)
    
    def _get_demo_channel_analysis(self, channel_info):
        """Demo analysis for testing purposes"""
        return {
            'channel_art_score': 7.5,
            'thumbnail_score': 8.2,
            'title_optimization_score': 6.8,
            'overall_rating': 7.5,
            'details': {
                'strengths': ['عناوين جذابة', 'محتوى متنوع', 'تفاعل جيد مع الجمهور'],
                'weaknesses': ['تحتاج تحسين الصور المصغرة', 'عدم انتظام في النشر'],
                'content_strategy': 'استراتيجية محتوى متوسطة مع إمكانية للتطوير',
                'audience_engagement': 'تفاعل الجمهور جيد نسبياً'
            },
            'recommendations': [
                'تحسين جودة الصور المصغرة',
                'إنشاء جدول نشر منتظم',
                'زيادة التفاعل مع التعليقات',
                'تحسين كلمات البحث في العناوين'
            ]
        }
    
    def _get_demo_video_ideas(self, niche):
        """Demo video ideas for testing"""
        demo_ideas = [
            {
                'title': f'أسرار النجاح في مجال {niche} - دليل شامل 2024',
                'description': f'اكتشف أهم النصائح والاستراتيجيات للنجاح في {niche}',
                'success_score': 8.5,
                'video_type': 'تعليمي',
                'key_points': ['نصائح عملية', 'أمثلة واقعية', 'استراتيجيات مجربة']
            },
            {
                'title': f'أخطاء شائعة في {niche} يجب تجنبها',
                'description': f'تعرف على أكثر الأخطاء شيوعاً في {niche} وكيفية تجنبها',
                'success_score': 7.8,
                'video_type': 'تحليلي',
                'key_points': ['أخطاء شائعة', 'حلول عملية', 'نصائح الخبراء']
            },
            {
                'title': f'مراجعة أفضل أدوات {niche} لعام 2024',
                'description': f'مقارنة شاملة لأهم الأدوات المستخدمة في {niche}',
                'success_score': 8.2,
                'video_type': 'مراجعة',
                'key_points': ['مقارنة الأدوات', 'الإيجابيات والسلبيات', 'توصيات']
            },
            {
                'title': f'كيف بدأت رحلتي في {niche} - قصة نجاح ملهمة',
                'description': f'شارك تجربتك الشخصية في تعلم وإتقان {niche}',
                'success_score': 7.5,
                'video_type': 'شخصي',
                'key_points': ['قصة شخصية', 'التحديات والحلول', 'دروس مستفادة']
            }
        ]
        
        return demo_ideas[:8]
