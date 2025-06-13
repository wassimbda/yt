from app import db
from datetime import datetime
import json

class ChannelAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.String(100), nullable=False)
    channel_name = db.Column(db.String(200), nullable=False)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Channel basic info
    subscriber_count = db.Column(db.Integer)
    video_count = db.Column(db.Integer)
    view_count = db.Column(db.BigInteger)
    description = db.Column(db.Text)
    
    # AI Analysis results
    detected_niche = db.Column(db.String(100))
    channel_art_score = db.Column(db.Float)
    thumbnail_score = db.Column(db.Float)
    title_optimization_score = db.Column(db.Float)
    overall_rating = db.Column(db.Float)
    
    # Analysis details (stored as JSON string)
    analysis_details = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    
    def __repr__(self):
        return f'<ChannelAnalysis {self.channel_name}>'

class TitleAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # AI Analysis scores
    attractiveness_score = db.Column(db.Float)  # 1-100
    success_probability = db.Column(db.Float)   # 0-1
    emotional_impact = db.Column(db.Float)      # 1-10
    keyword_strength = db.Column(db.Float)      # 1-10
    
    # Analysis details
    strengths = db.Column(db.Text)  # JSON array
    weaknesses = db.Column(db.Text) # JSON array
    suggestions = db.Column(db.Text) # JSON array
    category = db.Column(db.String(100))
    
    # Timing analysis
    best_posting_time = db.Column(db.String(100))
    target_audience = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<TitleAnalysis {self.title[:50]}...>'

class VideoIdea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('channel_analysis.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    niche = db.Column(db.String(100), nullable=False)
    success_score = db.Column(db.Float)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    analysis = db.relationship('ChannelAnalysis', backref=db.backref('video_ideas', lazy=True))
    
    def __repr__(self):
        return f'<VideoIdea {self.title}>'

class OptimalTiming(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.String(100), nullable=False)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timing recommendations
    best_days = db.Column(db.Text)  # JSON array of best days
    best_hours = db.Column(db.Text) # JSON array of best hours
    timezone = db.Column(db.String(50))
    audience_data = db.Column(db.Text) # JSON with audience insights
    
    # Performance metrics
    confidence_score = db.Column(db.Float)
    data_quality = db.Column(db.String(20))  # 'high', 'medium', 'low'
    
    def __repr__(self):
        return f'<OptimalTiming {self.channel_id}>'
