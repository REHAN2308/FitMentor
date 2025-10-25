"""
FitMentor API - Flask REST API with AI-Powered Fitness Plan Generation
Uses OpenRouter API with GPT-4o Mini model
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from fitmentor_ai import FitMentorAI
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration


@app.route('/')
def home():
    """Serve the main HTML interface"""
    return send_from_directory('.', 'index.html')


@app.route('/api')
def api_info():
    """API information endpoint"""
    api_key_status = "✅ Configured" if os.getenv('OPENROUTER_API_KEY') else "❌ Missing"
    
    return jsonify({
        'message': 'Welcome to FitMentor AI - Powered by GPT-4o Mini',
        'version': '2.0.0',
        'model': 'openai/gpt-4o-mini',
        'api_key_status': api_key_status,
        'endpoints': {
            '/api/generate-plan': 'POST - Generate AI-powered fitness plan',
            '/api/health': 'GET - Check API health',
            '/api/calculate-bmi': 'POST - Calculate BMI',
            '/api/calculate-calories': 'POST - Calculate daily caloric needs'
        },
        'note': 'Set OPENROUTER_API_KEY in .env file to enable AI features'
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    api_key_status = "configured" if os.getenv('OPENROUTER_API_KEY') else "missing"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'FitMentor AI API',
        'model': 'openai/gpt-4o-mini',
        'api_key_status': api_key_status
    })


@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    """
    Generate AI-powered personalized weekly fitness plan
    
    Expected JSON payload:
    {
        "weight": 70,
        "height": 175,
        "age": 25,
        "gender": "male",
        "activity_level": "moderate",
        "fitness_goal": "muscle gain",
        "dietary_preferences": "balanced",
        "health_restrictions": "none"
    }
    """
    try:
        # Get user data from request
        user_data = request.get_json()
        
        # Validate required fields
        required_fields = ['weight', 'height', 'age', 'gender', 'activity_level', 
                          'fitness_goal', 'dietary_preferences']
        
        missing_fields = [field for field in required_fields if field not in user_data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Validate data types and ranges
        try:
            weight = float(user_data['weight'])
            height = float(user_data['height'])
            age = int(user_data['age'])
            
            if weight <= 0 or weight > 300:
                return jsonify({'error': 'Weight must be between 1 and 300 kg'}), 400
            if height <= 0 or height > 250:
                return jsonify({'error': 'Height must be between 1 and 250 cm'}), 400
            if age <= 0 or age > 120:
                return jsonify({'error': 'Age must be between 1 and 120 years'}), 400
                
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid data types for weight, height, or age'}), 400
        
        # Validate enum fields
        valid_genders = ['male', 'female']
        valid_activity_levels = ['sedentary', 'light', 'moderate', 'active', 'very_active']
        valid_goals = ['weight loss', 'muscle gain', 'maintenance', 'endurance']
        valid_diets = ['vegetarian', 'vegan', 'keto', 'balanced']
        
        if user_data['gender'].lower() not in valid_genders:
            return jsonify({'error': f'Gender must be one of: {valid_genders}'}), 400
        if user_data['activity_level'].lower() not in valid_activity_levels:
            return jsonify({'error': f'Activity level must be one of: {valid_activity_levels}'}), 400
        if user_data['fitness_goal'].lower() not in valid_goals:
            return jsonify({'error': f'Fitness goal must be one of: {valid_goals}'}), 400
        if user_data['dietary_preferences'].lower() not in valid_diets:
            return jsonify({'error': f'Dietary preference must be one of: {valid_diets}'}), 400
        
        # Check for API key
        if not os.getenv('OPENROUTER_API_KEY'):
            return jsonify({
                'error': 'OpenRouter API key not configured',
                'message': 'Please set OPENROUTER_API_KEY in .env file',
                'note': 'Fallback mode will be used but with limited AI features'
            }), 503
        
        # Generate AI-powered fitness plan
        print(f"\n{'='*80}")
        print(f"Generating plan for: {user_data['gender']}, {age}y, {weight}kg, {height}cm")
        print(f"Goal: {user_data['fitness_goal']}, Diet: {user_data['dietary_preferences']}")
        print(f"{'='*80}\n")
        
        trainer = FitMentorAI(user_data)
        plan = trainer.generate_weekly_plan()
        
        # Return the plan directly (UI expects plan data at root level)
        response_data = plan.copy()
        response_data['_metadata'] = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'model': 'deepseek/deepseek-r1:free'
        }
        
        return jsonify(response_data), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Configuration error',
            'message': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/api/calculate-bmi', methods=['POST'])
def calculate_bmi():
    """
    Calculate BMI
    
    Expected JSON payload:
    {
        "weight": 70,
        "height": 175
    }
    """
    try:
        data = request.get_json()
        
        if 'weight' not in data or 'height' not in data:
            return jsonify({'error': 'Weight and height are required'}), 400
        
        weight = float(data['weight'])
        height = float(data['height'])
        
        height_m = height / 100
        bmi = round(weight / (height_m ** 2), 2)
        
        # Determine BMI category
        if bmi < 18.5:
            category = 'Underweight'
            recommendation = 'Consider muscle gain program'
        elif 18.5 <= bmi < 25:
            category = 'Normal weight'
            recommendation = 'Maintain your healthy weight'
        elif 25 <= bmi < 30:
            category = 'Overweight'
            recommendation = 'Consider weight loss program'
        else:
            category = 'Obese'
            recommendation = 'Consult with healthcare provider and consider weight loss program'
        
        return jsonify({
            'bmi': bmi,
            'category': category,
            'recommendation': recommendation
        }), 200
        
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid weight or height values'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/calculate-calories', methods=['POST'])
def calculate_calories():
    """
    Calculate daily caloric needs
    
    Expected JSON payload:
    {
        "weight": 70,
        "height": 175,
        "age": 25,
        "gender": "male",
        "activity_level": "moderate",
        "fitness_goal": "muscle gain"
    }
    """
    try:
        data = request.get_json()
        
        required = ['weight', 'height', 'age', 'gender', 'activity_level', 'fitness_goal']
        if not all(field in data for field in required):
            return jsonify({'error': 'All fields are required'}), 400
        
        weight = float(data['weight'])
        height = float(data['height'])
        age = int(data['age'])
        gender = data['gender'].lower()
        activity_level = data['activity_level'].lower()
        fitness_goal = data['fitness_goal'].lower()
        
        # Calculate BMR
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Activity multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'moderate': 1.55,
            'active': 1.725,
            'very active': 1.9
        }
        
        tdee = bmr * activity_multipliers.get(activity_level, 1.55)
        
        # Adjust based on goal
        if fitness_goal == 'weight loss':
            target_calories = int(tdee - 500)
            adjustment = -500
        elif fitness_goal == 'muscle gain':
            target_calories = int(tdee + 300)
            adjustment = +300
        else:
            target_calories = int(tdee)
            adjustment = 0
        
        # Calculate macros
        if fitness_goal == 'muscle gain':
            protein = int((target_calories * 0.30) / 4)
            carbs = int((target_calories * 0.45) / 4)
            fats = int((target_calories * 0.25) / 9)
        elif fitness_goal == 'weight loss':
            protein = int((target_calories * 0.35) / 4)
            carbs = int((target_calories * 0.35) / 4)
            fats = int((target_calories * 0.30) / 9)
        else:
            protein = int((target_calories * 0.25) / 4)
            carbs = int((target_calories * 0.45) / 4)
            fats = int((target_calories * 0.30) / 9)
        
        return jsonify({
            'bmr': int(bmr),
            'tdee': int(tdee),
            'target_calories': target_calories,
            'adjustment': adjustment,
            'macros': {
                'protein_g': protein,
                'carbs_g': carbs,
                'fats_g': fats
            },
            'explanation': {
                'bmr': 'Basal Metabolic Rate - calories burned at rest',
                'tdee': 'Total Daily Energy Expenditure',
                'target': f'Adjusted for {fitness_goal} goal'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║     FITMENTOR AI - Powered by GPT-4o Mini (OpenRouter)        ║
    ╠════════════════════════════════════════════════════════════════╣
    ║  Running on: http://localhost:5000                             ║
    ║  Model: openai/gpt-4o-mini (Fast & Reliable)                   ║
    ╠════════════════════════════════════════════════════════════════╣
    """)
    
    # Check for API key
    if os.getenv('OPENROUTER_API_KEY'):
        print("║  ✅ API Key: Configured                                      ║")
    else:
        print("║  ⚠️  API Key: MISSING - Please set in .env file              ║")
        print("║     OPENROUTER_API_KEY=your_key_here                         ║")
    
    print("""╠════════════════════════════════════════════════════════════════╣
    ║  Endpoints:                                                     ║
    ║    GET  /                     - API information                ║
    ║    GET  /api/health           - Health check                   ║
    ║    POST /api/generate-plan    - Generate AI fitness plan       ║
    ║    POST /api/calculate-bmi    - Calculate BMI                  ║
    ║    POST /api/calculate-calories - Calculate caloric needs      ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

# Export for Vercel serverless
# This allows Vercel to use the Flask app as a serverless function
if __name__ != '__main__':
    # Vercel will import this module, so we expose 'app'
    application = app
