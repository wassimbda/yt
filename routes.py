from flask import render_template, request, flash, redirect, url_for, jsonify
from app import app, db
from models import ChannelAnalysis, VideoIdea, TitleAnalysis, OptimalTiming
from youtube_service import YouTubeService
from ai_analyzer import AIAnalyzer
from title_analyzer import TitleAnalyzer
from success_predictor import SuccessPredictor
from timing_optimizer import TimingOptimizer
from niche_detector import NicheDetector
import json
import logging
import os

# Initialize services
youtube_service = YouTubeService()
ai_analyzer = AIAnalyzer()
title_analyzer = TitleAnalyzer()
success_predictor = SuccessPredictor()
timing_optimizer = TimingOptimizer()
niche_detector = NicheDetector()

@app.route('/')
def index():
    """Main page with channel analysis and title analysis options"""
    # Check API status
    openai_available = bool(os.environ.get('OPENAI_API_KEY'))
    youtube_available = bool(os.environ.get('YOUTUBE_API_KEY'))
    
    # Check if OpenAI is working by looking for quota errors
    openai_limited = False
    if hasattr(ai_analyzer, 'last_error') and ai_analyzer.last_error:
        openai_limited = 'insufficient_quota' in str(ai_analyzer.last_error) or '429' in str(ai_analyzer.last_error)
    
    api_status = {
        'openai_available': openai_available,
        'openai_limited': openai_limited,
        'youtube_available': youtube_available,
        'analysis_mode': 'متقدم مع CLIP' if not openai_limited else 'محلي متطور'
    }
    return render_template('index.html', api_status=api_status)

@app.route('/analyze_channel', methods=['POST'])
def analyze_channel():
    """Comprehensive channel analysis"""
    channel_input = request.form.get('channel_input', '').strip()
    
    if not channel_input:
        flash('يرجى إدخال رابط أو معرف قناة يوتيوب', 'error')
        return redirect(url_for('index'))
    
    try:
        # Extract channel ID
        channel_id = youtube_service.extract_channel_id(channel_input)
        if not channel_id:
            flash('رابط أو معرف قناة يوتيوب غير صالح', 'error')
            return redirect(url_for('index'))
        
        # Get channel information
        channel_info = youtube_service.get_channel_info(channel_id)
        if not channel_info:
            flash('القناة غير موجودة أو حدث خطأ في الواجهة البرمجية', 'error')
            return redirect(url_for('index'))
        
        # Get recent videos
        videos = youtube_service.get_channel_videos(channel_id, max_results=20)
        
        # Perform comprehensive AI analysis
        analysis_result = ai_analyzer.analyze_channel(channel_info, videos)
        
        # Detect niche
        niche_analysis = niche_detector.detect_niche(channel_info, videos)
        
        # Analyze optimal timing
        timing_analysis = timing_optimizer.analyze_optimal_timing(channel_info, videos)
        
        # Save analysis to database
        analysis = ChannelAnalysis(
            channel_id=channel_id,
            channel_name=channel_info['title'],
            subscriber_count=channel_info.get('subscriber_count', 0),
            video_count=channel_info.get('video_count', 0),
            view_count=channel_info.get('view_count', 0),
            description=channel_info.get('description', ''),
            detected_niche=niche_analysis.get('primary_niche', ''),
            channel_art_score=analysis_result.get('channel_art_score', 0),
            thumbnail_score=analysis_result.get('thumbnail_score', 0),
            title_optimization_score=analysis_result.get('title_optimization_score', 0),
            overall_rating=analysis_result.get('overall_rating', 0),
            analysis_details=json.dumps({
                'niche_analysis': niche_analysis,
                'timing_analysis': timing_analysis,
                **analysis_result.get('details', {})
            }),
            recommendations=json.dumps(analysis_result.get('recommendations', []))
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Save timing analysis
        timing_record = OptimalTiming(
            channel_id=channel_id,
            best_days=json.dumps(timing_analysis.get('best_days', [])),
            best_hours=json.dumps(timing_analysis.get('best_hours', [])),
            timezone=timing_analysis.get('timezone', 'UTC'),
            audience_data=json.dumps(timing_analysis.get('audience_data', {})),
            confidence_score=timing_analysis.get('confidence_score', 0),
            data_quality=timing_analysis.get('data_quality', 'low')
        )
        
        db.session.add(timing_record)
        db.session.commit()
        
        return render_template('analysis.html', 
                              channel_info=channel_info,
                              analysis=analysis,
                              analysis_result=analysis_result,
                              niche_analysis=niche_analysis,
                              timing_analysis=timing_analysis,
                              videos=videos[:10])
        
    except Exception as e:
        logging.error(f"Error analyzing channel: {str(e)}")
        flash(f'خطأ في تحليل القناة: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/analyze_title', methods=['GET', 'POST'])
def analyze_title():
    """Advanced title analysis with AI"""
    if request.method == 'GET':
        return render_template('title_analysis.html')
    
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'عام')
    target_audience = request.form.get('target_audience', '')
    
    if not title:
        flash('يرجى إدخال عنوان للتحليل', 'error')
        return render_template('title_analysis.html')
    
    try:
        # Perform comprehensive title analysis
        title_analysis_result = title_analyzer.analyze_title(title, category, target_audience)
        
        # Predict success probability
        success_analysis = success_predictor.predict_success(title, category)
        
        # Get optimal timing recommendations
        timing_recommendations = timing_optimizer.get_timing_recommendations(category, target_audience)
        
        # Save analysis to database
        analysis = TitleAnalysis(
            title=title,
            attractiveness_score=title_analysis_result.get('attractiveness_score', 0),
            success_probability=success_analysis.get('success_probability', 0),
            emotional_impact=title_analysis_result.get('emotional_impact', 0),
            keyword_strength=title_analysis_result.get('keyword_strength', 0),
            strengths=json.dumps(title_analysis_result.get('strengths', [])),
            weaknesses=json.dumps(title_analysis_result.get('weaknesses', [])),
            suggestions=json.dumps(title_analysis_result.get('suggestions', [])),
            category=category,
            best_posting_time=json.dumps(timing_recommendations),
            target_audience=target_audience
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        return render_template('title_analysis.html',
                              title=title,
                              analysis=analysis,
                              title_analysis=title_analysis_result,
                              success_analysis=success_analysis,
                              timing_recommendations=timing_recommendations,
                              show_results=True)
        
    except Exception as e:
        logging.error(f"Error analyzing title: {str(e)}")
        flash(f'خطأ في تحليل العنوان: {str(e)}', 'error')
        return render_template('title_analysis.html')

@app.route('/generate_ideas', methods=['POST'])
def generate_ideas():
    """Generate video ideas based on channel analysis"""
    analysis_id = request.form.get('analysis_id')
    niche = request.form.get('niche', '').strip()
    custom_niche = request.form.get('custom_niche', '').strip()
    
    if not analysis_id:
        flash('التحليل غير موجود', 'error')
        return redirect(url_for('index'))
    
    try:
        analysis = ChannelAnalysis.query.get_or_404(analysis_id)
        target_niche = custom_niche if custom_niche else niche
        
        if not target_niche:
            flash('يرجى اختيار أو إدخال مجال المحتوى', 'error')
            return redirect(url_for('index'))
        
        # Generate advanced video ideas
        ideas = ai_analyzer.generate_advanced_video_ideas(target_niche, analysis.channel_name, analysis)
        
        # Save ideas to database
        for idea in ideas:
            video_idea = VideoIdea(
                analysis_id=analysis.id,
                title=idea['title'],
                description=idea['description'],
                niche=target_niche,
                success_score=idea.get('success_score', 0)
            )
            db.session.add(video_idea)
        
        db.session.commit()
        
        # Return updated analysis page with ideas
        return render_template('analysis.html',
                              channel_info={
                                  'title': analysis.channel_name,
                                  'subscriber_count': analysis.subscriber_count,
                                  'video_count': analysis.video_count,
                                  'view_count': analysis.view_count,
                                  'description': analysis.description
                              },
                              analysis=analysis,
                              video_ideas=ideas,
                              selected_niche=target_niche,
                              show_ideas=True)
        
    except Exception as e:
        logging.error(f"Error generating ideas: {str(e)}")
        flash(f'خطأ في توليد أفكار الفيديوهات: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/quick_analysis', methods=['POST'])
def quick_analysis():
    """Quick API endpoint for title analysis"""
    data = request.get_json()
    title = data.get('title', '').strip()
    
    if not title:
        return jsonify({'error': 'عنوان مطلوب'}), 400
    
    try:
        # Quick analysis without saving to database
        result = title_analyzer.quick_analyze(title)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('index.html'), 500
