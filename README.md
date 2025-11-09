# 🎬 AI Movie Recommendation App

A modern, responsive web application built with **Streamlit** that provides intelligent movie recommendations using **Gemini AI** and comprehensive movie data from multiple sources.

## ✨ Features

- **🤖 AI-Powered Recommendations**: Uses Google Gemini AI for intelligent movie suggestions
- **⭐ Star Ratings**: Displays IMDb, Rotten Tomatoes, and Metacritic ratings with visual stars
- **🔗 Where to Watch**: Direct links to Netflix, Prime Video, Hotstar, JustWatch, and more
- **🌍 Multi-Language Support**: Hindi, English, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi
- **🎭 Genre-Based Discovery**: Action, Comedy, Drama, Thriller, Romance, Horror, Sci-Fi, and more
- **📱 Fully Responsive**: Optimized for mobile, tablet, and desktop
- **⚡ Fast & Reliable**: Smart fallbacks when API limits are reached
- **🎨 Modern UI**: Beautiful glassmorphism design with smooth animations

## 🛠️ Technology Stack

- **Python 3.8+** - Core programming language
- **Streamlit** - Modern web framework
- **Google Gemini AI** - Advanced movie recommendations
- **OMDb API** - Movie ratings and metadata
- **Custom CSS** - Responsive glassmorphism UI
- **Smart Caching** - Optimized performance

## 🚀 Live Demo

The app provides two ways to get recommendations:
1. **Title-based**: Enter any movie title → Get similar movies

## 🚀 Quick Start

### Local Development

1. **Clone Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/movie-mood-app.git
   cd movie-mood-app
   ```

2. **Set Up Environment**
   - Copy `.env.example` to `.env`
   - Fill in your API keys in the `.env` file

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Application**
   ```bash
   streamlit run streamlit_app_modern.py
   ```

5. **Open in Browser**
   Navigate to `http://localhost:8501`

## ☁️ Deploy to Vercel

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Deploy to Vercel**
   - Go to [Vercel](https://vercel.com) and sign in with GitHub
   - Click "New Project" and import your repository
   - Configure project settings:
     - Framework Preset: Streamlit
     - Root Directory: (leave empty)
     - Build Command: `pip install -r requirements.txt`
     - Output Directory: (leave empty)
   - Add Environment Variables from your `.env` file
   - Click "Deploy"

3. **Configure Custom Domain (Optional)**
   - Go to your project settings in Vercel
   - Navigate to "Domains"
   - Add your custom domain and follow the verification steps

## 🔧 Environment Variables

Create a `.env` file in the root directory with the following variables:

```
TMDB_API_KEY=your_tmdb_api_key_here
TMDB_ACCESS_TOKEN=your_tmdb_access_token_here
OPENAI_API_KEY=your_openai_api_key_here
STREAMLIT_SERVER_HEADLESS=true
ENABLE_CORS=true
```

## 🔧 Configuration

### OpenAI API Setup (Optional)
1. Get your API key from [OpenAI](https://platform.openai.com/)
2. Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-api-key-here"
```

**Note:** App works perfectly without OpenAI API using the comprehensive database!

## 📊 Database Statistics
3. Get curated movie recommendations based on your preferences

### **Features You'll See:**
- ⭐ **Star ratings** with IMDb, RT, MC scores
- 🔗 **Where to watch** links (Netflix, Prime Video, Hotstar, etc.)
- 📝 **AI summaries** for each movie
- 🎭 **Genre and language** information

## 🔧 Core Functions

### Data Processing
- **`load_data()`**: Loads movie dataset from CSV
- **`prepare_features()`**: Combines genres and language for similarity calculation

### Recommendation Engine
- **`recommend_movies(title, top_n)`**: Main recommendation function using cosine similarity
- **`get_movie_index(title)`**: Finds movie index with fuzzy matching support

### Poster Integration
- **`get_poster(title)`**: Fetches movie posters from OMDb API with fallback placeholders

### Responsive UI
- **Custom CSS**: Mobile-first responsive design
- **Dynamic Layout**: Adapts to different screen sizes
- **Interactive Components**: Streamlit widgets with custom styling

## 🎨 UI Components

- **Header Section**: App title and description
- **Input Controls**: Movie selector and recommendation count slider
- **Movie Cards**: Responsive grid layout with posters and movie info
- **Sidebar**: App information and usage tips

## 🔑 API Configuration

To use real movie posters, get a free API key from [OMDb API](http://www.omdbapi.com/):

1. Sign up for a free API key
2. Replace `"your_omdb_api_key"` in `app.py` with your actual key
3. Restart the application

## 📱 Responsive Design

The app automatically adapts to different screen sizes:
- **Desktop**: 4-column grid layout
- **Tablet**: 3-column grid layout  
- **Mobile**: Single column layout with optimized spacing

## 🧪 Testing

Test the app with different movies:
- Try "Se7en" for crime thrillers
- Try "Parasite" for international films
- Try "Kahaani" for Bollywood thrillers

## 🔮 Future Enhancements

- [ ] Add more movies to the dataset
- [ ] Implement user ratings and reviews
- [ ] Add movie trailers integration
- [ ] Include more filtering options (year, director, etc.)
- [ ] Add user preference learning
- [ ] Implement collaborative filtering

## 🐛 Troubleshooting

**Issue**: "Could not find movies.csv"
- **Solution**: Ensure `movies.csv` is in the same directory as `app.py`

**Issue**: No movie posters showing
- **Solution**: Check your internet connection and OMDb API key

**Issue**: Streamlit not starting
- **Solution**: Make sure all dependencies are installed: `pip install -r requirements.txt`

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

---

**Built with ❤️ using Streamlit and Python**
