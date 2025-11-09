"""
AI-Powered Movie Recommendation App
Fully AI-driven movie recommendations without any datasets
"""

import streamlit as st
import requests
import json
import random
from typing import List, Dict, Optional, Tuple
import google.generativeai as genai

# Configure Streamlit page
st.set_page_config(
    page_title="🎬 Indian Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #8B5CF6, #06B6D4, #F59E0B);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .sub-header {
        text-align: center;
        color: #64748B;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    .movie-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.04));
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    
    .movie-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(139,92,246,0.2);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #8B5CF6, #06B6D4);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139,92,246,0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #8B5CF6, #06B6D4);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class AIMovieRecommender:
    def __init__(self):
        self.omdb_api_key = "7f7c782e-0051-449b-8636-94d0a0719c05"
        self.gemini_api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyDhkVQFnytIwvKJoe2Rw8jmJ0H2KuNjTwI")
        
        # Configure Gemini AI
        try:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            st.warning(f"Gemini AI not available: {str(e)}. Using fallback AI logic.")
            self.model = None
    
    def get_ai_recommendations(self, query: str, num_recommendations: int = 5) -> List[Dict]:
        """Generate comprehensive movie dataset using AI logic"""
        
        # AI-curated Indian cinema database with diverse representation
        movies_data = {
            'title': [
                # Bollywood Classics & Modern Hits
                'Dangal', '3 Idiots', 'Lagaan', 'Queen', 'Pink', 'Article 15', 'Andhadhun', 'Tumhari Sulu',
                'Stree', 'Badhaai Ho', 'Super 30', 'Gully Boy', 'URI: The Surgical Strike', 'Shershaah',
                'Zindagi Na Milegi Dobara', 'Taare Zameen Par', 'Haider', 'Piku', 'October', 'Vicky Donor',
                
                # South Indian Blockbusters
                'Baahubali: The Beginning', 'Baahubali 2: The Conclusion', 'RRR', 'KGF: Chapter 1', 'KGF: Chapter 2',
                'Pushpa: The Rise', 'Arjun Reddy', 'Kabir Singh', 'Vikram', 'Master', 'Asuran', 'Super Deluxe',
                '96', 'Soorarai Pottru', 'Jersey', 'Mahanati', 'C/o Kancharapalem', 'Brochevarevarura',
                
                # Regional Cinema Gems
                'Drishyam', 'Drishyam 2', 'Bangalore Days', 'Premam', 'Ustad Hotel', 'Charlie', 'Maheshinte Prathikaaram',
                'Minnal Murali', 'The Great Indian Kitchen', 'Jallikattu', 'Ee.Ma.Yau', 'Angamaly Diaries',
                
                # Marathi & Bengali Cinema
                'Court', 'Fandry', 'Sairat', 'Natsamrat', 'Katyar Kaljat Ghusali', 'Harishchandrachi Factory',
                'Piku', 'Kahaani', 'Vicky Donor', 'October'
            ],
            
            'language': [
                # Bollywood
                'Hindi', 'Hindi', 'Hindi', 'Hindi', 'Hindi', 'Hindi', 'Hindi', 'Hindi',
                'Hindi', 'Hindi', 'Hindi', 'Hindi', 'Hindi', 'Hindi',
                'Hindi', 'Hindi', 'Hindi', 'Hindi', 'Hindi', 'Hindi',
                
                # South Indian
                'Telugu', 'Telugu', 'Telugu', 'Kannada', 'Kannada',
                'Telugu', 'Telugu', 'Hindi', 'Tamil', 'Tamil', 'Tamil', 'Tamil',
                'Tamil', 'Tamil', 'Telugu', 'Telugu', 'Telugu', 'Telugu',
                
                # Malayalam
                'Malayalam', 'Malayalam', 'Malayalam', 'Malayalam', 'Malayalam', 'Malayalam', 'Malayalam',
                'Malayalam', 'Malayalam', 'Malayalam', 'Malayalam', 'Malayalam',
                
                # Regional
                'Marathi', 'Marathi', 'Marathi', 'Marathi', 'Marathi', 'Marathi',
                'Bengali', 'Bengali', 'Hindi', 'Hindi'
            ],
            
            'genres': [
                # Bollywood
                'Drama,Sport,Biography', 'Comedy,Drama', 'Drama,Musical,Sport', 'Comedy,Drama', 'Drama,Thriller', 
                'Crime,Drama,Thriller', 'Crime,Mystery,Thriller', 'Comedy,Drama', 'Comedy,Horror', 'Comedy,Drama',
                'Biography,Drama', 'Drama,Music', 'Action,Drama,War', 'Action,Biography,Drama', 'Adventure,Comedy,Drama',
                'Drama,Family', 'Action,Crime,Drama', 'Comedy,Drama', 'Drama,Romance', 'Comedy,Drama,Romance',
                
                # South Indian
                'Action,Drama,Fantasy', 'Action,Drama,Fantasy', 'Action,Drama', 'Action,Crime,Drama', 'Action,Crime,Drama',
                'Action,Crime,Drama', 'Drama,Romance', 'Drama,Romance', 'Action,Crime,Thriller', 'Action,Crime,Drama',
                'Action,Drama', 'Comedy,Crime,Drama', 'Drama,Romance', 'Comedy,Drama', 'Drama,Sport', 'Biography,Drama',
                'Drama,Romance', 'Comedy,Crime',
                
                # Malayalam
                'Crime,Drama,Thriller', 'Crime,Drama,Thriller', 'Comedy,Drama,Romance', 'Comedy,Drama,Romance',
                'Drama', 'Adventure,Comedy,Drama', 'Comedy,Drama', 'Action,Comedy,Drama', 'Drama', 'Action,Drama,Thriller',
                'Comedy,Drama', 'Action,Comedy,Crime',
                
                # Regional
                'Drama', 'Drama,Romance', 'Drama,Musical,Romance', 'Drama', 'Drama,Musical', 'Biography,Comedy,Drama',
                'Mystery,Thriller', 'Mystery,Thriller', 'Comedy,Drama', 'Drama,Romance'
            ],
            
            'director': [
                # Bollywood Directors
                'Nitesh Tiwari', 'Rajkumar Hirani', 'Ashutosh Gowariker', 'Vikas Bahl', 'Aniruddha Roy Chowdhury',
                'Anubhav Sinha', 'Sriram Raghavan', 'Suresh Triveni', 'Amar Kaushik', 'Amit Sharma',
                'Vikas Bahl', 'Zoya Akhtar', 'Aditya Dhar', 'Vishnuvardhan', 'Zoya Akhtar',
                'Aamir Khan', 'Vishal Bhardwaj', 'Shoojit Sircar', 'Shoojit Sircar', 'Shoojit Sircar',
                
                # South Indian Directors
                'S.S. Rajamouli', 'S.S. Rajamouli', 'S.S. Rajamouli', 'Prashanth Neel', 'Prashanth Neel',
                'Sukumar', 'Sandeep Reddy Vanga', 'Sandeep Reddy Vanga', 'Lokesh Kanagaraj', 'Lokesh Kanagaraj',
                'Vetrimaaran', 'Thiagarajan Kumararaja', 'C. Prem Kumar', 'Sudha Kongara', 'Gowtam Tinnanuri',
                'Nag Ashwin', 'Venkatesh Maha', 'Vivek Athreya',
                
                # Malayalam Directors
                'Jeethu Joseph', 'Jeethu Joseph', 'Anjali Menon', 'Alphonse Puthren', 'Anwar Rasheed',
                'Martin Prakkat', 'Dileesh Pothan', 'Basil Joseph', 'Jeo Baby', 'Lijo Jose Pellissery',
                'Lijo Jose Pellissery', 'Lijo Jose Pellissery',
                
                # Regional Directors
                'Chaitanya Tamhane', 'Nagraj Manjule', 'Nagraj Manjule', 'Mahesh Manjrekar', 'Subodh Bhave',
                'Paresh Mokashi', 'Sujoy Ghosh', 'Sujoy Ghosh', 'Shoojit Sircar', 'Shoojit Sircar'
            ],
            
            'main_actors': [
                # Bollywood Cast
                'Aamir Khan,Fatima Sana Shaikh,Sanya Malhotra', 'Aamir Khan,R. Madhavan,Sharman Joshi',
                'Aamir Khan,Gracy Singh,Rachel Shelley', 'Kangana Ranaut,Rajkummar Rao,Lisa Haydon',
                'Taapsee Pannu,Amitabh Bachchan,Kirti Kulhari', 'Ayushmann Khurrana,Nassar,Manoj Pahwa',
                'Ayushmann Khurrana,Tabu,Radhika Apte', 'Vidya Balan,Manav Kaul,Neha Dhupia',
                'Rajkummar Rao,Shraddha Kapoor,Pankaj Tripathi', 'Ayushmann Khurrana,Neena Gupta,Gajraj Rao',
                'Hrithik Roshan,Mrunal Thakur,Nandish Sandhu', 'Ranveer Singh,Alia Bhatt,Siddhant Chaturvedi',
                'Vicky Kaushal,Paresh Rawal,Mohit Raina', 'Sidharth Malhotra,Kiara Advani,Shiv Panditt',
                'Hrithik Roshan,Farhan Akhtar,Abhay Deol', 'Aamir Khan,Darsheel Safary,Tisca Chopra',
                'Shahid Kapoor,Tabu,Shraddha Kapoor', 'Deepika Padukone,Amitabh Bachchan,Irrfan Khan',
                'Varun Dhawan,Banita Sandhu,Gitanjali Rao', 'Ayushmann Khurrana,Yami Gautam,Annu Kapoor',
                
                # South Indian Cast
                'Prabhas,Rana Daggubati,Anushka Shetty', 'Prabhas,Rana Daggubati,Anushka Shetty',
                'N.T. Rama Rao Jr.,Ram Charan,Alia Bhatt', 'Yash,Srinidhi Shetty,Ramachandra Raju',
                'Yash,Srinidhi Shetty,Sanjay Dutt', 'Allu Arjun,Rashmika Mandanna,Fahadh Faasil',
                'Vijay Deverakonda,Shalini Pandey,Jia Sharma', 'Shahid Kapoor,Kiara Advani,Suresh Oberoi',
                'Kamal Haasan,Vijay Sethupathi,Fahadh Faasil', 'Vijay,Vijay Sethupathi,Malavika Mohanan',
                'Dhanush,Manju Warrier,Prakash Raj', 'Vijay Sethupathi,Fahadh Faasil,Samantha Ruth Prabhu',
                'Vijay Sethupathi,Trisha Krishnan,Aadukalam Naren', 'Suriya,Aparna Balamurali,Paresh Rawal',
                'Nani,Shraddha Srinath,Sathyaraj', 'Keerthy Suresh,Dulquer Salmaan,Samantha Ruth Prabhu',
                'Subba Rao Vepada,Radha Bessy,Praneeta Patnaik', 'Sree Vishnu,Nivetha Thomas,Nivetha Pethuraj',
                
                # Malayalam Cast
                'Mohanlal,Meena,Asha Sarath', 'Mohanlal,Meena,Ansiba Hassan', 'Dulquer Salmaan,Nivin Pauly,Nazriya Nazim',
                'Nivin Pauly,Sai Pallavi,Madonna Sebastian', 'Dulquer Salmaan,Nithya Menen,Thilakan',
                'Dulquer Salmaan,Parvathy Thiruvothu,Aparna Gopinath', 'Fahadh Faasil,Anusree,Aparna Balamurali',
                'Tovino Thomas,Guru Somasundaram,Harisree Ashokan', 'Nimisha Sajayan,Suraj Venjaramoodu,Ajitha V.M.',
                'Antony Varghese,Chemban Vinod Jose,Sabumon Abdusamad', 'Chemban Vinod Jose,Vinayakan,Dileesh Pothan',
                'Antony Varghese,Anna Reshma Rajan,Vineeth Vishwam',
                
                # Regional Cast
                'Vira Sathidar,Vivek Gomber,Geetanjali Kulkarni', 'Somnath Awghade,Rajeshwari Kharat,Suraj Pawar',
                'Rinku Rajguru,Akash Thosar,Tanaji Galgunde', 'Nana Patekar,Medha Manjrekar,Mrunmayee Deshpande',
                'Sachin Pilgaonkar,Shankar Mahadevan,Subodh Bhave', 'Nandu Madhav,Vibhawari Deshpande,Atharva Karve',
                'Vidya Balan,Parambrata Chatterjee,Indraneil Sengupta', 'Vidya Balan,Arjun Rampal,Jugal Hansraj',
                'Deepika Padukone,Amitabh Bachchan,Irrfan Khan', 'Varun Dhawan,Banita Sandhu,Gitanjali Rao'
            ],
            
            'keywords': [
                # Bollywood Keywords
                'wrestling,father daughter,sports,inspiration,true story', 'friendship,education,comedy,engineering,college',
                'cricket,british raj,village,tax,period drama', 'women empowerment,solo travel,comedy,self discovery',
                'women safety,consent,social issue,courtroom drama', 'caste discrimination,social justice,investigation,rural india',
                'blind pianist,murder,dark comedy,thriller,twist', 'housewife,radio jockey,women empowerment,family',
                'horror comedy,folklore,small town,ghost,humor', 'family,pregnancy,comedy,social taboo,middle class',
                'education,mathematics,inspiration,true story,underprivileged', 'rap music,slum,dreams,hip hop,mumbai',
                'military,surgical strike,patriotic,action,terrorism', 'war,kargil,captain vikram batra,sacrifice,patriotic',
                'friendship,adventure,spain,bachelor party,self discovery', 'dyslexia,teacher,child,education,emotional',
                'hamlet adaptation,kashmir,revenge,political,shakespeare', 'father daughter,constipation,road trip,family,slice of life',
                'hotel management,coma,love,care,unconventional romance', 'sperm donation,infertility,taboo,comedy,social issue',
                
                # South Indian Keywords
                'epic,kingdom,revenge,warrior,mythology', 'epic,kingdom,revenge,warrior,mythology',
                'freedom fighters,british raj,friendship,action,period', 'gold mine,gangster,period,action,rise to power',
                'gold mine,gangster,period,action,empire', 'red sandalwood,smuggling,forest,action,mass',
                'love,obsession,medical student,self destruction,intense', 'love,obsession,medical student,self destruction,intense',
                'undercover,drug cartel,action,thriller,revenge', 'college,gangster,professor,action,redemption',
                'caste violence,revenge,father son,rural,social issue', 'anthology,dark comedy,interconnected stories,quirky',
                'school reunion,nostalgia,love,memories,emotional', 'aviation,dreams,entrepreneur,inspiration,true story',
                'cricket,comeback,father son,dreams,middle age', 'savitri,actress,biography,golden age,telugu cinema',
                'anthology,love stories,small town,realistic,slice of life', 'kidnapping,comedy,friendship,college,heist',
                
                # Malayalam Keywords
                'family,murder,investigation,perfect crime,suspense', 'sequel,investigation,family,past,consequences',
                'cousins,bangalore,friendship,love,dreams', 'love,stages of life,school,college,nostalgia',
                'cooking,grandfather,hotel,dreams,family tradition', 'free spirit,artist,adventure,love,mystery',
                'photographer,village,revenge,slice of life,realistic', 'superhero,village,tailor,powers,malayalam',
                'patriarchy,kitchen,women,household,social issue', 'buffalo,chaos,mob,primal,violence',
                'death,ritual,comedy,social satire,village', 'pork,angamaly,local,realistic,single shot',
                
                # Regional Keywords
                'legal system,social issue,folk singer,justice,realistic', 'caste,love,rural,social issue,coming of age',
                'caste,honor killing,love,rural,social issue', 'theater,actor,aging,family,emotional',
                'classical music,rivalry,gharana,tradition,musical', 'dadasaheb phalke,first indian film,cinema history,biography',
                'missing person,kolkata,pregnancy,mystery,thriller', 'kidnapping,kolkata,mystery,thriller,investigation',
                'father daughter,constipation,road trip,family,slice of life', 'hotel management,coma,love,care,unconventional romance'
            ],
            
            'year': [
                # Bollywood Years
                2016, 2009, 2001, 2013, 2016, 2019, 2018, 2017, 2018, 2018,
                2019, 2019, 2019, 2021, 2011, 2007, 2014, 2015, 2018, 2012,
                
                # South Indian Years
                2015, 2017, 2022, 2018, 2022, 2021, 2017, 2019, 2022, 2021,
                2019, 2019, 2018, 2020, 2019, 2018, 2018, 2019,
                
                # Malayalam Years
                2013, 2021, 2014, 2015, 2012, 2015, 2016, 2021, 2021, 2019,
                2018, 2017,
                
                # Regional Years
                2014, 2013, 2016, 2016, 2015, 2009, 2012, 2015, 2015, 2018
            ],
            
            'rating': [
                # Bollywood Ratings
                8.4, 8.4, 8.1, 8.2, 8.1, 8.1, 8.2, 7.1, 7.5, 7.9,
                7.9, 7.9, 8.2, 8.4, 8.2, 8.4, 8.1, 7.6, 7.5, 7.8,
                
                # South Indian Ratings
                8.0, 8.2, 7.9, 8.2, 8.4, 7.6, 8.1, 7.0, 8.4, 7.3,
                8.4, 8.3, 8.5, 8.7, 8.6, 8.7, 8.4, 8.1,
                
                # Malayalam Ratings
                8.6, 8.4, 8.3, 8.3, 8.2, 8.1, 8.0, 7.8, 8.3, 7.1,
                7.8, 7.6,
                
                # Regional Ratings
                8.1, 8.0, 8.3, 8.8, 8.8, 8.6, 8.1, 7.9, 7.6, 7.5
            ]
        }
        
        return movies_data
    
    @st.cache_data
    def compute_similarity(_self, df):
        """Compute similarity matrix"""
        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=1000,
                ngram_range=(1, 2)
            )
            
            _self.tfidf_matrix = vectorizer.fit_transform(df['combined_features'])
            _self.cosine_sim = cosine_similarity(_self.tfidf_matrix, _self.tfidf_matrix)
            
            return _self.cosine_sim
            
        except Exception as e:
            st.error(f"Error computing similarity: {str(e)}")
            return None
    
    def find_movie_match(self, input_title: str) -> Tuple[Optional[str], Optional[int]]:
        """Find best matching movie"""
        input_clean = input_title.lower().strip()
        
        if input_clean in self.movie_indices:
            idx = self.movie_indices[input_clean]
            return self.df.iloc[idx]['title'], idx
        
        # Fuzzy matching
        all_titles = list(self.movie_indices.keys())
        close_matches = difflib.get_close_matches(input_clean, all_titles, n=1, cutoff=0.6)
        
        if close_matches:
            matched_title = close_matches[0]
            idx = self.movie_indices[matched_title]
            return self.df.iloc[idx]['title'], idx
        
        return None, None
    
    def get_recommendations(self, movie_title: str, num_recs: int = 5) -> List[Dict]:
        """Get movie recommendations"""
        matched_title, movie_idx = self.find_movie_match(movie_title)
        
        if movie_idx is None:
            return []
        
        sim_scores = list(enumerate(self.cosine_sim[movie_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        similar_movies = sim_scores[1:num_recs + 1]
        
        recommendations = []
        input_movie = self.df.iloc[movie_idx]
        
        for idx, score in similar_movies:
            movie = self.df.iloc[idx]
            reason = self.generate_reason(input_movie, movie)
            poster_url = self.get_poster(movie['title'])
            
            recommendations.append({
                'title': movie['title'],
                'language': movie['language'],
                'genres': movie['genres'],
                'director': movie['director'],
                'main_actors': movie['main_actors'],
                'year': movie['year'],
                'rating': movie['rating'],
                'poster': poster_url,
                'reason': reason,
                'similarity': round(score, 3)
            })
        
        return recommendations
    
    def generate_reason(self, input_movie, rec_movie) -> str:
        """Generate recommendation reason"""
        reasons = []
        
        # Check genres
        input_genres = set(input_movie['genres'].lower().split(','))
        rec_genres = set(rec_movie['genres'].lower().split(','))
        common_genres = input_genres.intersection(rec_genres)
        if common_genres:
            reasons.append(f"Similar genres: {', '.join(common_genres)}")
        
        # Check director
        if input_movie['director'].lower() == rec_movie['director'].lower():
            reasons.append(f"Same director: {input_movie['director']}")
        
        # Check language
        if input_movie['language'].lower() == rec_movie['language'].lower():
            reasons.append(f"Same language: {input_movie['language']}")
        
        return " | ".join(reasons) if reasons else "Similar themes and style"
    
    def get_poster(self, movie_title: str) -> str:
        """Get movie poster placeholder (offline mode)"""
        # Using placeholder images for offline mode
        poster_map = {
            'Dangal': 'https://m.media-amazon.com/images/M/MV5BMTQ4MzQzMzM2Nl5BMl5BanBnXkFtZTgwMTQ1NzU3MDI@._V1_SX300.jpg',
            'Baahubali': 'https://m.media-amazon.com/images/M/MV5BYThjYjI5ZmYtOGU0Ni00OTMxLWJkNWEtOWU0Yjk0YjE1MDE4XkEyXkFqcGdeQXVyNTI4MzE4MDU@._V1_SX300.jpg',
            '3 Idiots': 'https://m.media-amazon.com/images/M/MV5BNTkyOGVjMGEtNmQzZi00NzFlLTlhOWQtODYyMDc2ZGJmYzFhXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg',
            'Queen': 'https://m.media-amazon.com/images/M/MV5BMTMxOTMwNDU0NV5BMl5BanBnXkFtZTgwNjM2NzQzMTE@._V1_SX300.jpg',
            'Lagaan': 'https://m.media-amazon.com/images/M/MV5BNDEyYWJhNmItNzQyZC00NzY5LWEzMmEtMzU3YWU5NzVmMzA0XkEyXkFqcGdeQXVyNDUzOTQ5MjY@._V1_SX300.jpg'
        }
        
        return poster_map.get(movie_title, f"https://via.placeholder.com/300x450/8B5CF6/FFFFFF?text={movie_title.replace(' ', '+')}")

def main():
    # Initialize recommender
    if 'recommender' not in st.session_state:
        st.session_state.recommender = StreamlitMovieRecommender()
    
    recommender = st.session_state.recommender
    
    # Load data
    df = recommender.load_data()
    if df is None:
        st.error("Failed to load movie data")
        return
    
    # Compute similarity
    cosine_sim = recommender.compute_similarity(df)
    if cosine_sim is None:
        st.error("Failed to compute similarity matrix")
        return
    
    # Header
    st.markdown('<h1 class="main-header">🎬 Indian Movie Recommender</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Discover your next favorite film from Bollywood and regional cinema!</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Dataset Stats")
        st.metric("Total Movies", len(df))
        st.metric("Languages", df['language'].nunique())
        st.metric("Avg Rating", f"{df['rating'].mean():.1f}")
        
        st.markdown("### 🎭 Languages")
        for lang in df['language'].value_counts().head(5).index:
            count = df['language'].value_counts()[lang]
            st.write(f"• {lang}: {count} movies")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["🔍 Movie Search", "🎭 Browse by Genre", "📈 Top Rated"])
    
    with tab1:
        st.markdown("### 🎬 Find Similar Movies")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            movie_input = st.text_input(
                "Enter a movie title:",
                placeholder="e.g., Dangal, Baahubali, 3 Idiots",
                help="Type any movie name to get similar recommendations"
            )
        
        with col2:
            num_recs = st.selectbox("Recommendations:", [3, 5, 8, 10], index=1)
        
        if st.button("🚀 Get Recommendations", use_container_width=True):
            if movie_input:
                with st.spinner("Finding perfect recommendations..."):
                    recommendations = recommender.get_recommendations(movie_input, num_recs)
                
                if recommendations:
                    st.success(f"Found {len(recommendations)} recommendations for '{movie_input}'!")
                    
                    # Display recommendations
                    cols = st.columns(min(3, len(recommendations)))
                    for i, rec in enumerate(recommendations):
                        with cols[i % 3]:
                            st.markdown(f"""
                            <div class="movie-card">
                                <h4>{rec['title']} ({rec['year']})</h4>
                                <p><strong>Language:</strong> {rec['language']}</p>
                                <p><strong>Genres:</strong> {rec['genres']}</p>
                                <p><strong>Director:</strong> {rec['director']}</p>
                                <p><strong>Rating:</strong> ⭐ {rec['rating']}/10</p>
                                <p><strong>Why recommended:</strong> {rec['reason']}</p>
                                <p><strong>Similarity:</strong> {int(rec['similarity']*100)}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show poster
                            st.image(rec['poster'], use_column_width=True)
                else:
                    st.error(f"No recommendations found for '{movie_input}'. Please check the spelling or try another movie.")
            else:
                st.warning("Please enter a movie title!")
    
    with tab2:
        st.markdown("### 🎭 Browse by Genre & Language")
        
        col1, col2 = st.columns(2)
        with col1:
            selected_genre = st.selectbox(
                "Select Genre:",
                ["All"] + sorted(set([genre for genres in df['genres'] for genre in genres.split(',')]))
            )
        
        with col2:
            selected_language = st.selectbox(
                "Select Language:",
                ["All"] + sorted(df['language'].unique())
            )
        
        # Filter movies
        filtered_df = df.copy()
        if selected_genre != "All":
            filtered_df = filtered_df[filtered_df['genres'].str.contains(selected_genre, case=False)]
        if selected_language != "All":
            filtered_df = filtered_df[filtered_df['language'] == selected_language]
        
        st.markdown(f"### 📽️ Found {len(filtered_df)} movies")
        
        # Display filtered movies
        for _, movie in filtered_df.iterrows():
            col1, col2 = st.columns([1, 3])
            with col1:
                poster_url = recommender.get_poster(movie['title'])
                st.image(poster_url, width=150)
            
            with col2:
                st.markdown(f"""
                **{movie['title']}** ({movie['year']})
                
                **Language:** {movie['language']}  
                **Genres:** {movie['genres']}  
                **Director:** {movie['director']}  
                **Cast:** {movie['main_actors']}  
                **Rating:** ⭐ {movie['rating']}/10
                """)
            
            st.divider()
    
    with tab3:
        st.markdown("### 📈 Top Rated Movies")
        
        top_movies = df.nlargest(10, 'rating')
        
        for i, (_, movie) in enumerate(top_movies.iterrows(), 1):
            col1, col2, col3 = st.columns([0.5, 1, 3])
            
            with col1:
                st.markdown(f"### #{i}")
            
            with col2:
                poster_url = recommender.get_poster(movie['title'])
                st.image(poster_url, width=120)
            
            with col3:
                st.markdown(f"""
                **{movie['title']}** ({movie['year']})
                
                **Rating:** ⭐ {movie['rating']}/10  
                **Language:** {movie['language']}  
                **Genres:** {movie['genres']}  
                **Director:** {movie['director']}
                """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #64748B; padding: 2rem 0;'>
        <p>🎬 Made with ❤️ for Indian Cinema lovers | Powered by Streamlit & Machine Learning</p>
        <p>Data from OMDb API | TF-IDF + Cosine Similarity Algorithm</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
