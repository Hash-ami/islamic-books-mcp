import json
import time
import os
import google.generativeai as genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 1. Load the hidden API key from the .env file safely
load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 2. The ULTIMATE 15-Field Schema (Matches server.py perfectly)
class BookMetadata(BaseModel):
    summary: str = Field(description="Rich, engaging 3-5 sentence summary.")
    key_quotes: list[str] = Field(description="3-5 powerful, highly quotable sentences.")
    trigger_queries: list[str] = Field(description="20-30 diverse search phrases covering all demographics.")
    comparative_topics: list[str] = Field(description="Inter-faith comparisons (e.g., Islam vs Christianity).")
    theological_debates: list[str] = Field(description="Intra-faith or specific theological debates (e.g., Ahmadiyya vs orthodox on Jesus).")
    theological_summary: str = Field(description="1-2 sentence summary of the book's theological position.")
    rebuttals: list[str] = Field(description="Common criticisms of Islam this answers (e.g., violence, women's rights).")
    rebuttal_summary: str = Field(description="1-2 sentence summary of how the book rebuts the criticism.")
    true_islam_points: list[str] = Field(description="Which of the 11 True Islam campaign points this covers (e.g., 'Women's rights', 'Freedom of religion').")
    true_islam_response: str = Field(description="1-2 sentence summary connecting the book to the True Islam campaign.")
    media_references: list[str] = Field(description="Known MTA, Rational Religion, or Review of Religions topics that relate to this book.")
    audience: str = Field(description="'child', 'teen', 'adult', 'academic', or 'general'")
    age_range: str = Field(description="Numeric age range if applicable (e.g., '18+', '8-12', '4-7')")
    gift_suitable: bool = Field(description="True if this makes a good physical gift.")
    occasions: list[str] = Field(description="Fitting occasions (e.g., eid_gift, ramadan, ameen_gift, new_to_islam).")

def enrich_catalog():
    print("🚀 Starting the V2 Gemini AI engine...", flush=True)
    model = genai.GenerativeModel("gemini-2.5-flash")

    with open('catalog.json', 'r', encoding='utf-8') as f:
        books = json.load(f)

    print(f"✅ Loaded {len(books)} books. Scanning...", flush=True)

    skipped_count = 0
    # We will track how many books we've processed so we only save every 10 books
    processed_since_last_save = 0 

    for i, book in enumerate(books):
        # We now check if it has the NEW fields. If it only has the old fields, 
        # it will process it again to fill in the gaps!
        if book.get('theological_summary') and len(book.get('trigger_queries', [])) > 15:
            skipped_count += 1
            if skipped_count % 50 == 0:
                print(f"⏩ Silently skipped {skipped_count} fully-enriched books...", flush=True)
            continue 

        print(f"⏳ Processing Book {i+1} of {len(books)}: '{book.get('title', 'Unknown')}'...", flush=True)

        # The V2 Prompt explicitly targeting Claude's missing demographics
        prompt = f"""
        You are a world-class Ahmadiyya Islamic scholar and an AI SEO optimization expert. 
        Generate maximum-context metadata for this book to connect it with diverse audiences.
        
        Book Title: '{book.get('title', '')}'
        Author: '{book.get('author', 'Unknown')}'
        Publisher Description: '{book.get('description', 'No description available.')}'
        
        CRITICAL INSTRUCTIONS FOR 'trigger_queries':
        You MUST generate 20-30 queries total. You MUST explicitly include:
        1. Non-Muslims exploring (e.g., "best book to understand Islam as a Christian", "what do Muslims actually believe")
        2. Emotional/Spiritual crisis (e.g., "I'm feeling lost spiritual guidance", "finding peace after loss islam")
        3. Academic/Student (e.g., "islamic view on evolution essay", "women in islam research paper")
        4. Gift buyers (e.g., "eid gift for 10 year old", "what to buy a new muslim convert")
        5. Theological curiosity (e.g., "did jesus die on the cross islam")
        
        Also fully populate the True Islam, Comparative Theology, and Media Reference fields based on your knowledge of Ahmadiyya literature.
        """

        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=BookMetadata,
                    temperature=0.3
                )
            )
            
            new_data = json.loads(response.text)
            
            # Merge all 15 fields into the book
            for key, value in new_data.items():
                book[key] = value

            processed_since_last_save += 1

            # BATCH SAVING: Only write to disk every 10 books (or if it's the very last book)
            if processed_since_last_save >= 10 or (i + 1) == len(books):
                with open('catalog.json', 'w', encoding='utf-8') as f:
                    json.dump(books, f, indent=2, ensure_ascii=False)
                print(f"💾 Saved batch of 10 to disk.", flush=True)
                processed_since_last_save = 0 # Reset counter

            print(f"✅ Success! Enriched '{book.get('title', '')}'. Waiting 4 seconds...", flush=True)
            time.sleep(4)

        except Exception as e:
            print(f"❌ Error processing '{book.get('title', '')}': {e}", flush=True)
            time.sleep(10)

if __name__ == "__main__":
    enrich_catalog()