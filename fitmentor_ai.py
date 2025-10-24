"""
FitMentor - AI-Powered Personal Fitness Trainer using OpenRouter API
Generates personalized weekly fitness plans using DeepSeek AI model
"""

import json
import os
import requests
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()


class FitMentorAI:
    """AI-Powered Personal Fitness Trainer using OpenRouter API"""
    
    def __init__(self, user_data: Dict[str, Any], api_key: Optional[str] = None):
        self.weight = user_data.get('weight')
        self.height = user_data.get('height')
        self.age = user_data.get('age')
        self.gender = user_data.get('gender', 'male').lower()
        self.activity_level = user_data.get('activity_level', 'moderate').lower()
        self.fitness_goal = user_data.get('fitness_goal', 'maintenance').lower()
        self.dietary_preferences = user_data.get('dietary_preferences', 'balanced').lower()
        self.health_restrictions = user_data.get('health_restrictions', 'none').lower()
        
        # OpenRouter API configuration
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "openai/gpt-4o-mini"  # Faster and more reliable than DeepSeek
        
        # Calculate basic metrics
        self.bmi = self._calculate_bmi()
        self.daily_calories = self._calculate_calories()
        self.macros = self._calculate_macros()
        
    def _calculate_bmi(self) -> float:
        """Calculate Body Mass Index"""
        height_m = self.height / 100
        return round(self.weight / (height_m ** 2), 2)
    
    def _calculate_calories(self) -> int:
        """Calculate daily caloric needs using Mifflin-St Jeor Equation"""
        # BMR calculation
        if self.gender == 'male':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        
        # Activity multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9,
            'very active': 1.9  # Handle both formats
        }
        
        tdee = bmr * activity_multipliers.get(self.activity_level, 1.55)
        
        # Adjust based on fitness goal
        if self.fitness_goal == 'weight loss':
            return int(tdee - 500)
        elif self.fitness_goal == 'muscle gain':
            return int(tdee + 300)
        else:
            return int(tdee)
    
    def _calculate_macros(self) -> Dict[str, int]:
        """Calculate daily macronutrient requirements"""
        if self.fitness_goal == 'muscle gain':
            protein_ratio = 0.30
            carbs_ratio = 0.45
            fats_ratio = 0.25
        elif self.fitness_goal == 'weight loss':
            protein_ratio = 0.35
            carbs_ratio = 0.35
            fats_ratio = 0.30
        else:
            protein_ratio = 0.25
            carbs_ratio = 0.45
            fats_ratio = 0.30
        
        return {
            'protein': int((self.daily_calories * protein_ratio) / 4),
            'carbs': int((self.daily_calories * carbs_ratio) / 4),
            'fats': int((self.daily_calories * fats_ratio) / 9)
        }
    
    def _call_openrouter_api(self, prompt: str) -> str:
        """Call OpenRouter API with the given prompt"""
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Please set OPENROUTER_API_KEY in .env file or pass it to the constructor.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/fitmentor",
            "X-Title": "FitMentor AI"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,  # Limit response size for faster generation
            "temperature": 0.7   # Slightly lower for faster, more focused responses
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)  # Reduced timeout
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Clean the response (remove thinking tags, markdown, etc.)
            return self._clean_ai_response(content)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error calling OpenRouter API: {str(e)}")
    
    def _clean_ai_response(self, response: str) -> str:
        """Clean AI response to extract pure JSON"""
        response = response.strip()
        
        # Remove <think> tags (DeepSeek specific)
        if '<think>' in response:
            # Extract content after </think>
            parts = response.split('</think>')
            if len(parts) > 1:
                response = parts[-1].strip()
        
        # Remove markdown code blocks
        if response.startswith('```'):
            lines = response.split('\n')
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            response = '\n'.join(lines).strip()
        
        # Handle cases where ``` appears at the end
        if response.endswith('```'):
            response = response[:-3].strip()
        
        # Remove 'json' prefix if present
        if response.startswith('json'):
            response = response[4:].strip()
        
        return response
    
    def generate_weekly_plan(self) -> Dict[str, Any]:
        """Generate complete personalized weekly fitness plan using AI"""
        
        # Create user profile context
        user_context = f"""
User Profile:
- Weight: {self.weight}kg, Height: {self.height}cm, Age: {self.age}, Gender: {self.gender}
- BMI: {self.bmi}
- Activity Level: {self.activity_level}
- Fitness Goal: {self.fitness_goal}
- Dietary Preferences: {self.dietary_preferences}
- Health Restrictions: {self.health_restrictions}
- Daily Calories: {self.daily_calories} kcal
- Daily Macros: Protein {self.macros['protein']}g, Carbs {self.macros['carbs']}g, Fats {self.macros['fats']}g
"""
        
        print("🤖 Generating AI-powered fitness plan...")
        print("⏳ This may take 15-25 seconds...\n")
        
        # Generate workouts and meals in parallel for speed
        print("💪 Generating workout and meal plans in parallel...")
        
        workouts = None
        meals = None
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both tasks simultaneously
            workout_future = executor.submit(self._generate_workouts_ai, user_context)
            meal_future = executor.submit(self._generate_meals_ai, user_context)
            
            # Get results as they complete
            for future in as_completed([workout_future, meal_future]):
                if future == workout_future:
                    workouts = future.result()
                    print("✓ Workouts generated")
                elif future == meal_future:
                    meals = future.result()
                    print("✓ Meals generated")
        
        # Generate notifications (use fallback for speed - instant)
        print("🔔 Generating notifications...")
        notifications = self._get_fallback_notifications()
        
        # Generate challenge and tips (use fallback for speed - instant)
        print("🎯 Generating weekly challenge...")
        challenge = self._get_fallback_challenge()
        
        print("💡 Generating fitness tips...")
        tips = self._get_fallback_tips()
        
        print("✅ Plan generation complete!\n")
        
        return {
            'user_profile': {
                'bmi': self.bmi,
                'daily_calories': self.daily_calories,
                'macros': self.macros
            },
            'workouts': workouts,
            'meals': meals,
            'tracking_metrics': {
                'weight': f"{self.weight} kg",
                'body_fat': "Track weekly",
                'muscle_mass': "Track weekly",
                'water_intake': f"{2.5 if self.gender == 'male' else 2.0} liters/day",
                'sleep_hours': "7-8 hours/night",
                'steps': f"{8000 if self.activity_level in ['sedentary', 'moderate'] else 10000} steps/day"
            },
            'notifications': notifications,
            'weekly_challenge': challenge,
            'fitness_tips': tips
        }
    
    def _generate_workouts_ai(self, user_context: str) -> Dict[str, Any]:
        """Generate weekly workout plan using AI"""
        prompt = f"""{user_context}

Create 7-day workout plan. Return ONLY valid JSON:

{{
    "Monday": [{{"exercise_name": "name", "sets": 3, "reps": 12, "duration_minutes": 5, "intensity_level": "moderate", "equipment_required": "dumbbells"}}],
    "Tuesday": [...],
    "Wednesday": [...],
    "Thursday": [...],
    "Friday": [...],
    "Saturday": [...],
    "Sunday": [...]
}}

Rules:
- 4-5 exercises per day for goal: {self.fitness_goal}
- Include warm-up, main, cool-down
- Respect: {self.health_restrictions}
- Return ONLY JSON, no markdown."""

        try:
            response = self._call_openrouter_api(prompt)
            workouts = json.loads(response)
            
            # Convert to expected format (day: exercises list)
            formatted_workouts = []
            for day, exercises in workouts.items():
                formatted_workouts.append({
                    'day': day,
                    'exercises': exercises
                })
            return formatted_workouts
        except Exception as e:
            print(f"⚠️ Warning: AI workout generation failed ({str(e)}), using fallback")
            return self._get_fallback_workouts()
    
    def _generate_meals_ai(self, user_context: str) -> Dict[str, Any]:
        """Generate weekly meal plan using AI"""
        prompt = f"""{user_context}

Create 7-day meal plan. Return ONLY valid JSON with this structure:
{{"Monday": {{"breakfast": {{"meal": "name", "protein_g": 30, "carbs_g": 45, "fats_g": 15, "calories": 420}}, "lunch": {{}}, "dinner": {{}}}}, "Tuesday": {{}}, "Wednesday": {{}}, "Thursday": {{}}, "Friday": {{}}, "Saturday": {{}}, "Sunday": {{}}}}

Diet: {self.dietary_preferences}. Target: Protein {self.macros['protein']}g, Carbs {self.macros['carbs']}g, Fats {self.macros['fats']}g. Calories: ~{self.daily_calories} kcal/day. Return ONLY JSON, no markdown."""

        try:
            response = self._call_openrouter_api(prompt)
            meals_data = json.loads(response)
            
            # Convert to expected format
            formatted_meals = []
            for day, meals in meals_data.items():
                formatted_meals.append({
                    'day': day,
                    'breakfast': meals.get('breakfast', {}),
                    'lunch': meals.get('lunch', {}),
                    'dinner': meals.get('dinner', {}),
                    'snacks': meals.get('snacks', [])
                })
            return formatted_meals
        except Exception as e:
            print(f"⚠️ Warning: AI meal generation failed ({str(e)}), using fallback")
            return self._get_fallback_meals()
    
    # Fallback methods for fast generation
        base_water = 2.5 if self.gender == 'male' else 2.0
        base_sleep = 7.5
        
        for day in days:
            tracking[day] = {
                'steps_goal': base_steps,
                'water_liters_goal': base_water,
                'sleep_hours_goal': base_sleep,
                'workout_completed': False,
                'meals_logged': 0,
                'calories_burned_goal': 400 if self.fitness_goal == 'weight loss' else 300,
                'heart_rate_zones': {
                    'warm_up': '50-60% max HR',
                    'fat_burn': '60-70% max HR',
                    'cardio': '70-80% max HR',
                    'peak': '80-90% max HR'
                },
                'progress_notes': 'Track your daily achievements and how you feel'
            }
        
        return tracking
    
    # Fallback methods (in case API fails)
    def _get_fallback_workouts(self) -> list:
        """Simple fallback workout plan"""
        workouts_dict = {
            'Monday': [
                {
                    'phase': 'Warm-up',
                    'exercise_name': 'Dynamic Stretching',
                    'sets': 1,
                    'reps': 10,
                    'duration_minutes': 5,
                    'intensity_level': 'easy',
                    'equipment_required': 'none',
                    'alternative': 'Light cardio'
                },
                {
                    'phase': 'Main Workout',
                    'exercise_name': 'Full Body Strength Training',
                    'sets': 3,
                    'reps': 12,
                    'duration_minutes': 30,
                    'intensity_level': 'moderate',
                    'equipment_required': 'dumbbells',
                    'alternative': 'Bodyweight exercises'
                },
                {
                    'phase': 'Cool-down',
                    'exercise_name': 'Stretching',
                    'sets': 1,
                    'reps': 1,
                    'duration_minutes': 5,
                    'intensity_level': 'easy',
                    'equipment_required': 'none',
                    'alternative': 'Walking'
                }
            ],
            'Tuesday': [{'phase': 'Cardio', 'exercise_name': 'Cardio Session', 'sets': 1, 'reps': 1, 'duration_minutes': 30, 'intensity_level': 'moderate', 'equipment_required': 'none', 'alternative': 'Walking'}],
            'Wednesday': [{'phase': 'Main Workout', 'exercise_name': 'Strength Training', 'sets': 3, 'reps': 12, 'duration_minutes': 30, 'intensity_level': 'moderate', 'equipment_required': 'dumbbells', 'alternative': 'Bodyweight'}],
            'Thursday': [{'phase': 'Rest', 'exercise_name': 'Active Recovery', 'sets': 1, 'reps': 1, 'duration_minutes': 20, 'intensity_level': 'easy', 'equipment_required': 'none', 'alternative': 'Yoga'}],
            'Friday': [{'phase': 'Main Workout', 'exercise_name': 'Full Body Workout', 'sets': 3, 'reps': 12, 'duration_minutes': 30, 'intensity_level': 'moderate', 'equipment_required': 'dumbbells', 'alternative': 'Bodyweight'}],
            'Saturday': [{'phase': 'Cardio', 'exercise_name': 'HIIT Session', 'sets': 1, 'reps': 1, 'duration_minutes': 25, 'intensity_level': 'hard', 'equipment_required': 'none', 'alternative': 'Jogging'}],
            'Sunday': [{'phase': 'Rest', 'exercise_name': 'Rest Day', 'sets': 1, 'reps': 1, 'duration_minutes': 20, 'intensity_level': 'easy', 'equipment_required': 'none', 'alternative': 'Light walk'}]
        }
        
        # Convert to expected format
        formatted = []
        for day, exercises in workouts_dict.items():
            formatted.append({
                'day': day,
                'exercises': exercises
            })
        return formatted
    
    def _get_fallback_meals(self) -> list:
        """Simple fallback meal plan"""
        daily_meal = {
            'breakfast': {
                'meal': 'Protein Oatmeal',
                'description': 'Oats with protein powder and berries',
                'protein_g': int(self.macros['protein'] * 0.25),
                'carbs_g': int(self.macros['carbs'] * 0.30),
                'fats_g': int(self.macros['fats'] * 0.25),
                'calories': int(self.daily_calories * 0.25),
                'alternatives': ['Greek yogurt parfait', 'Egg white omelet']
            },
            'lunch': {
                'meal': 'Chicken and Rice Bowl',
                'description': 'Grilled chicken with brown rice and vegetables',
                'protein_g': int(self.macros['protein'] * 0.35),
                'carbs_g': int(self.macros['carbs'] * 0.35),
                'fats_g': int(self.macros['fats'] * 0.35),
                'calories': int(self.daily_calories * 0.35),
                'alternatives': ['Turkey wrap', 'Salmon salad']
            },
            'dinner': {
                'meal': 'Lean Protein Dinner',
                'description': 'Lean meat with vegetables and complex carbs',
                'protein_g': int(self.macros['protein'] * 0.30),
                'carbs_g': int(self.macros['carbs'] * 0.25),
                'fats_g': int(self.macros['fats'] * 0.30),
                'calories': int(self.daily_calories * 0.30),
                'alternatives': ['Fish with quinoa', 'Tofu stir-fry']
            },
            'snacks': [
                {
                    'meal': 'Protein Snack',
                    'description': 'Greek yogurt with nuts',
                    'protein_g': int(self.macros['protein'] * 0.05),
                    'carbs_g': int(self.macros['carbs'] * 0.05),
                    'fats_g': int(self.macros['fats'] * 0.075),
                    'calories': int(self.daily_calories * 0.05),
                    'alternatives': ['Protein bar', 'Cottage cheese']
                },
                {
                    'meal': 'Energy Snack',
                    'description': 'Fruit with nut butter',
                    'protein_g': int(self.macros['protein'] * 0.05),
                    'carbs_g': int(self.macros['carbs'] * 0.05),
                    'fats_g': int(self.macros['fats'] * 0.075),
                    'calories': int(self.daily_calories * 0.05),
                    'alternatives': ['Trail mix', 'Rice cakes']
                }
            ]
        }
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        formatted = []
        for day in days:
            formatted.append({
                'day': day,
                'breakfast': daily_meal['breakfast'],
                'lunch': daily_meal['lunch'],
                'dinner': daily_meal['dinner'],
                'snacks': daily_meal['snacks']
            })
        return formatted
    
    def _get_fallback_notifications(self) -> list:
        """Simple fallback notifications"""
        return [
            {'time': '07:00', 'type': 'workout', 'message': '💪 Time for your workout!'},
            {'time': '08:00', 'type': 'breakfast', 'message': '🥗 Breakfast time!'},
            {'time': '12:30', 'type': 'lunch', 'message': '🍽️ Lunch break!'},
            {'time': '15:00', 'type': 'snack', 'message': '🥜 Healthy snack time!'},
            {'time': '19:00', 'type': 'dinner', 'message': '🍴 Dinner time!'},
            {'time': '22:00', 'type': 'sleep_prep', 'message': '😴 Time to wind down!'}
        ]
    
    def _get_fallback_challenge(self) -> Dict[str, str]:
        """Simple fallback challenge"""
        return {
            'title': f'{self.fitness_goal.title()} Challenge',
            'description': f'Stay consistent with your {self.fitness_goal} program this week',
            'goal': 'Complete all workouts and track your meals',
            'reward': 'Improved fitness and progress toward your goal'
        }
    
    def _get_fallback_tips(self) -> list:
        """Simple fallback tips"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        tips = [
            'Stay consistent with your workouts',
            'Proper nutrition is key to results',
            'Rest and recovery are essential',
            'Focus on form over weight',
            'Stay hydrated throughout the day',
            'Get adequate sleep for recovery',
            'Reflect on your weekly progress'
        ]
        return [{'day': day, 'tip': tips[i], 'motivation': 'Keep pushing forward!'} for i, day in enumerate(days)]
    
    def get_plan_json(self) -> str:
        """Return fitness plan as JSON string"""
        plan = self.generate_weekly_plan()
        return json.dumps(plan, indent=4, ensure_ascii=False)


def main():
    """Example usage of FitMentorAI"""
    # Sample user input
    user_data = {
        "weight": 70,
        "height": 175,
        "age": 25,
        "gender": "male",
        "activity_level": "moderate",
        "fitness_goal": "muscle gain",
        "dietary_preferences": "balanced",
        "health_restrictions": "none"
    }
    
    # Create FitMentorAI instance
    print("🏋️ FitMentor AI - Powered by DeepSeek\n")
    
    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("⚠️  WARNING: OPENROUTER_API_KEY not found!")
        print("📝 Please create a .env file with your API key:")
        print("   OPENROUTER_API_KEY=your_key_here\n")
        print("🔄 Will use fallback mode for now...\n")
    
    trainer = FitMentorAI(user_data)
    
    # Generate and get plan as JSON
    plan_json = trainer.get_plan_json()
    
    # Print the plan
    print("\n" + "="*80)
    print("GENERATED PLAN:")
    print("="*80)
    print(plan_json)
    
    # Save to file
    with open('ai_fitness_plan.json', 'w', encoding='utf-8') as f:
        f.write(plan_json)
    
    print("\n✅ Plan saved to: ai_fitness_plan.json")


if __name__ == "__main__":
    main()
