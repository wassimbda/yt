import os
import json
import logging
import re
from collections import Counter
from openai import OpenAI

class NicheDetector:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', 'sk-fallback-key'))
        self.demo_mode = not os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY') == 'sk-fallback-key'
        
        # Predefined niche categories with Arabic keywords
        self.niche_keywords = {
            'تعليم وتطوير': [
                'تعليم', 'شرح', 'دروس', 'كورس', 'تعلم', 'دليل', 'كيف', 'طريقة',
                'نصائح', 'مهارات', 'تطوير', 'دورة', 'أساسيات', 'متقدم'
            ],
            'تقنية وبرمجة': [
                'تقنية', 'برمجة', 'كمبيوتر', 'تطوير', 'تطبيق', 'موقع', 'ذكي',
                'اصطناعي', 'تكنولوجيا', 'ديجيتال', 'سوفتوير', 'هاردوير'
            ],
            'ترفيه وكوميديا': [
                'ترفيه', 'كوميدي', 'مضحك', 'تحدي', 'فلوق', 'مقلب', 'لعب',
                'مسلي', 'مرح', 'ضحك', 'فكاهة', 'تسلية'
            ],
            'رياضة ولياقة': [
                'رياضة', 'كرة', 'لعب', 'فريق', 'مباراة', 'تمرين', 'لياقة',
                'جيم', 'رياضی', 'بدني', 'صحة', 'عضلات'
            ],
            'طبخ وطعام': [
                'طبخ', 'وصفة', 'أكل', 'طعام', 'مطبخ', 'طبخة', 'حلويات',
                'سلطة', 'عشاء', 'فطار', 'غداء', 'طبيخ'
            ],
            'موسيقى وفن': [
                'موسيقى', 'أغنية', 'مطرب', 'فنان', 'إيقاع', 'لحن', 'غناء',
                'عزف', 'آلة', 'موسيقية', 'فن', 'رسم'
            ],
            'سفر وثقافة': [
                'سفر', 'رحلة', 'سياحة', 'بلد', 'مدينة', 'ثقافة', 'تاريخ',
                'حضارة', 'تراث', 'أماكن', 'معالم'
            ],
            'أعمال ومال': [
                'أعمال', 'مال', 'استثمار', 'تجارة', 'ربح', 'اقتصاد', 'مشروع',
                'شركة', 'تسويق', 'بيع', 'شراء', 'أموال'
            ],
            'صحة وجمال': [
                'صحة', 'جمال', 'عناية', 'بشرة', 'شعر', 'مكياج', 'رشاقة',
                'نظافة', 'طبيعي', 'علاج', 'وقاية'
            ],
            'عائله وأطفال': [
                'عائلة', 'أطفال', 'أم', 'أب', 'طفل', 'تربية', 'أسرة',
                'زواج', 'حمل', 'والدة', 'عناية'
            ],
            'دين وروحانيات': [
                'دين', 'إسلام', 'قرآن', 'حديث', 'صلاة', 'روحاني', 'دعاء',
                'فقه', 'سيرة', 'إيمان', 'عبادة'
            ],
            'ألعاب': [
                'ألعاب', 'جيمنج', 'لعبة', 'بلاي', 'كونسول', 'موبايل',
                'محاكي', 'مغامرة', 'أكشن', 'إستراتيجية'
            ]
        }
    
    def detect_niche(self, channel_info, videos):
        """Detect channel niche using multiple analysis methods"""
        if self.demo_mode:
            return self._get_demo_niche_detection(channel_info)
        
        try:
            # Collect text content for analysis
            text_content = self._collect_text_content(channel_info, videos)
            
            # Keyword-based analysis
            keyword_analysis = self._analyze_keywords(text_content)
            
            # AI-powered niche detection
            ai_analysis = self._get_ai_niche_analysis(channel_info, videos)
            
            # Content pattern analysis
            pattern_analysis = self._analyze_content_patterns(videos)
            
            # Combine all analyses
            final_niche = self._combine_analyses(keyword_analysis, ai_analysis, pattern_analysis)
            
            result = {
                'primary_niche': final_niche['primary'],
                'secondary_niches': final_niche['secondary'],
                'confidence_score': final_niche['confidence'],
                'niche_evolution': pattern_analysis.get('evolution', 'مستقر'),
                'keyword_analysis': keyword_analysis,
                'content_consistency': pattern_analysis.get('consistency', 0.7),
                'recommendations': ai_analysis.get('recommendations', []),
                'growth_potential': ai_analysis.get('growth_potential', {}),
                'competition_level': ai_analysis.get('competition_level', 'متوسط'),
                'target_audience': ai_analysis.get('target_audience', {}),
                'monetization_opportunities': ai_analysis.get('monetization', [])
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error in niche detection: {str(e)}")
            return self._get_demo_niche_detection(channel_info)
    
    def _collect_text_content(self, channel_info, videos):
        """Collect all text content for analysis"""
        content = []
        
        # Channel info
        content.append(channel_info.get('title', ''))
        content.append(channel_info.get('description', ''))
        content.append(channel_info.get('keywords', ''))
        
        # Video titles and descriptions
        for video in videos[:20]:  # Analyze up to 20 recent videos
            content.append(video.get('title', ''))
            content.append(video.get('description', '')[:200])  # First 200 chars
        
        return ' '.join(content).lower()
    
    def _analyze_keywords(self, text_content):
        """Analyze keywords to determine niche"""
        niche_scores = {}
        
        for niche, keywords in self.niche_keywords.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                # Count occurrences of each keyword
                count = text_content.count(keyword)
                if count > 0:
                    score += count
                    matched_keywords.append({'keyword': keyword, 'count': count})
            
            if score > 0:
                niche_scores[niche] = {
                    'score': score,
                    'matched_keywords': matched_keywords,
                    'keyword_diversity': len(matched_keywords)
                }
        
        # Sort by score
        sorted_niches = sorted(niche_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        return {
            'top_niches': sorted_niches[:5],
            'total_matches': sum(data['score'] for _, data in sorted_niches),
            'keyword_distribution': {niche: data['score'] for niche, data in sorted_niches}
        }
    
    def _get_ai_niche_analysis(self, channel_info, videos):
        """Get AI-powered niche analysis"""
        try:
            # Prepare data for AI analysis
            video_data = []
            for video in videos[:10]:
                video_data.append({
                    'title': video.get('title', ''),
                    'description': video.get('description', '')[:100],
                    'view_count': video.get('view_count', 0)
                })
            
            context = {
                'channel': {
                    'title': channel_info.get('title', ''),
                    'description': channel_info.get('description', '')[:300],
                    'subscriber_count': channel_info.get('subscriber_count', 0)
                },
                'recent_videos': video_data
            }
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """أنت خبير تحليل محتوى يوتيوب متخصص في تحديد مجالات القنوات.
                        
                        قم بتحليل البيانات المعطاة وحدد:
                        1. المجال الأساسي للقناة
                        2. المجالات الفرعية
                        3. مستوى الثقة في التحديد
                        4. إمكانيات النمو
                        5. مستوى المنافسة
                        6. الجمهور المستهدف
                        7. فرص الربح
                        8. توصيات للتحسين
                        
                        استخدم المجالات التالية كمرجع:
                        تعليم وتطوير، تقنية وبرمجة، ترفيه وكوميديا، رياضة ولياقة،
                        طبخ وطعام، موسيقى وفن، سفر وثقافة، أعمال ومال،
                        صحة وجمال، عائلة وأطفال، دين وروحانيات، ألعاب
                        
                        أرجع النتيجة بصيغة JSON."""
                    },
                    {
                        "role": "user",
                        "content": f"حلل مجال هذه القناة: {json.dumps(context, ensure_ascii=False)}"
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Standardize field names
            return {
                'primary_niche': result.get('primary_niche', result.get('المجال_الأساسي', 'عام')),
                'secondary_niches': result.get('secondary_niches', result.get('المجالات_الفرعية', [])),
                'confidence': result.get('confidence', result.get('مستوى_الثقة', 0.7)),
                'growth_potential': result.get('growth_potential', result.get('إمكانيات_النمو', {})),
                'competition_level': result.get('competition_level', result.get('مستوى_المنافسة', 'متوسط')),
                'target_audience': result.get('target_audience', result.get('الجمهور_المستهدف', {})),
                'monetization': result.get('monetization', result.get('فرص_الربح', [])),
                'recommendations': result.get('recommendations', result.get('توصيات', []))
            }
            
        except Exception as e:
            logging.error(f"Error in AI niche analysis: {str(e)}")
            return {
                'primary_niche': 'عام',
                'secondary_niches': [],
                'confidence': 0.5,
                'growth_potential': {'level': 'متوسط'},
                'competition_level': 'متوسط',
                'target_audience': {'age': '18-35'},
                'monetization': ['إعلانات'],
                'recommendations': ['تحسين المحتوى']
            }
    
    def _analyze_content_patterns(self, videos):
        """Analyze content patterns and consistency"""
        if not videos:
            return {'consistency': 0.5, 'evolution': 'غير محدد'}
        
        # Analyze video titles for patterns
        titles = [video.get('title', '') for video in videos]
        
        # Check for common words across titles
        all_words = []
        for title in titles:
            words = re.findall(r'\w+', title.lower())
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        common_words = [word for word, count in word_freq.most_common(10) if count > 1]
        
        # Calculate consistency based on common themes
        consistency = min(1.0, len(common_words) / 10)
        
        # Analyze evolution (simple approach)
        if len(videos) > 5:
            recent_titles = ' '.join(titles[:5]).lower()
            older_titles = ' '.join(titles[-5:]).lower()
            
            # Simple similarity check
            recent_words = set(re.findall(r'\w+', recent_titles))
            older_words = set(re.findall(r'\w+', older_titles))
            
            overlap = len(recent_words.intersection(older_words))
            total_unique = len(recent_words.union(older_words))
            
            if total_unique > 0:
                similarity = overlap / total_unique
                if similarity > 0.7:
                    evolution = 'مستقر'
                elif similarity > 0.4:
                    evolution = 'تطور تدريجي'
                else:
                    evolution = 'تغيير كبير'
            else:
                evolution = 'غير محدد'
        else:
            evolution = 'بيانات غير كافية'
        
        return {
            'consistency': consistency,
            'evolution': evolution,
            'common_themes': common_words[:5],
            'content_variety': len(set(titles)) / len(titles) if titles else 0
        }
    
    def _combine_analyses(self, keyword_analysis, ai_analysis, pattern_analysis):
        """Combine different analyses to determine final niche"""
        # Get top niche from keyword analysis
        keyword_niche = None
        if keyword_analysis['top_niches']:
            keyword_niche = keyword_analysis['top_niches'][0][0]
        
        # Get AI suggested niche
        ai_niche = ai_analysis.get('primary_niche', 'عام')
        
        # Determine primary niche
        if ai_niche and ai_niche != 'عام':
            primary_niche = ai_niche
            confidence = ai_analysis.get('confidence', 0.7)
        elif keyword_niche:
            primary_niche = keyword_niche
            confidence = 0.6
        else:
            primary_niche = 'عام'
            confidence = 0.3
        
        # Determine secondary niches
        secondary_niches = []
        
        # Add from keyword analysis
        if keyword_analysis['top_niches']:
            for niche, data in keyword_analysis['top_niches'][1:4]:
                if niche != primary_niche:
                    secondary_niches.append(niche)
        
        # Add from AI analysis
        ai_secondary = ai_analysis.get('secondary_niches', [])
        for niche in ai_secondary:
            if niche not in secondary_niches and niche != primary_niche:
                secondary_niches.append(niche)
        
        # Adjust confidence based on content consistency
        content_consistency = pattern_analysis.get('consistency', 0.5)
        confidence = confidence * (0.7 + 0.3 * content_consistency)
        
        return {
            'primary': primary_niche,
            'secondary': secondary_niches[:3],  # Limit to 3 secondary niches
            'confidence': min(1.0, confidence)
        }
    
    def _get_demo_niche_detection(self, channel_info):
        """Demo niche detection for testing purposes"""
        # Simple keyword-based detection for demo
        title = channel_info.get('title', '').lower()
        description = channel_info.get('description', '').lower()
        content = f"{title} {description}"
        
        # Check for obvious indicators
        if any(word in content for word in ['تعليم', 'شرح', 'دروس']):
            primary_niche = 'تعليم وتطوير'
        elif any(word in content for word in ['تقنية', 'برمجة', 'تطوير']):
            primary_niche = 'تقنية وبرمجة'
        elif any(word in content for word in ['ترفيه', 'كوميدي', 'مضحك']):
            primary_niche = 'ترفيه وكوميديا'
        elif any(word in content for word in ['طبخ', 'وصفة', 'طعام']):
            primary_niche = 'طبخ وطعام'
        else:
            primary_niche = 'عام'
        
        return {
            'primary_niche': primary_niche,
            'secondary_niches': ['تعليم وتطوير', 'ترفيه وكوميديا'],
            'confidence_score': 0.75,
            'niche_evolution': 'مستقر',
            'keyword_analysis': {
                'top_niches': [(primary_niche, {'score': 10})],
                'total_matches': 10
            },
            'content_consistency': 0.8,
            'recommendations': [
                'التركيز على المجال الأساسي',
                'تطوير محتوى متخصص أكثر',
                'استخدام كلمات مفتاحية محددة',
                'بناء جمهور مستهدف'
            ],
            'growth_potential': {
                'level': 'عالي',
                'factors': ['طلب متزايد', 'منافسة معتدلة', 'فرص كبيرة']
            },
            'competition_level': 'متوسط',
            'target_audience': {
                'age_group': '18-35 سنة',
                'interests': [primary_niche],
                'behavior': 'نشيط على منصات التواصل'
            },
            'monetization_opportunities': [
                'إعلانات يوتيوب',
                'الرعايات المدفوعة',
                'بيع الكورسات',
                'التسويق بالعمولة',
                'المنتجات الرقمية'
            ]
        }
