import json
import re
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException

def _analyze_document_structure(soup: BeautifulSoup) -> dict:
    """
    Analyzes the HTML soup to identify document structure, create an outline,
    extract key phrases, and classify the content type.
    """
    # 1. Heading Hierarchy Detection & Document Outline Generation
    document_outline = []
    for i in range(1, 7):
        for heading in soup.find_all(f'h{i}'):
            if heading.get_text(strip=True):
                document_outline.append({'level': i, 'text': heading.get_text(strip=True)})

    # 2. Key Phrase Extraction (Heuristic Approach)
    key_phrases = set()
    # Extract text from emphasized tags (bold, italic)
    for tag in soup.find_all(['strong', 'b', 'em', 'i']):
        key_phrases.add(tag.get_text(strip=True).lower())
    # Extract from meta keywords
    keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
    if keywords_tag and keywords_tag.get('content'):
        keywords = [k.strip().lower() for k in keywords_tag.get('content').split(',')]
        key_phrases.update(keywords)
    
    # 3. Content Type Classification (Heuristic)
    content_type = 'Generic Page'
    if soup.find('article'):
        content_type = 'Article/Blog Post'
    # Check for e-commerce patterns in structured data
    for script_tag in soup.find_all('script', type='application/ld+json'):
        try:
            if script_tag.string:
                data = json.loads(script_tag.string)
                if data.get('@type') in ['Product', 'Offer', 'ItemPage']:
                    content_type = 'Product/E-commerce Page'
                    break
        except Exception:
            continue

    return {
        'document_outline': document_outline,
        'key_phrases': sorted(list(key_phrases)),
        'content_type': content_type
    }

def _process_text_pipeline(raw_text: str) -> dict:
    """
    An advanced text processing pipeline that cleans, normalizes,
    and prepares content for AI analysis.
    """
    text = re.sub(r'\s+', ' ', raw_text).strip()
    text = "".join(filter(lambda char: char.isprintable(), text))
    lines = (line.strip() for line in text.splitlines())
    text = "\n".join(line for line in lines if len(line.split()) > 3)
    detected_language = 'unknown'
    try:
        if text:
            detected_language = detect(text[:500])
    except LangDetectException:
        print("Language detection failed.")
    return {'cleaned_text': text, 'detected_language': detected_language}

def extract_and_clean_content(html_content: str) -> dict:
    """
    Main function to extract, process, and analyze content from raw HTML.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # --- Step 1: Perform document structure analysis ---
    structure_analysis = _analyze_document_structure(soup)

    # --- Step 2: Extract and clean main text content ---
    title = soup.title.string.strip() if soup.title else None
    description_tag = soup.find('meta', attrs={'name': 'description'})
    meta_description = description_tag.get('content', '').strip() if description_tag else None
    
    main_content_area = soup.find('article') or soup.find('main') or soup.body
    if main_content_area:
        for element in main_content_area(['nav', 'header', 'footer', 'aside', 'script', 'style']):
            element.decompose()
    
    raw_text = main_content_area.get_text(separator=' ', strip=True) if main_content_area else ""
    processed_text_data = _process_text_pipeline(raw_text)

    # --- Step 3: Assemble the final output ---
    final_output = {
        "title": title,
        "meta_description": meta_description,
        "main_content_text": processed_text_data['cleaned_text'],
        "detected_language": processed_text_data['detected_language']
    }
    # Merge the structure analysis results into the final dictionary
    final_output.update(structure_analysis)
    
    return final_output