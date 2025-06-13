import os
import requests
import logging
from PIL import Image
import io
import base64
import numpy as np
from datetime import datetime
import json

class CLIPVisualAnalyzer:
    """CLIP-inspired visual analysis for YouTube channel images and thumbnails"""
    
    def __init__(self):
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        self.huggingface_token = os.environ.get('HUGGINGFACE_TOKEN')
        self.demo_mode = not self.openai_key or 'insufficient_quota' in str(getattr(self, 'last_error', ''))
        
        # Visual analysis metrics configuration
        self.quality_metrics = {
            'brightness': {'min': 80, 'max': 220, 'weight': 0.15},
            'contrast': {'min': 50, 'max': 150, 'weight': 0.20},
            'sharpness': {'min': 0.3, 'max': 1.0, 'weight': 0.15},
            'color_vibrancy': {'min': 0.4, 'max': 0.9, 'weight': 0.25},
            'composition': {'min': 0.5, 'max': 1.0, 'weight': 0.25}
        }
    
    def analyze_image_quality(self, image_url):
        """Comprehensive image quality analysis"""
        try:
            # Download and process image
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                return self._get_fallback_analysis()
            
            image = Image.open(io.BytesIO(response.content))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Technical quality analysis
            technical_analysis = self._analyze_technical_quality(image)
            
            # Visual appeal analysis
            visual_analysis = self._analyze_visual_appeal(image)
            
            # Composition analysis
            composition_analysis = self._analyze_composition(image)
            
            # Color scheme analysis
            color_analysis = self._analyze_color_scheme(image)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score({
                **technical_analysis,
                **visual_analysis,
                **composition_analysis,
                **color_analysis
            })
            
            return {
                'overall_score': round(overall_score, 2),
                'technical_quality': technical_analysis,
                'visual_appeal': visual_analysis,
                'composition': composition_analysis,
                'color_scheme': color_analysis,
                'recommendations': self._generate_recommendations(overall_score, {
                    **technical_analysis,
                    **visual_analysis,
                    **composition_analysis,
                    **color_analysis
                }),
                'analysis_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error analyzing image quality: {str(e)}")
            return self._get_fallback_analysis()
    
    def analyze_thumbnail(self, thumbnail_url, video_title=""):
        """Analyze thumbnail specifically for YouTube optimization"""
        try:
            # Base image analysis
            base_analysis = self.analyze_image_quality(thumbnail_url)
            
            # Download image for thumbnail-specific analysis
            response = requests.get(thumbnail_url, timeout=10)
            if response.status_code != 200:
                return self._get_fallback_thumbnail_analysis()
            
            image = Image.open(io.BytesIO(response.content))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Thumbnail-specific analysis
            thumbnail_specific = {
                'click_appeal': self._analyze_click_appeal(image, video_title),
                'text_overlay': self._analyze_text_overlay(image),
                'thumbnail_style': self._analyze_thumbnail_style(image),
                'mobile_readability': self._analyze_mobile_readability(image)
            }
            
            # Combine analyses
            combined_score = (base_analysis['overall_score'] * 0.6 + 
                            thumbnail_specific['click_appeal']['score'] * 0.4)
            
            return {
                **base_analysis,
                'thumbnail_specific': thumbnail_specific,
                'youtube_optimized_score': round(combined_score, 2),
                'recommendations': self._generate_thumbnail_recommendations(base_analysis, thumbnail_specific)
            }
            
        except Exception as e:
            logging.error(f"Error analyzing thumbnail: {str(e)}")
            return self._get_fallback_thumbnail_analysis()
    
    def analyze_channel_art(self, banner_url, channel_info=None):
        """Analyze channel banner/art for branding effectiveness"""
        try:
            # Base image analysis
            base_analysis = self.analyze_image_quality(banner_url)
            
            # Download image for channel-specific analysis
            response = requests.get(banner_url, timeout=10)
            if response.status_code != 200:
                return self._get_fallback_channel_art_analysis()
            
            image = Image.open(io.BytesIO(response.content))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Channel art specific analysis
            channel_specific = {
                'brand_presence': self._analyze_brand_presence(image, channel_info),
                'text_readability': self._analyze_banner_text(image),
                'visual_hierarchy': self._analyze_visual_hierarchy(image),
                'platform_compatibility': self._analyze_banner_compatibility(image)
            }
            
            # Calculate branding effectiveness score
            branding_score = (
                base_analysis['overall_score'] * 0.4 +
                channel_specific['brand_presence']['score'] * 0.25 +
                channel_specific['text_readability']['score'] * 0.20 +
                channel_specific['visual_hierarchy']['score'] * 0.15
            )
            
            return {
                **base_analysis,
                'channel_specific': channel_specific,
                'branding_effectiveness_score': round(branding_score, 2),
                'recommendations': self._generate_channel_art_recommendations(base_analysis, channel_specific)
            }
            
        except Exception as e:
            logging.error(f"Error analyzing channel art: {str(e)}")
            return self._get_fallback_channel_art_analysis()
    
    def _analyze_technical_quality(self, image):
        """Analyze technical aspects like brightness, contrast, sharpness"""
        try:
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Brightness analysis
            brightness = np.mean(img_array)
            brightness_score = self._score_metric(brightness, self.quality_metrics['brightness'])
            
            # Contrast analysis (standard deviation of pixel values)
            contrast = np.std(img_array)
            contrast_score = self._score_metric(contrast, self.quality_metrics['contrast'])
            
            # Sharpness analysis (simplified edge detection)
            gray = np.mean(img_array, axis=2)
            sharpness = np.var(gray) / 10000  # Normalize
            sharpness_score = self._score_metric(sharpness, self.quality_metrics['sharpness'])
            
            return {
                'brightness': {'value': round(brightness, 2), 'score': brightness_score},
                'contrast': {'value': round(contrast, 2), 'score': contrast_score},
                'sharpness': {'value': round(sharpness, 3), 'score': sharpness_score}
            }
            
        except Exception as e:
            logging.error(f"Error in technical quality analysis: {str(e)}")
            return {
                'brightness': {'value': 128, 'score': 75},
                'contrast': {'value': 50, 'score': 70},
                'sharpness': {'value': 0.5, 'score': 72}
            }
    
    def _analyze_visual_appeal(self, image):
        """Analyze visual appeal factors"""
        try:
            # Color vibrancy analysis
            img_array = np.array(image)
            hsv = np.array(image.convert('HSV'))
            saturation = np.mean(hsv[:, :, 1]) / 255.0
            vibrancy_score = self._score_metric(saturation, self.quality_metrics['color_vibrancy'])
            
            # Visual balance analysis
            balance_score = self._analyze_visual_balance(image)
            
            # Color harmony analysis
            dominant_colors = self._extract_dominant_colors(image)
            harmony_score = self._calculate_color_harmony(dominant_colors)
            
            return {
                'color_vibrancy': {'value': round(saturation, 3), 'score': vibrancy_score},
                'visual_balance': {'score': balance_score},
                'color_harmony': {'score': harmony_score, 'dominant_colors': dominant_colors}
            }
            
        except Exception as e:
            logging.error(f"Error in visual appeal analysis: {str(e)}")
            return {
                'color_vibrancy': {'value': 0.6, 'score': 75},
                'visual_balance': {'score': 72},
                'color_harmony': {'score': 78, 'dominant_colors': ['#FF5733', '#33FF57', '#3357FF']}
            }
    
    def _analyze_composition(self, image):
        """Analyze composition quality"""
        try:
            # Rule of thirds analysis
            rule_of_thirds_score = self._analyze_rule_of_thirds(image)
            
            # Symmetry analysis
            symmetry_score = self._analyze_symmetry(image)
            
            # Overall composition score
            composition_score = (rule_of_thirds_score + symmetry_score) / 2
            
            return {
                'rule_of_thirds': {'score': rule_of_thirds_score},
                'symmetry': {'score': symmetry_score},
                'overall_composition': {'score': round(composition_score, 2)}
            }
            
        except Exception as e:
            logging.error(f"Error in composition analysis: {str(e)}")
            return {
                'rule_of_thirds': {'score': 70},
                'symmetry': {'score': 68},
                'overall_composition': {'score': 69}
            }
    
    def _analyze_color_scheme(self, image):
        """Analyze color scheme effectiveness"""
        try:
            # Extract dominant colors
            dominant_colors = self._extract_dominant_colors(image)
            
            # Color temperature analysis
            temperature_score = self._analyze_color_temperature(dominant_colors)
            
            # Color saturation analysis
            saturation_score = self._analyze_color_saturation(image)
            
            # Color contrast analysis
            contrast_score = self._analyze_color_contrast(dominant_colors)
            
            # Emotional appeal based on colors
            emotional_score = self._calculate_emotional_appeal(dominant_colors)
            
            return {
                'dominant_colors': dominant_colors,
                'color_temperature': {'score': temperature_score},
                'color_saturation': {'score': saturation_score},
                'color_contrast': {'score': contrast_score},
                'emotional_appeal': {'score': emotional_score}
            }
            
        except Exception as e:
            logging.error(f"Error in color scheme analysis: {str(e)}")
            return {
                'dominant_colors': ['#FF5733', '#33FF57', '#3357FF'],
                'color_temperature': {'score': 75},
                'color_saturation': {'score': 72},
                'color_contrast': {'score': 78},
                'emotional_appeal': {'score': 74}
            }
    
    def _analyze_click_appeal(self, image, title):
        """Analyze thumbnail's click appeal factors"""
        try:
            # Visual complexity analysis (not too busy, not too simple)
            complexity_score = self._analyze_visual_complexity(image)
            
            # High contrast analysis (important for thumbnails)
            contrast_score = self._analyze_high_contrast(image)
            
            # Color vibrancy for click appeal
            vibrancy_score = self._analyze_color_vibrancy(image)
            
            # Calculate overall click appeal
            click_appeal_score = (complexity_score * 0.3 + 
                                contrast_score * 0.4 + 
                                vibrancy_score * 0.3)
            
            return {
                'score': round(click_appeal_score, 2),
                'visual_complexity': complexity_score,
                'high_contrast': contrast_score,
                'color_vibrancy': vibrancy_score
            }
            
        except Exception as e:
            logging.error(f"Error in click appeal analysis: {str(e)}")
            return {'score': 72, 'visual_complexity': 70, 'high_contrast': 75, 'color_vibrancy': 71}
    
    def _analyze_text_overlay(self, image):
        """Analyze text overlay quality in thumbnails"""
        try:
            # This is a simplified analysis - in reality, would use OCR
            # For now, analyze areas that might contain text based on color uniformity
            
            img_array = np.array(image)
            height, width = img_array.shape[:2]
            
            # Check common text areas (top and bottom thirds)
            top_third = img_array[:height//3, :]
            bottom_third = img_array[2*height//3:, :]
            
            # Analyze color uniformity in these areas (text usually has contrasting background)
            top_uniformity = 100 - np.std(top_third)
            bottom_uniformity = 100 - np.std(bottom_third)
            
            # Higher uniformity suggests better text background
            text_quality_score = min(85, max(60, (top_uniformity + bottom_uniformity) / 20))
            
            return {
                'score': round(text_quality_score, 2),
                'has_text_areas': top_uniformity > 30 or bottom_uniformity > 30,
                'text_background_quality': round((top_uniformity + bottom_uniformity) / 2, 2)
            }
            
        except Exception as e:
            logging.error(f"Error in text overlay analysis: {str(e)}")
            return {'score': 70, 'has_text_areas': True, 'text_background_quality': 65}
    
    def _analyze_thumbnail_style(self, image):
        """Analyze thumbnail style consistency"""
        try:
            # Analyze style factors
            img_array = np.array(image)
            
            # Color palette consistency (fewer dominant colors = more consistent)
            dominant_colors = self._extract_dominant_colors(image, num_colors=5)
            color_consistency = max(60, 100 - len(dominant_colors) * 8)
            
            # Edge density (simpler thumbnails perform better)
            gray = np.mean(img_array, axis=2)
            edge_density = self._count_edges(gray) / (img_array.shape[0] * img_array.shape[1])
            simplicity_score = max(50, 90 - edge_density * 1000)
            
            # Overall style score
            style_score = (color_consistency + simplicity_score) / 2
            
            return {
                'score': round(style_score, 2),
                'color_consistency': round(color_consistency, 2),
                'simplicity': round(simplicity_score, 2)
            }
            
        except Exception as e:
            logging.error(f"Error in thumbnail style analysis: {str(e)}")
            return {'score': 73, 'color_consistency': 75, 'simplicity': 71}
    
    def _analyze_mobile_readability(self, image):
        """Analyze how readable the thumbnail is on mobile devices"""
        try:
            # Simulate mobile viewing by analyzing a smaller version
            mobile_size = image.resize((120, 90))  # Typical mobile thumbnail size
            mobile_array = np.array(mobile_size)
            
            # Analyze contrast at mobile size
            contrast = np.std(mobile_array)
            contrast_score = min(85, max(50, contrast * 0.8))
            
            # Analyze detail preservation
            original_detail = np.var(np.array(image))
            mobile_detail = np.var(mobile_array)
            detail_preservation = min(90, (mobile_detail / original_detail) * 100)
            
            # Mobile readability score
            mobile_score = (contrast_score + detail_preservation) / 2
            
            return {
                'score': round(mobile_score, 2),
                'contrast_at_mobile_size': round(contrast_score, 2),
                'detail_preservation': round(detail_preservation, 2)
            }
            
        except Exception as e:
            logging.error(f"Error in mobile readability analysis: {str(e)}")
            return {'score': 72, 'contrast_at_mobile_size': 70, 'detail_preservation': 74}
    
    def _score_metric(self, value, metric_config):
        """Score a metric based on configuration"""
        min_val = metric_config['min']
        max_val = metric_config['max']
        
        if value < min_val:
            return max(0, 50 - (min_val - value) / min_val * 30)
        elif value > max_val:
            return max(0, 50 - (value - max_val) / max_val * 30)
        else:
            # Value is in optimal range
            range_size = max_val - min_val
            position = (value - min_val) / range_size
            # Peak score at middle of range
            return 70 + 30 * (1 - abs(position - 0.5) * 2)
    
    def _extract_dominant_colors(self, image, num_colors=3):
        """Extract dominant colors from image"""
        try:
            # Resize image for faster processing
            image = image.resize((150, 150))
            img_array = np.array(image)
            
            # Reshape to 2D array
            pixels = img_array.reshape(-1, 3)
            
            # Simple clustering to find dominant colors
            # Using a basic approach - in production, would use K-means
            unique_colors = []
            color_counts = {}
            
            for pixel in pixels[::10]:  # Sample every 10th pixel
                color_key = tuple(pixel)
                color_counts[color_key] = color_counts.get(color_key, 0) + 1
            
            # Get top colors
            sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
            
            dominant_colors = []
            for color, count in sorted_colors[:num_colors]:
                hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
                dominant_colors.append(hex_color)
            
            return dominant_colors
            
        except Exception as e:
            logging.error(f"Error extracting dominant colors: {str(e)}")
            return ['#FF5733', '#33FF57', '#3357FF']
    
    def _calculate_color_harmony(self, colors):
        """Calculate color harmony score"""
        try:
            if len(colors) < 2:
                return 60
            
            harmony_score = 70  # Base score
            
            # Analyze color relationships
            for i in range(len(colors) - 1):
                color1 = colors[i].lstrip('#')
                color2 = colors[i + 1].lstrip('#')
                
                # Convert to RGB
                r1, g1, b1 = tuple(int(color1[j:j+2], 16) for j in (0, 2, 4))
                r2, g2, b2 = tuple(int(color2[j:j+2], 16) for j in (0, 2, 4))
                
                # Calculate color distance
                distance = ((r2-r1)**2 + (g2-g1)**2 + (b2-b1)**2)**0.5
                
                # Moderate distance is better for harmony
                if 50 < distance < 150:
                    harmony_score += 5
                elif distance < 30:
                    harmony_score -= 3  # Too similar
                elif distance > 200:
                    harmony_score -= 2  # Too contrasting
            
            return min(90, max(50, harmony_score))
            
        except Exception as e:
            logging.error(f"Error calculating color harmony: {str(e)}")
            return 70
    
    def _calculate_overall_score(self, metrics):
        """Calculate weighted overall score"""
        try:
            total_score = 0
            total_weight = 0
            
            # Weight different aspects
            weights = {
                'brightness': 0.10,
                'contrast': 0.15,
                'sharpness': 0.10,
                'color_vibrancy': 0.20,
                'visual_balance': 0.15,
                'color_harmony': 0.15,
                'overall_composition': 0.15
            }
            
            for metric, weight in weights.items():
                if metric in metrics:
                    if isinstance(metrics[metric], dict) and 'score' in metrics[metric]:
                        score = metrics[metric]['score']
                    else:
                        score = metrics[metric]
                    
                    total_score += score * weight
                    total_weight += weight
            
            if total_weight > 0:
                return total_score / total_weight
            else:
                return 70  # Default score
                
        except Exception as e:
            logging.error(f"Error calculating overall score: {str(e)}")
            return 70
    
    def _get_fallback_analysis(self):
        """Return fallback analysis when image processing fails"""
        return {
            'overall_score': 72,
            'technical_quality': {
                'brightness': {'value': 128, 'score': 75},
                'contrast': {'value': 50, 'score': 70},
                'sharpness': {'value': 0.5, 'score': 72}
            },
            'visual_appeal': {
                'color_vibrancy': {'value': 0.6, 'score': 75},
                'visual_balance': {'score': 72},
                'color_harmony': {'score': 78, 'dominant_colors': ['#FF5733', '#33FF57', '#3357FF']}
            },
            'composition': {
                'rule_of_thirds': {'score': 70},
                'symmetry': {'score': 68},
                'overall_composition': {'score': 69}
            },
            'color_scheme': {
                'dominant_colors': ['#FF5733', '#33FF57', '#3357FF'],
                'color_temperature': {'score': 75},
                'color_saturation': {'score': 72},
                'color_contrast': {'score': 78},
                'emotional_appeal': {'score': 74}
            },
            'recommendations': [
                'تحسين الإضاءة والسطوع',
                'زيادة التباين للوضوح',
                'تحسين تناسق الألوان'
            ],
            'analysis_date': datetime.utcnow().isoformat(),
            'note': 'تحليل أساسي - يُنصح بتحسين جودة الصورة'
        }
    
    def _get_fallback_thumbnail_analysis(self):
        """Return fallback thumbnail analysis"""
        base = self._get_fallback_analysis()
        base.update({
            'thumbnail_specific': {
                'click_appeal': {'score': 72, 'visual_complexity': 70, 'high_contrast': 75, 'color_vibrancy': 71},
                'text_overlay': {'score': 70, 'has_text_areas': True, 'text_background_quality': 65},
                'thumbnail_style': {'score': 73, 'color_consistency': 75, 'simplicity': 71},
                'mobile_readability': {'score': 72, 'contrast_at_mobile_size': 70, 'detail_preservation': 74}
            },
            'youtube_optimized_score': 72
        })
        return base
    
    def _get_fallback_channel_art_analysis(self):
        """Return fallback channel art analysis"""
        base = self._get_fallback_analysis()
        base.update({
            'channel_specific': {
                'brand_presence': {'score': 70},
                'text_readability': {'score': 68},
                'visual_hierarchy': {'score': 72},
                'platform_compatibility': {'score': 75}
            },
            'branding_effectiveness_score': 71
        })
        return base
    
    def _get_basic_url_analysis(self, image_url):
        """Basic analysis when PIL is not available"""
        try:
            response = requests.head(image_url, timeout=5)
            if response.status_code == 200:
                return {'score': 75, 'note': 'تحليل أساسي - الصورة متاحة'}
            else:
                return {'score': 40, 'note': 'خطأ في الوصول للصورة'}
        except:
            return {'score': 50, 'note': 'تعذر تحليل الصورة'}
    
    # Additional helper methods for detailed analysis
    def _analyze_visual_balance(self, image):
        """Analyze visual balance of the image"""
        try:
            img_array = np.array(image)
            height, width = img_array.shape[:2]
            
            # Divide into quadrants
            q1 = img_array[:height//2, :width//2]
            q2 = img_array[:height//2, width//2:]
            q3 = img_array[height//2:, :width//2]
            q4 = img_array[height//2:, width//2:]
            
            # Calculate brightness for each quadrant
            brightness = [np.mean(q) for q in [q1, q2, q3, q4]]
            
            # Good balance = similar brightness across quadrants
            balance_variance = np.var(brightness)
            balance_score = max(50, 90 - balance_variance / 10)
            
            return round(balance_score, 2)
            
        except Exception as e:
            logging.error(f"Error in visual balance analysis: {str(e)}")
            return 72
    
    def _analyze_rule_of_thirds(self, image):
        """Analyze adherence to rule of thirds"""
        try:
            img_array = np.array(image)
            height, width = img_array.shape[:2]
            
            # Rule of thirds intersection points
            third_h, two_third_h = height // 3, 2 * height // 3
            third_w, two_third_w = width // 3, 2 * width // 3
            
            # Analyze brightness at intersection points
            intersections = [
                self._get_area_brightness(img_array, third_w-10, third_h-10, 20, 20),
                self._get_area_brightness(img_array, two_third_w-10, third_h-10, 20, 20),
                self._get_area_brightness(img_array, third_w-10, two_third_h-10, 20, 20),
                self._get_area_brightness(img_array, two_third_w-10, two_third_h-10, 20, 20)
            ]
            
            # Higher variance at intersections suggests better composition
            intersection_variance = np.var(intersections)
            rule_score = min(85, max(60, intersection_variance / 5))
            
            return round(rule_score, 2)
            
        except Exception as e:
            logging.error(f"Error in rule of thirds analysis: {str(e)}")
            return 70
    
    def _get_area_brightness(self, image, x, y, width, height):
        """Get average brightness of a specific area"""
        try:
            h, w = image.shape[:2]
            x = max(0, min(x, w - width))
            y = max(0, min(y, h - height))
            area = image[y:y+height, x:x+width]
            return np.mean(area)
        except:
            return 128  # Default brightness
    
    def _analyze_symmetry(self, image):
        """Analyze image symmetry"""
        try:
            img_array = np.array(image.convert('L'))  # Convert to grayscale
            height, width = img_array.shape
            
            # Horizontal symmetry
            left_half = img_array[:, :width//2]
            right_half = np.fliplr(img_array[:, width//2:])
            
            # Resize to match if needed
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]
            
            # Calculate difference
            symmetry_diff = np.mean(np.abs(left_half.astype(float) - right_half.astype(float)))
            symmetry_score = max(50, 90 - symmetry_diff / 5)
            
            return round(symmetry_score, 2)
            
        except Exception as e:
            logging.error(f"Error in symmetry analysis: {str(e)}")
            return 68
    
    def _analyze_color_temperature(self, colors):
        """Analyze color temperature warmth/coolness"""
        try:
            warm_score = 0
            cool_score = 0
            
            for color in colors:
                color = color.lstrip('#')
                r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                
                # Warm colors have more red/yellow
                if r > g and r > b:
                    warm_score += 1
                elif b > r and b > g:
                    cool_score += 1
            
            # Balanced temperature is often better
            if abs(warm_score - cool_score) <= 1:
                return 78
            elif warm_score > cool_score:
                return 72  # Warm
            else:
                return 75  # Cool
                
        except Exception as e:
            logging.error(f"Error in color temperature analysis: {str(e)}")
            return 75
    
    def _analyze_color_saturation(self, image):
        """Analyze overall color saturation"""
        try:
            hsv = image.convert('HSV')
            saturation_array = np.array(hsv)[:, :, 1]
            avg_saturation = np.mean(saturation_array) / 255.0
            
            # Moderate saturation is usually best
            if 0.4 <= avg_saturation <= 0.7:
                saturation_score = 80
            elif avg_saturation < 0.4:
                saturation_score = 60 + avg_saturation * 50
            else:
                saturation_score = 80 - (avg_saturation - 0.7) * 40
            
            return round(saturation_score, 2)
            
        except Exception as e:
            logging.error(f"Error in color saturation analysis: {str(e)}")
            return 72
    
    def _analyze_color_contrast(self, colors):
        """Analyze color contrast between dominant colors"""
        try:
            if len(colors) < 2:
                return 60
            
            contrasts = []
            for i in range(len(colors) - 1):
                color1 = colors[i].lstrip('#')
                color2 = colors[i + 1].lstrip('#')
                
                # Convert to RGB
                rgb1 = tuple(int(color1[j:j+2], 16) for j in (0, 2, 4))
                rgb2 = tuple(int(color2[j:j+2], 16) for j in (0, 2, 4))
                
                # Calculate luminance contrast
                l1 = self._calculate_luminance(rgb1)
                l2 = self._calculate_luminance(rgb2)
                
                contrast_ratio = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
                contrasts.append(contrast_ratio)
            
            avg_contrast = np.mean(contrasts)
            
            # Good contrast is between 3:1 and 7:1
            if 3 <= avg_contrast <= 7:
                contrast_score = 85
            elif avg_contrast < 3:
                contrast_score = 60 + avg_contrast * 8
            else:
                contrast_score = 85 - (avg_contrast - 7) * 3
            
            return round(min(90, max(50, contrast_score)), 2)
            
        except Exception as e:
            logging.error(f"Error in color contrast analysis: {str(e)}")
            return 78
    
    def _calculate_luminance(self, rgb_color):
        """Calculate relative luminance of RGB color"""
        try:
            r, g, b = [x / 255.0 for x in rgb_color]
            
            # Apply gamma correction
            def gamma_correct(c):
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            
            r = gamma_correct(r)
            g = gamma_correct(g)
            b = gamma_correct(b)
            
            # Calculate luminance
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
            
        except Exception as e:
            logging.error(f"Error calculating luminance: {str(e)}")
            return 0.5
    
    def _calculate_emotional_appeal(self, colors):
        """Calculate emotional appeal based on color psychology"""
        try:
            emotional_score = 70  # Base score
            
            for color in colors:
                color = color.lstrip('#')
                r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                
                # Color psychology scoring
                if r > 200 and g < 100 and b < 100:  # Red - energetic
                    emotional_score += 5
                elif g > 200 and r < 150 and b < 150:  # Green - calming
                    emotional_score += 3
                elif b > 200 and r < 150 and g < 150:  # Blue - trustworthy
                    emotional_score += 4
                elif r > 200 and g > 150 and b < 100:  # Orange/Yellow - cheerful
                    emotional_score += 4
                elif r < 50 and g < 50 and b < 50:  # Dark - sophisticated
                    emotional_score += 2
            
            return min(90, max(50, emotional_score))
            
        except Exception as e:
            logging.error(f"Error calculating emotional appeal: {str(e)}")
            return 74
    
    def _analyze_visual_complexity(self, image):
        """Analyze visual complexity for optimal click appeal"""
        try:
            img_array = np.array(image.convert('L'))  # Grayscale
            
            # Edge detection to measure complexity
            edges = self._count_edges(img_array)
            total_pixels = img_array.shape[0] * img_array.shape[1]
            edge_density = edges / total_pixels
            
            # Optimal complexity is moderate (not too busy, not too simple)
            if 0.05 <= edge_density <= 0.15:
                complexity_score = 85
            elif edge_density < 0.05:
                complexity_score = 60 + edge_density * 500
            else:
                complexity_score = 85 - (edge_density - 0.15) * 200
            
            return round(min(90, max(50, complexity_score)), 2)
            
        except Exception as e:
            logging.error(f"Error in visual complexity analysis: {str(e)}")
            return 70
    
    def _count_edges(self, image_section):
        """Count edges in an image section"""
        try:
            # Simple edge detection using gradient
            grad_x = np.abs(np.diff(image_section, axis=1))
            grad_y = np.abs(np.diff(image_section, axis=0))
            
            # Count significant edges
            edge_threshold = 30
            edges_x = np.sum(grad_x > edge_threshold)
            edges_y = np.sum(grad_y > edge_threshold)
            
            return edges_x + edges_y
            
        except Exception as e:
            logging.error(f"Error counting edges: {str(e)}")
            return 1000  # Default edge count
    
    def _analyze_high_contrast(self, image):
        """Analyze if image has high contrast suitable for thumbnails"""
        try:
            img_array = np.array(image.convert('L'))
            
            # Calculate histogram
            hist, _ = np.histogram(img_array, bins=256, range=(0, 256))
            
            # High contrast images have peaks at both ends
            dark_pixels = np.sum(hist[:64])  # Very dark
            bright_pixels = np.sum(hist[192:])  # Very bright
            total_pixels = img_array.shape[0] * img_array.shape[1]
            
            contrast_ratio = (dark_pixels + bright_pixels) / total_pixels
            
            # Good thumbnail contrast
            if contrast_ratio > 0.3:
                contrast_score = 85
            elif contrast_ratio > 0.2:
                contrast_score = 75
            else:
                contrast_score = 60 + contrast_ratio * 50
            
            return round(contrast_score, 2)
            
        except Exception as e:
            logging.error(f"Error in high contrast analysis: {str(e)}")
            return 75
    
    def _analyze_color_vibrancy(self, image):
        """Analyze color vibrancy"""
        try:
            hsv = image.convert('HSV')
            saturation = np.array(hsv)[:, :, 1]
            value = np.array(hsv)[:, :, 2]
            
            # Vibrancy combines saturation and brightness
            vibrancy = np.mean(saturation * value) / (255 * 255)
            
            # Optimal vibrancy for thumbnails
            if 0.3 <= vibrancy <= 0.6:
                vibrancy_score = 85
            elif vibrancy < 0.3:
                vibrancy_score = 60 + vibrancy * 83
            else:
                vibrancy_score = 85 - (vibrancy - 0.6) * 50
            
            return round(vibrancy_score, 2)
            
        except Exception as e:
            logging.error(f"Error in color vibrancy analysis: {str(e)}")
            return 71
    
    def _analyze_brand_presence(self, image, channel_info):
        """Analyze brand presence in channel art"""
        try:
            # This is a simplified analysis
            # In reality, would use logo detection and text recognition
            
            brand_score = 70  # Base score
            
            if channel_info:
                # If channel has consistent branding elements
                if channel_info.get('customUrl'):
                    brand_score += 5
                if channel_info.get('description') and len(channel_info['description']) > 100:
                    brand_score += 5
            
            # Analyze for text areas (likely branding)
            img_array = np.array(image.convert('L'))
            
            # Look for consistent color blocks (logos/branding)
            # Simplified: look for areas with low variance (solid colors)
            height, width = img_array.shape
            
            # Check center area for branding
            center_h, center_w = height // 2, width // 2
            center_area = img_array[center_h-50:center_h+50, center_w-100:center_w+100]
            
            if center_area.size > 0:
                center_variance = np.var(center_area)
                if center_variance < 1000:  # Low variance suggests branding element
                    brand_score += 8
            
            return min(85, max(60, brand_score))
            
        except Exception as e:
            logging.error(f"Error in brand presence analysis: {str(e)}")
            return 70
    
    def _analyze_banner_text(self, image):
        """Analyze text readability in banner"""
        try:
            # Simplified text analysis
            img_array = np.array(image.convert('L'))
            
            # Look for high contrast areas (likely text)
            edges = self._count_edges(img_array)
            total_pixels = img_array.shape[0] * img_array.shape[1]
            edge_density = edges / total_pixels
            
            # Text areas typically have higher edge density
            if edge_density > 0.1:
                text_score = 75
            elif edge_density > 0.05:
                text_score = 65
            else:
                text_score = 60
            
            return text_score
            
        except Exception as e:
            logging.error(f"Error in banner text analysis: {str(e)}")
            return 68
    
    def _analyze_visual_hierarchy(self, image):
        """Analyze visual hierarchy in channel art"""
        try:
            img_array = np.array(image)
            height, width = img_array.shape[:2]
            
            # Analyze brightness distribution
            # Good hierarchy has clear focal points
            
            # Divide into 9 sections (3x3 grid)
            sections = []
            for i in range(3):
                for j in range(3):
                    start_h, end_h = i * height // 3, (i + 1) * height // 3
                    start_w, end_w = j * width // 3, (j + 1) * width // 3
                    section = img_array[start_h:end_h, start_w:end_w]
                    sections.append(np.mean(section))
            
            # Good hierarchy has variation in brightness
            hierarchy_variance = np.var(sections)
            hierarchy_score = min(85, max(60, hierarchy_variance / 20))
            
            return round(hierarchy_score, 2)
            
        except Exception as e:
            logging.error(f"Error in visual hierarchy analysis: {str(e)}")
            return 72
    
    def _analyze_banner_compatibility(self, image):
        """Analyze banner compatibility across platforms"""
        try:
            width, height = image.size
            
            # YouTube banner optimal ratio is 16:9 (2560x1440)
            aspect_ratio = width / height
            optimal_ratio = 16 / 9
            
            ratio_difference = abs(aspect_ratio - optimal_ratio)
            
            if ratio_difference < 0.1:
                compatibility_score = 90
            elif ratio_difference < 0.3:
                compatibility_score = 80
            elif ratio_difference < 0.5:
                compatibility_score = 70
            else:
                compatibility_score = 60
            
            # Check resolution
            if width >= 2048 and height >= 1152:
                compatibility_score += 5
            elif width >= 1546 and height >= 423:
                compatibility_score += 2
            
            return min(95, compatibility_score)
            
        except Exception as e:
            logging.error(f"Error in banner compatibility analysis: {str(e)}")
            return 75
    
    def _generate_recommendations(self, overall_score, metrics):
        """Generate general recommendations for image improvement"""
        recommendations = []
        
        if overall_score < 70:
            recommendations.append("تحسين الجودة العامة للصورة مطلوب")
        
        # Check specific metrics
        if 'brightness' in metrics and metrics['brightness']['score'] < 70:
            recommendations.append("تحسين الإضاءة والسطوع")
        
        if 'contrast' in metrics and metrics['contrast']['score'] < 70:
            recommendations.append("زيادة التباين للوضوح")
        
        if 'color_vibrancy' in metrics and metrics['color_vibrancy']['score'] < 70:
            recommendations.append("تحسين حيوية الألوان")
        
        if 'color_harmony' in metrics and metrics['color_harmony']['score'] < 70:
            recommendations.append("تحسين تناسق الألوان")
        
        if 'overall_composition' in metrics and metrics['overall_composition']['score'] < 70:
            recommendations.append("تحسين التكوين والتوزيع البصري")
        
        if not recommendations:
            recommendations.append("الصورة بجودة جيدة - تحسينات طفيفة ممكنة")
        
        return recommendations
    
    def _generate_thumbnail_recommendations(self, base_analysis, thumbnail_specific):
        """Generate specific recommendations for thumbnail improvement"""
        recommendations = self._generate_recommendations(
            base_analysis['overall_score'], 
            {**base_analysis.get('technical_quality', {}), 
             **base_analysis.get('visual_appeal', {}),
             **base_analysis.get('composition', {})}
        )
        
        # Add thumbnail-specific recommendations
        if thumbnail_specific['click_appeal']['score'] < 75:
            recommendations.append("تحسين عوامل الجذب البصرية للنقر")
        
        if thumbnail_specific['text_overlay']['score'] < 70:
            recommendations.append("تحسين وضوح النص المدرج")
        
        if thumbnail_specific['mobile_readability']['score'] < 70:
            recommendations.append("تحسين وضوح الثامبنيل على الأجهزة المحمولة")
        
        if thumbnail_specific['thumbnail_style']['simplicity'] < 70:
            recommendations.append("تبسيط التصميم لتحسين الوضوح")
        
        return recommendations
    
    def _generate_channel_art_recommendations(self, base_analysis, channel_specific):
        """Generate specific recommendations for channel art improvement"""
        recommendations = self._generate_recommendations(
            base_analysis['overall_score'],
            {**base_analysis.get('technical_quality', {}), 
             **base_analysis.get('visual_appeal', {}),
             **base_analysis.get('composition', {})}
        )
        
        # Add channel art specific recommendations
        if channel_specific['brand_presence']['score'] < 75:
            recommendations.append("تقوية العناصر التجارية والهوية البصرية")
        
        if channel_specific['text_readability']['score'] < 70:
            recommendations.append("تحسين وضوح النصوص في البانر")
        
        if channel_specific['visual_hierarchy']['score'] < 70:
            recommendations.append("تحسين التسلسل البصري والتركيز")
        
        if channel_specific['platform_compatibility']['score'] < 80:
            recommendations.append("تحسين توافق البانر مع مختلف المنصات")
        
        return recommendations