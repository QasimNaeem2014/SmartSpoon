import streamlit as st
import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import mimetypes
from dotenv import load_dotenv, set_key, find_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SmartSpoon - AI Recipe Generator",
    page_icon="🥄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for aesthetic design
st.markdown("""
<style>
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #1a0033 0%, #000000 50%, #2d1b4e 100%);
        padding: 2rem;
        position: relative;
        min-height: 100vh;
    }
    
    /* Animated background particles */
    .main::before {
        content: "🍳 🥘 🍽 🔪 🥄 🍴 👨‍🍳 🥗 🍕 🍝";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        font-size: 2rem;
        opacity: 0.03;
        word-spacing: 3rem;
        line-height: 5rem;
        overflow: hidden;
        pointer-events: none;
        z-index: 1;
        animation: float-icons 20s linear infinite;
    }
    
    @keyframes float-icons {
        0% { transform: translateY(0); }
        100% { transform: translateY(-100px); }
    }
    
    /* Logo and Brand Container */
    .brand-container {
        text-align: center;
        margin-bottom: 3rem;
        position: relative;
        z-index: 10;
    }
    
    /* Floating Logo Animation */
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        25% { transform: translateY(-20px) rotate(5deg); }
        50% { transform: translateY(-10px) rotate(0deg); }
        75% { transform: translateY(-20px) rotate(-5deg); }
    }
    
    @keyframes glow {
        0%, 100% { text-shadow: 0 0 20px rgba(255,255,255,0.5), 0 0 40px rgba(255,255,255,0.3); }
        50% { text-shadow: 0 0 30px rgba(255,255,255,0.8), 0 0 60px rgba(255,255,255,0.5); }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    .logo-spoon {
        font-size: 5rem;
        display: inline-block;
        animation: float 4s ease-in-out infinite;
        filter: drop-shadow(0 10px 20px rgba(0,0,0,0.3));
        margin-bottom: 1rem;
    }
    
    /* Brand Name */
    .brand-name {
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(45deg, #ffffff, #f0f0f0, #ffffff, #e0e0e0);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 3s linear infinite, glow 2s ease-in-out infinite;
        letter-spacing: 3px;
        margin: 0;
        padding: 0;
        text-transform: uppercase;
        position: relative;
        display: inline-block;
    }
    
    .brand-name::before {
        content: "SmartSpoon";
        position: absolute;
        top: 0;
        left: 0;
        z-index: -1;
        background: linear-gradient(45deg, #ff6ec4, #7873f5, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: blur(15px);
        opacity: 0.7;
    }
    
    /* Card styling */
    .stTabs {
        background: rgba(0, 0, 0, 0.85);
        padding: 2.5rem;
        border-radius: 25px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        backdrop-filter: blur(10px);
        position: relative;
        z-index: 10;
    }
    
    /* Subheader styling */
    .subtitle {
        text-align: center;
        color: rgba(255,255,255,0.95);
        font-size: 1.3rem;
        margin-top: 1rem;
        margin-bottom: 3rem;
        font-weight: 300;
        letter-spacing: 1px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        justify-content: center;
        background: transparent;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 8px 25px rgba(245, 87, 108, 0.4);
        transform: scale(1.05);
    }
    
    .stTabs [data-baseweb="tab"]::after {
        display: none !important;
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        padding: 1rem 2.5rem;
        font-size: 1.2rem;
        font-weight: 700;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(245, 87, 108, 0.4);
        transition: all 0.3s ease;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(245, 87, 108, 0.5);
        background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 15px;
        border: 2px solid #444;
        padding: 1rem;
        transition: all 0.3s ease;
        background: rgba(30, 30, 30, 0.9);
        color: #ffffff;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
        background: rgba(40, 40, 40, 1);
    }
    
    /* Select box styling */
    .stSelectbox>div>div {
        border-radius: 15px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox>div>div:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Success message */
    .stSuccess {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        border-radius: 15px;
        padding: 1.2rem;
        color: #006400;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(132, 250, 176, 0.3);
    }
    
    /* Warning message */
    .stWarning {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        border-radius: 15px;
        padding: 1.2rem;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(255, 234, 167, 0.3);
    }
    
    /* Recipe output styling */
    .recipe-output {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe5e5 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-top: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border: 3px solid rgba(245, 87, 108, 0.2);
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Image preview */
    .stImage {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stImage:hover {
        transform: scale(1.02);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        border-left: 6px solid #667eea;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        color: #ffffff;
    }
    
    /* Labels styling */
    label {
        font-weight: 600;
        font-size: 1.05rem;
        color: #ffffff;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: rgba(102, 126, 234, 0.05);
        padding: 1rem;
        border-radius: 15px;
    }
    
    /* File uploader */
    .stFileUploader {
        border: 3px dashed #667eea;
        border-radius: 20px;
        padding: 2rem;
        background: rgba(102, 126, 234, 0.05);
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #f093fb;
        background: rgba(240, 147, 251, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Function to save API key to .env file
def save_api_key_to_env(api_key):
    env_file = find_dotenv()
    if not env_file:
        env_file = '.env'
        with open(env_file, 'w') as f:
            f.write('')
    
    set_key(env_file, "GEMINI_API_KEY", api_key)
    os.environ["GEMINI_API_KEY"] = api_key
    return True

# Initialize Gemini client
@st.cache_resource
def get_gemini_client(api_key):
    return genai.Client(api_key=api_key)

# Helper function to generate recipe from ingredients
def generate_recipe_from_ingredients(client, ingredients, dietary_pref, cuisine, meal_type):
    # Check if input looks like a non-food question
    non_food_keywords = ['who made', 'who is', 'what is', 'when was', 'where is', 'capital', 'president', 'history', 'math', 'calculate']
    if any(keyword in ingredients.lower() for keyword in non_food_keywords):
        return "I don't know. I can only help with recipes and cooking-related questions."
    
    prompt = f"""Create a detailed recipe based on the following:
    
Ingredients: {ingredients}
Dietary Preference: {dietary_pref}
Cuisine Style: {cuisine}
Meal Type: {meal_type}
Make sure response should not be very and readable for user. 
Provide a recipe with:
- Recipe name
- Preparation time
- Servings
- Ingredients list (with measurements)
- Step-by-step instructions

Be direct and concise. Start directly with the recipe name."""

    contents = [types.Part.from_text(text=prompt)]
    
    config = types.GenerateContentConfig(
        response_modalities=["TEXT"],
        temperature=0.7
    )
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=config
    )
    
    return response.text

# Helper function to generate recipe from image
def generate_recipe_from_image(client, image_bytes, mime_type):
    prompt = """You are a senior chef. From the given image, identify the food item and provide its recipe.
Answer should not be very long, and to the point like dont add transition senetence like "Here is the recipe.."
Give a to-the-point recipe with:
- Food name
- Preparation time
- Ingredients (with measurements)
- Step-by-step instructions

Be direct and concise."""

    contents = [
        types.Part(inline_data=types.Blob(mime_type=mime_type, data=image_bytes)),
        types.Part.from_text(text=prompt)
    ]
    
    config = types.GenerateContentConfig(
        response_modalities=["TEXT"],
        temperature=0.7
    )
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=config
    )
    
    return response.text

# Main app
def main():
    # Brand Header with Floating Logo
    st.markdown("""
    <div class="brand-container">
        <div class="logo-spoon">🥄</div>
        <h1 class="brand-name">SmartSpoon</h1>
        <p class="subtitle">Transform ingredients into delicious recipes with the power of AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    # API Key Configuration Section
    if not api_key or api_key == "your_gemini_api_key_here":
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.warning("⚠ Please configure your Gemini API key to use the app")
        
        st.markdown("""
        How to get your API key:
        1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Create or copy your API key
        3. Paste it below and click Save
        """)
        
        col1, col2 = st.columns([4, 1])
        with col1:
            new_api_key = st.text_input(
                "Enter your Gemini API Key",
                type="password",
                placeholder="AIza..."
            )
        with col2:
            st.write("")
            st.write("")
            if st.button("💾 Save", type="primary"):
                if new_api_key and len(new_api_key) > 20:
                    try:
                        # Test the API key
                        test_client = genai.Client(api_key=new_api_key)
                        # Save to .env
                        save_api_key_to_env(new_api_key)
                        st.success("✅ API key saved successfully!")
                        st.info("🔄 Please refresh the page to continue")
                        st.stop()
                    except Exception as e:
                        st.error(f"❌ Invalid API key: {str(e)}")
                else:
                    st.error("Please enter a valid API key")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    
    # Initialize client
    try:
        client = get_gemini_client(api_key)
    except Exception as e:
        st.error(f"Error initializing Gemini client: {str(e)}")
        st.stop()
    
    # Create tabs
    tab1, tab2 = st.tabs(["📝 From Ingredients", "📸 From Image"])
    
    # Tab 1: Generate from Ingredients
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            ingredients = st.text_area(
                "🥗 Enter Ingredients",
                placeholder="e.g., chicken, tomatoes, garlic, olive oil",
                height=120
            )
            
            dietary_pref = st.selectbox(
                "🥑 Dietary Preference",
                ["No Preference", "Vegetarian", "Vegan", "Gluten-Free", "Keto", "Low-Carb", "Dairy-Free"]
            )
        
        with col2:
            cuisine = st.selectbox(
                "🌍 Cuisine Style",
                ["Any", "Italian", "Chinese", "Indian", "Mexican", "Thai", "Japanese", "French", "Mediterranean", "American"]
            )
            
            meal_type = st.selectbox(
                "🍽 Meal Type",
                ["Any", "Breakfast", "Lunch", "Dinner", "Snack", "Dessert", "Appetizer"]
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🔥 Generate Recipe", key="gen_ingredients", type="primary"):
                if not ingredients:
                    st.warning("Please enter at least one ingredient!")
                else:
                    with st.spinner("👨‍🍳 Creating your recipe..."):
                        try:
                            recipe = generate_recipe_from_ingredients(
                                client, ingredients, dietary_pref, cuisine, meal_type
                            )
                            st.success("✅ Recipe generated successfully!")
                            st.markdown("### 📋 Your Recipe:")
                            st.markdown(recipe)
                        except Exception as e:
                            st.error(f"❌ Error generating recipe: {str(e)}")
    
    # Tab 2: Generate from Image
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            upload_option = st.radio(
                "📷 Choose input method:",
                ["Upload Image", "Take Photo"],
                horizontal=True
            )
            
            image = None
            image_bytes = None
            mime_type = None
            
            if upload_option == "Upload Image":
                uploaded_file = st.file_uploader(
                    "Upload food image",
                    type=["jpg", "jpeg", "png", "webp"],
                    help="Upload a clear image of the food"
                )
                
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    image_bytes = uploaded_file.getvalue()
                    mime_type = uploaded_file.type
            
            else:
                camera_image = st.camera_input("Take a photo of your food")
                
                if camera_image:
                    image = Image.open(camera_image)
                    image_bytes = camera_image.getvalue()
                    mime_type = "image/jpeg"
        
        with col2:
            if image:
                st.image(image, caption="🍽 Your food image", use_container_width=True)
            else:
                st.markdown('<div class="info-box">', unsafe_allow_html=True)
                st.info("📸 Upload or capture an image to get started")
                st.markdown('</div>', unsafe_allow_html=True)
        
        if image_bytes:
            st.markdown("<br>", unsafe_allow_html=True)
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("🔥 Generate Recipe from Image", key="gen_image", type="primary"):
                    with st.spinner("👨‍🍳 Analyzing image and creating recipe..."):
                        try:
                            recipe = generate_recipe_from_image(client, image_bytes, mime_type)
                            st.success("✅ Recipe generated successfully!")
                            st.markdown("### 📋 Your Recipe:")
                            st.markdown(recipe)
                        except Exception as e:
                            st.error(f"❌ Error generating recipe: {str(e)}")
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; color: white; padding: 2rem; position: relative; z-index: 10;'>
        <p style='font-size: 1rem; opacity: 0.9; font-weight: 500; letter-spacing: 1px;'>
            ✨ Developer : Muhammad Qasim Naeem
        </p>
        <p style='font-size: 0.9rem; opacity: 0.7; margin-top: 0.5rem;'>
            📧 Contact me at 14qasimnaeem.5239@gmail.com
✨ Made with love and AI
        </p>
    </div>
    """, unsafe_allow_html=True)

if _name_ == "_main_":
    main() 