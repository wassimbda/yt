import os
import json
import logging
from datetime import datetime, timedelta
from openai import OpenAI

class TimingOptimizer:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', 'sk-fallback-key'))
        self.demo_mode = not os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY') == 'sk-fallback-key'
        
        # General optimal posting patterns for MENA region
        self.general_patterns = {
            'weekdays': {
                'الأحد': {'peak_hours': [20, 21, 22], 'activity_level': 0.8},
                'الاثنين': {'peak_hours': [19, 20, 21], 'activity_level': 0.7},
                'الثلاثاء': {'peak_hours': [19, 20, 21], 'activity_level': 0.7},
                'الأربعاء': {'peak_hours': [19, 20, 21], 'activity_level': 0.7},
                'الخميس': {'peak_hours': [20, 21, 22], 'activity_level': 0.9},
                'الجمعة': {'peak_hours': [14, 15, 20, 21], 'activity_level': 1.0},
                'السبت': {'peak_hours': [15, 16, 20, 21], 'activity_level': 0.9}
            },
            'content_categories': {
                'تعليم': {'best_days': ['الأحد', 'الاثنين', 'الثلاثاء'], 'best_hours': [19, 20, 21]},
                'ترفيه': {'best_days': ['الخميس', 'الجمعة', 'السبت'], 'best_hours': [20, 21, 22]},
                'تقنية': {'best_days': ['الأحد', 'الثلاثاء', 'الأربعاء'], 'best_hours': [19, 20]},
                'رياضة': {'best_days': ['الخميس', 'الجمعة', 'السبت'], 'best_hours': [21, 22, 23]},
                'موسيقى': {'best_days': ['الجمعة', 'السبت'], 'best_hours': [20, 21, 22, 23]},
                'طبخ': {'best_days': ['الخميس', 'الجمعة'], 'best_hours': [18, 19, 20]},
                'عام': {'best_days': ['الخميس', 'الجمعة', 'السبت'], 'best_hours': [20, 21, 22]}
            }
        }
    
    def analyze_optimal_timing(self, channel_info, videos):
        """Analyze optimal posting timing for a channel"""
        if self.demo_mode:
            return self._get_demo_timing_analysis(channel_info)
        
        try:
            # Analyze historical posting patterns
            posting_patterns = self._analyze_posting_patterns(videos)
            
            # Determine content category
            content_category = self._determine_content_category(channel_info, videos)
            
            # Get AI-powered timing analysis
            ai_analysis = self._get_ai_timing_analysis(channel_info, posting_patterns, content_category)
            
            # Combine with general patterns
            optimal_timing = self._calculate_optimal_timing(content_category, posting_patterns, ai_analysis)
            
            result = {
                'best_days': optimal_timing['best_days'],
                'best_hours': optimal_timing['best_hours'],
                'timezone': 'Asia/Riyadh',  # Default for MENA
                'audience_data': {
                    'primary_timezone': 'GMT+3',
                    'activity_pattern': optimal_timing['activity_pattern'],
                    'engagement_peaks': optimal_timing['engagement_peaks']
                },
                'confidence_score': optimal_timing['confidence'],
                'data_quality': self._assess_data_quality(videos),
                'recommendations': ai_analysis.get('recommendations', []),
                'seasonal_considerations': ai_analysis.get('seasonal_factors', {}),
                'content_specific_timing': optimal_timing.get('content_specific', {})
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error in timing analysis: {str(e)}")
            return self._get_demo_timing_analysis(channel_info)
    
    def get_timing_recommendations(self, category, target_audience=''):
        """Get timing recommendations for specific content category"""
        if category in self.general_patterns['content_categories']:
            pattern = self.general_patterns['content_categories'][category]
        else:
            pattern = self.general_patterns['content_categories']['عام']
        
        # Get AI-enhanced recommendations if available
        if not self.demo_mode:
            try:
                ai_recommendations = self._get_ai_category_timing(category, target_audience)
                # Merge AI recommendations with general patterns
                return {
                    'best_days': ai_recommendations.get('best_days', pattern['best_days']),
                    'best_hours': ai_recommendations.get('best_hours', pattern['best_hours']),
                    'reasoning': ai_recommendations.get('reasoning', []),
                    'additional_tips': ai_recommendations.get('tips', [])
                }
            except:
                pass
        
        return {
            'best_days': pattern['best_days'],
            'best_hours': pattern['best_hours'],
            'reasoning': [f'أفضل أوقات النشر لمحتوى {category}'],
            'additional_tips': ['انشر بانتظام', 'تفاعل مع التعليقات']
        }
    
    def _analyze_posting_patterns(self, videos):
        """Analyze historical posting patterns"""
        if not videos:
            return {'posting_frequency': 'غير منتظم', 'common_days': [], 'common_hours': []}
        
        posting_times = []
        for video in videos:
            if video.get('published_at'):
                try:
                    pub_time = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                    posting_times.append(pub_time)
                except:
                    continue
        
        if not posting_times:
            return {'posting_frequency': 'غير منتظم', 'common_days': [], 'common_hours': []}
        
        # Analyze days of week
        days_count = {}
        hours_count = {}
        
        for time in posting_times:
            day_name = self._get_arabic_day_name(time.weekday())
            hour = time.hour
            
            days_count[day_name] = days_count.get(day_name, 0) + 1
            hours_count[hour] = hours_count.get(hour, 0) + 1
        
        # Get most common days and hours
        common_days = sorted(days_count.keys(), key=lambda x: days_count[x], reverse=True)[:3]
        common_hours = sorted(hours_count.keys(), key=lambda x: hours_count[x], reverse=True)[:3]
        
        # Calculate posting frequency
        if len(posting_times) > 1:
            time_diff = max(posting_times) - min(posting_times)
            avg_interval = time_diff.days / len(posting_times)
            if avg_interval < 3:
                frequency = 'يومي'
            elif avg_interval < 7:
                frequency = 'أسبوعي'
            elif avg_interval < 30:
                frequency = 'شهري'
            else:
                frequency = 'غير منتظم'
        else:
            frequency = 'غير منتظم'
        
        return {
            'posting_frequency': frequency,
            'common_days': common_days,
            'common_hours': common_hours,
            'total_videos': len(videos),
            'analysis_period': len(posting_times)
        }
    
    def _determine_content_category(self, channel_info, videos):
        """Determine content category from channel info and videos"""
        # Simple keyword-based categorization
        text_content = f"{channel_info.get('title', '')} {channel_info.get('description', '')}"
        
        # Add video titles for better analysis
        for video in videos[:5]:  # Check first 5 videos
            text_content += f" {video.get('title', '')}"
        
        text_content = text_content.lower()
        
        # Category keywords
        categories = {
            'تعليم': ['تعليم', 'شرح', 'دروس', 'كورس', 'تعلم', 'دليل', 'كيف'],
            'ترفيه': ['ترفيه', 'كوميدي', 'مضحك', 'تحدي', 'فلوق', 'مقلب'],
            'تقنية': ['تقنية', 'برمجة', 'كمبيوتر', 'تطوير', 'تطبيق', 'موقع'],
            'رياضة': ['رياضة', 'كرة', 'لعب', 'فريق', 'مباراة', 'تمرين'],
            'موسيقى': ['موسيقى', 'أغنية', 'مطرب', 'فنان', 'إيقاع', 'لحن'],
            'طبخ': ['طبخ', 'وصفة', 'أكل', 'طعام', 'مطبخ', 'طبخة']
        }
        
        max_matches = 0
        detected_category = 'عام'
        
        for category, keywords in categories.items():
            matches = sum(1 for keyword in keywords if keyword in text_content)
            if matches > max_matches:
                max_matches = matches
                detected_category = category
        
        return detected_category
    
    def _get_ai_timing_analysis(self, channel_info, posting_patterns, content_category):
        """Get AI-powered timing analysis"""
        try:
            context = {
                'channel_title': channel_info.get('title', ''),
                'subscriber_count': channel_info.get('subscriber_count', 0),
                'content_category': content_category,
                'posting_patterns': posting_patterns
            }
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """أنت خبير تحليل توقيت النشر على يوتيوب متخصص في الجمهور العربي.
                        
                        قم بتحليل البيانات المعطاة وتوصي بأفضل أوقات النشر مع مراعاة:
                        1. نوع المحتوى
                        2. حجم الجمهور
                        3. أنماط النشر الحالية
                        4. السلوك العام للجمهور العربي
                        5. العوامل الموسمية
                        
                        أعط توصيات مفصلة مع التبرير."""
                    },
                    {
                        "role": "user",
                        "content": f"حلل أفضل توقيت للنشر: {json.dumps(context, ensure_ascii=False)}"
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logging.error(f"Error in AI timing analysis: {str(e)}")
            return {
                'recommendations': ['انشر في المساء'],
                'seasonal_factors': {'رمضان': 'أوقات مختلفة'},
                'reasoning': ['تحليل عام']
            }
    
    def _get_ai_category_timing(self, category, target_audience):
        """Get AI timing recommendations for specific category"""
        try:
            context = {
                'category': category,
                'target_audience': target_audience
            }
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """أنت خبير توقيت النشر على يوتيوب للجمهور العربي.
                        أعط توصيات دقيقة لأفضل أوقات النشر حسب فئة المحتوى والجمهور المستهدف."""
                    },
                    {
                        "role": "user",
                        "content": f"ما أفضل توقيت للنشر؟ {json.dumps(context, ensure_ascii=False)}"
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Error in AI category timing: {str(e)}")
            return {}
    
    def _calculate_optimal_timing(self, content_category, posting_patterns, ai_analysis):
        """Calculate optimal timing based on all factors"""
        # Get base recommendations for content category
        base_timing = self.general_patterns['content_categories'].get(
            content_category, 
            self.general_patterns['content_categories']['عام']
        )
        
        # Combine with AI analysis
        ai_days = ai_analysis.get('best_days', [])
        ai_hours = ai_analysis.get('best_hours', [])
        
        # Merge recommendations
        best_days = list(set(base_timing['best_days'] + ai_days))[:4]
        best_hours = list(set(base_timing['best_hours'] + ai_hours))[:4]
        
        # Sort by preference
        if not best_days:
            best_days = base_timing['best_days']
        if not best_hours:
            best_hours = base_timing['best_hours']
        
        # Calculate confidence based on data quality
        confidence = 0.7  # Base confidence
        if posting_patterns.get('analysis_period', 0) > 10:
            confidence += 0.1
        if ai_analysis:
            confidence += 0.1
        
        return {
            'best_days': best_days,
            'best_hours': best_hours,
            'activity_pattern': 'مساء عادة أفضل للجمهور العربي',
            'engagement_peaks': ['20:00-22:00', '14:00-16:00 (نهاية الأسبوع)'],
            'confidence': min(1.0, confidence),
            'content_specific': {
                'category': content_category,
                'reasoning': f'مجال {content_category} يحتاج توقيت خاص'
            }
        }
    
    def _assess_data_quality(self, videos):
        """Assess the quality of data for analysis"""
        if not videos:
            return 'منخفض'
        elif len(videos) < 5:
            return 'منخفض'
        elif len(videos) < 15:
            return 'متوسط'
        else:
            return 'عالي'
    
    def _get_arabic_day_name(self, weekday):
        """Convert weekday number to Arabic day name"""
        days = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
        return days[weekday]
    
    def _get_demo_timing_analysis(self, channel_info):
        """Demo timing analysis for testing purposes"""
        return {
            'best_days': ['الخميس', 'الجمعة', 'السبت'],
            'best_hours': [20, 21, 22],
            'timezone': 'Asia/Riyadh',
            'audience_data': {
                'primary_timezone': 'GMT+3',
                'activity_pattern': 'نشاط مسائي عالي',
                'engagement_peaks': ['20:00-22:00', '14:00-16:00']
            },
            'confidence_score': 0.75,
            'data_quality': 'متوسط',
            'recommendations': [
                'انشر في المساء بين الساعة 8-10 مساءً',
                'نهاية الأسبوع أفضل للمحتوى الترفيهي',
                'تجنب أوقات الصلاة والوجبات الرئيسية',
                'اختبر أوقات مختلفة وقس النتائج'
            ],
            'seasonal_considerations': {
                'رمضان': 'انشر بعد الإفطار (20:30-23:00)',
                'الصيف': 'انشر متأخراً (21:00-23:00)',
                'الشتاء': 'انشر مبكراً (19:00-21:00)',
                'المدرسة': 'تجنب ساعات الدراسة (8:00-15:00)'
            },
            'content_specific_timing': {
                'تعليمي': 'مساء أيام الأسبوع',
                'ترفيهي': 'نهاية الأسبوع',
                'ديني': 'بعد الصلوات',
                'رياضي': 'مساء الخميس والجمعة'
            }
        }
