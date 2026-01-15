# 💄 Shivani's Cosmetics Advisor AI (Streamlit + Voice + Azure OpenAI)

This project is a **Streamlit web app** that acts as an AI-powered **cosmetics advisor**.  
It supports **voice input**, **text chat**, and integrates with **Azure OpenAI**, **MySQL database**, and **Google Text-to-Speech (gTTS)** to provide intelligent product recommendations.  

---

## 🚀 Features  
- 🎤 **Voice Input**: Speak queries using `streamlit-mic-recorder`.  
- ⌨️ **Text Input**: Type queries if microphone not available.  
- 🤖 **AI-Powered Responses**: Uses **Azure OpenAI (Chat Completions)** to analyze product catalog and suggest best matches.  
- 🗄️ **MySQL Integration**: Fetches real product data (name, brand, shade, price, stock).  
- 🔊 **Text-to-Speech (TTS)**: Reads AI responses aloud using **gTTS**.  
- 📜 **Chat History**: Maintains conversational history inside Streamlit session.  

---

## ⚙️ Requirements  

### Python Packages  
Install dependencies:  
```bash
pip install streamlit mysql-connector-python openai gTTS streamlit-mic-recorder SpeechRecognition pydub
```

### External Tools  
- **FFmpeg** is required for audio conversion (pydub).  
  - [Download FFmpeg](https://ffmpeg.org/download.html) and add it to your PATH.  
  - Or set the converter path in code:  
    ```python
    AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"
    ```

### Azure OpenAI Setup  
Set environment variables:  
```bash
export AZURE_OPENAI_KEY="your_api_key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="your_deployment_name"
```

### MySQL Setup  
Create a database `cosmetics_db` with a `products` table:  

```sql
CREATE DATABASE cosmetics_db;
USE cosmetics_db;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    brand VARCHAR(50),
    shade VARCHAR(50),
    category VARCHAR(50),
    price INT,
    stock INT
);

-- Sample data
INSERT INTO products (name, brand, shade, category, price, stock) VALUES
("Red Matte Lipstick", "Lakme", "Red Velvet", "lipstick", 450, 10),
("Hydrating Aloe Cream", "Himalaya", "Green", "cream", 600, 8),
("Matte Foundation", "Maybelline", "Beige", "foundation", 1200, 5),
("Luxury Perfume", "Chanel", "Floral", "perfume", 2500, 3);
```

Update DB password in code:  
```python
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="cosmetics_db"
)
```

---

## ▶️ Running the App  

Run the Streamlit app:  
```bash
streamlit run app.py
```

Then open:  
👉 [http://localhost:8501](http://localhost:8501)  

---

## 🌐 How It Works  

1. User speaks or types a query.  
2. Voice input is converted to text using **SpeechRecognition + Google Speech API**.  
3. The query is passed to **Azure OpenAI** along with product data from **MySQL**.  
4. AI suggests suitable products with reasoning.  
5. The response is displayed on screen and also read aloud via **gTTS**.  

---

## 📜 Example Interaction  

**You (voice/text):**  
*"Suggest a good lipstick under 500."*  

**AI Response:**  
*"Based on your request, I recommend Lakme Red Matte Lipstick (₹450). It has long-lasting color and fits within your budget."*  

🔊 The AI also **speaks** this recommendation.  

---

## 🔧 Customization  
- Modify **categories/fields** in MySQL for your product catalog.  
- Replace gTTS with **Azure TTS** for higher-quality voices.  
- Add **multilingual support** by changing recognition/tts languages.  
# Cosmetics_AI
Ai chatbot and telecalling of cosmetics product where the user can purchase the product according to their skin type  and ask any questions related to cosmetics .It also provides the prduct data and their price
