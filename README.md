# 🏋️ FitMentor AI - Premium Fitness Planner

![FitMentor AI](https://img.shields.io/badge/AI-Powered-6366F1?style=for-the-badge&logo=openai)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=for-the-badge&logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

A stunning, AI-powered fitness planning application that generates personalized workout routines and meal plans using advanced GPT-4o-mini model. Features a premium dark theme UI with animated particles, glassmorphism effects, and smooth animations.

## ✨ Features

### 🤖 AI-Powered Generation
- **Parallel Processing**: Workouts and meals generated simultaneously (50% faster)
- **GPT-4o-mini Model**: Fast, reliable, and cost-effective via OpenRouter API
- **Optimized Prompts**: 75% token reduction for faster responses
- **Personalized Plans**: Customized based on age, weight, height, goals, and dietary preferences

### 🎨 Premium UI/UX
- **Animated Background**: 50+ twinkling particles with floating gradient orbs
- **Glassmorphism Design**: Modern blurred glass effects on all cards
- **Glow Effects**: Beautiful hover animations with neon glow
- **Smooth Transitions**: Cubic-bezier animations for professional feel
- **Responsive Design**: Fully optimized for desktop, tablet, and mobile

### 📊 Comprehensive Features
- Weekly workout plans with detailed exercises
- Complete meal plans (breakfast, lunch, dinner) with macros
- Daily fitness notifications and reminders
- Weekly fitness challenges
- Personalized fitness tips and motivation
- BMI calculation and caloric needs estimation

### ⚡ Performance
- **Fast Generation**: 15-25 seconds for complete plan
- **Concurrent Processing**: ThreadPoolExecutor for parallel AI calls
- **Optimized API**: Reduced timeout and token usage
- **Web Notifications**: Real-time progress updates

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenRouter API key ([Get one here](https://openrouter.ai))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/fitmentor-ai.git
cd fitmentor-ai
```

2. **Create virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API Key**
```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your OpenRouter API key
OPENROUTER_API_KEY=your_api_key_here
```

5. **Run the application**
```bash
python api_ai.py
```

6. **Open in browser**
```
http://localhost:5000
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### API Settings

You can modify these in `fitmentor_ai.py`:
- `timeout`: API request timeout (default: 60s)
- `max_tokens`: Maximum response tokens (default: 2000)
- `temperature`: AI creativity level (default: 0.7)

## 📁 Project Structure

```
fitmentor-ai/
├── api_ai.py              # Flask API server
├── fitmentor_ai.py        # AI generation logic
├── index.html             # Premium UI
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
└── README.md             # Documentation
```

## 🎯 API Endpoints

### `POST /api/generate-plan`
Generate a complete fitness plan

**Request Body:**
```json
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
```

**Response:**
```json
{
  "user_profile": { "bmi": 22.86, "daily_calories": 2500, ... },
  "workouts": [...],
  "meals": [...],
  "notifications": [...],
  "weekly_challenge": {...},
  "fitness_tips": [...]
}
```

### `GET /api/health`
Health check endpoint

### `POST /api/calculate-bmi`
Calculate BMI

### `POST /api/calculate-calories`
Calculate daily caloric needs

## 🎨 UI Customization

The UI uses CSS variables for easy theming. Modify these in `index.html`:

```css
:root {
  --primary: #6366F1;      /* Main purple */
  --secondary: #EC4899;    /* Pink accent */
  --accent: #14B8A6;       /* Teal highlight */
  --gold: #F59E0B;         /* Premium gold */
  /* ... more colors */
}
```

## 🔒 Security

- API keys stored in `.env` (not committed to Git)
- CORS enabled for local development
- Input validation on all endpoints
- No sensitive data logged

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenRouter** for providing AI API access
- **OpenAI GPT-4o-mini** for intelligent plan generation
- **Flask** for the lightweight backend
- **Font Awesome** for beautiful icons
- **Google Fonts** for Poppins typography

## 📧 Contact

Your Name - [@yourhandle](https://twitter.com/yourhandle)

Project Link: [https://github.com/yourusername/fitmentor-ai](https://github.com/yourusername/fitmentor-ai)

---

<p align="center">Made with ❤️ and ☕</p>
<p align="center">⭐ Star this repo if you find it helpful!</p>
