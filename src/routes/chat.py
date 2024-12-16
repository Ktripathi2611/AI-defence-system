from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from src.models.chat import Chat
from src.models import db
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@login_required
def chat_page():
    return render_template('chat.html')

@chat_bp.route('/api/chat/messages', methods=['GET'])
@login_required
def get_messages():
    messages = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.timestamp.desc()).limit(50).all()
    return jsonify([message.to_dict() for message in messages])

@chat_bp.route('/api/chat/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    message = data.get('message')
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
        
    # Save user message
    chat = Chat(
        user_id=current_user.id,
        message=message,
        is_ai_response=False
    )
    db.session.add(chat)
    
    # Generate AI response
    ai_response = "This is a sample AI response. Replace with actual AI integration."
    ai_chat = Chat(
        user_id=current_user.id,
        message=ai_response,
        is_ai_response=True
    )
    db.session.add(ai_chat)
    
    db.session.commit()
    
    return jsonify({
        'user_message': chat.to_dict(),
        'ai_response': ai_chat.to_dict()
    })
