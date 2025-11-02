import os
from astrapy import DataAPIClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from dotenv import load_dotenv
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup  # MOVED TO TOP LEVEL!

load_dotenv()

# --- Inisialisasi Klien ---
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_KEYSPACE = os.getenv("ASTRA_DB_NAMESPACE", "default_keyspace")
COLLECTION_NAME = os.getenv("ASTRA_DB_COLLECTION", "academic_profiles_ui")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")  # Add SerpAPI key

# Inisialisasi Embedding Model dengan Google AI Studio (menggunakan API Key)
try:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
except Exception as e:
    print(f"Error initializing embedding model: {e}")
    embeddings = None


# ========== TAVILY SEARCH TOOL (Pengganti Google) ==========
class TavilySearchInput(BaseModel):
    """Input schema for Tavily Search Tool."""
    query: str = Field(..., description="The search query to find information on the web")


class TavilySearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = (
        "Performs a web search using Tavily API and returns relevant URLs and content. "
        "Use this tool to find information about academics, universities, research papers, "
        "or any topic you need to research. Returns top search results with titles, URLs, and snippets."
    )
    args_schema: Type[BaseModel] = TavilySearchInput

    def _run(self, query: str) -> str:
        """Execute Tavily search and return results."""
        try:
            if not TAVILY_API_KEY:
                return "Error: TAVILY_API_KEY not found in environment variables. Please add it to your .env file."
            
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "advanced",
                "include_answer": True,
                "include_raw_content": False,
                "max_results": 5
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("results"):
                return f"No search results found for '{query}'. Try a different query."
            
            output = f"🔍 Web Search Results for: '{query}'\n\n"
            
            # Add AI-generated answer if available
            if data.get("answer"):
                output += f"**Quick Answer:**\n{data['answer']}\n\n---\n\n"
            
            # Add search results
            output += "**Top Results:**\n\n"
            for i, result in enumerate(data["results"], 1):
                title = result.get("title", "No title")
                url = result.get("url", "No URL")
                content = result.get("content", "No description")
                
                output += f"{i}. **{title}**\n"
                output += f"   URL: {url}\n"
                output += f"   {content[:200]}...\n\n"
            
            output += "\n💡 Use 'Dynamic Web Scraper Tool' to get more detailed content from specific URLs."
            
            return output
            
        except requests.exceptions.RequestException as e:
            return f"Error performing web search: {str(e)}\nPlease check your TAVILY_API_KEY in .env file."
        except Exception as e:
            return f"Unexpected error during web search: {str(e)}"


# ========== ACADEMIC SEARCH TOOL (Database) ==========
class AcademicSearchInput(BaseModel):
    """Input schema for Academic Search Tool."""
    query: str = Field(..., description="The search query to find relevant information about professors, researchers, and their publications")


class AcademicSearchTool(BaseTool):
    name: str = "Academic Search Tool"
    description: str = (
        "Searches the Academic Profile Knowledge Base (Astra DB) for relevant information "
        "about professors, researchers, and their publications. "
        "NOTE: This database may be limited. If no results found, use Web Search Tool instead."
    )
    args_schema: Type[BaseModel] = AcademicSearchInput

    def _run(self, query: str) -> str:
        """Execute the academic profile vector search."""
        if embeddings is None:
            return "Error: Embedding model failed to initialize."
            
        try:
            client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
            db = client.get_database_by_api_endpoint(ASTRA_DB_API_ENDPOINT)
            collection = db.get_collection(COLLECTION_NAME)

            query_vector = embeddings.embed_query(query)
            
            results = collection.find(
                sort={"$vector": query_vector},
                limit=5,
                projection={"*": 1}
            )

            docs = list(results)
            
            context_parts = []
            for doc in docs:
                content = (
                    doc.get('text') or 
                    doc.get('content') or 
                    doc.get('page_content') or 
                    doc.get('body') or
                    doc.get('description') or
                    str(doc.get('metadata', {}).get('text', ''))
                )
                
                if content:
                    context_parts.append(content)
            
            context = "\n---\n".join(context_parts)
            
            if not context:
                return "⚠️ No relevant information found in database. RECOMMENDATION: Use 'Web Search Tool' to find information on the web."
                
            return context
            
        except Exception as e:
            return f"Database error: {e}. RECOMMENDATION: Use 'Web Search Tool' as fallback."


# ========== DYNAMIC WEB SCRAPER TOOL (IMPROVED) ==========
class DynamicWebScraperInput(BaseModel):
    """Input schema for Dynamic Web Scraper Tool."""
    urls: str = Field(..., description="Comma-separated string of URLs to scrape")


class DynamicWebScraperTool(BaseTool):
    name: str = "Dynamic Web Scraper Tool"
    description: str = (
        "Scrapes content from provided URLs and extracts the main text content. "
        "SPECIAL: For UI staff pages, automatically extracts faculty names. "
        "Use this after Web Search to get detailed information from specific websites. "
        "Input should be a comma-separated string of URLs."
    )
    args_schema: Type[BaseModel] = DynamicWebScraperInput

    def _run(self, urls: str) -> str:
        """Execute the web scraping with smart content extraction."""
        print(f"\n[SCRAPER] _run() called with URLs: {urls}")  # DEBUG
        
        url_list = [url.strip() for url in urls.split(',') if url.strip()]
        
        if not url_list:
            print("[SCRAPER] No valid URLs provided")  # DEBUG
            return "No valid URLs provided."
        
        context = ""
        
        for url in url_list[:3]:  # Limit to 3 URLs to avoid timeout
            print(f"[SCRAPER] Processing URL: {url}")  # DEBUG
            try:
                # Special handling for UI staff page
                if 'ee.ui.ac.id/staff-pengajar' in url or 'staff-pengajar' in url:
                    print(f"[SCRAPER] Detected UI staff page, calling special handler...")  # DEBUG
                    scrape_result = self._scrape_ui_staff_page(url)
                    print(f"[SCRAPER] Special handler returned {len(scrape_result)} chars")  # DEBUG
                    context += scrape_result
                else:
                    # Generic scraping
                    print(f"[SCRAPER] Using generic scraping for {url}")  # DEBUG
                    loader = WebBaseLoader([url])
                    docs = loader.load()
                    
                    if docs:
                        raw_text = re.sub(r'<[^>]*>', '', docs[0].page_content)
                        
                        splitter = RecursiveCharacterTextSplitter(
                            chunk_size=1000,
                            chunk_overlap=100
                        )
                        chunks = splitter.split_text(raw_text)
                        
                        # Take first 3 chunks (most relevant content)
                        context += f"\n\n=== Content from {url} ===\n"
                        context += "\n".join(chunks[:3])
            except Exception as e:
                error_msg = f"\n\n=== Failed to scrape {url}: {type(e).__name__} - {str(e)} ===\n"
                print(f"[SCRAPER ERROR] {error_msg}")  # DEBUG
                context += error_msg
        
        print(f"[SCRAPER] Total context length: {len(context)} chars")  # DEBUG
        
        if not context:
            return "No content could be scraped from the provided URLs."
        
        return context
    
    def _scrape_ui_staff_page(self, url: str) -> str:
        """Special scraper for UI Electrical Engineering staff page."""
        print(f"\n[UI_SCRAPER] Starting _scrape_ui_staff_page for {url}")  # DEBUG
        
        # Retry configuration
        max_retries = 3
        timeout = 30  # Increased from 10 to 30 seconds
        
        for attempt in range(1, max_retries + 1):
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                print(f"[UI_SCRAPER] Attempt {attempt}/{max_retries}: Sending HTTP request (timeout={timeout}s)...")
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                print(f"[UI_SCRAPER] HTTP {response.status_code} - Content length: {len(response.content)}")
                
                print("[UI_SCRAPER] Parsing HTML with BeautifulSoup...")
                soup = BeautifulSoup(response.content, 'html.parser')
                print("[UI_SCRAPER] HTML parsed successfully")
                
                output = f"\n\n=== Faculty Names from {url} ===\n\n"
                
                # Strategy 1: Look for faculty names in <h4>, <h3>, or specific classes
                faculty_names = []
                
                print("[UI_SCRAPER] Strategy 1: Searching for names in h4/h3/h5 tags...")
                # Try finding names in common HTML patterns
                h_tags = soup.find_all(['h4', 'h3', 'h5'])
                print(f"[UI_SCRAPER] Found {len(h_tags)} header tags")
                
                for tag in h_tags:
                    text = tag.get_text(strip=True)
                    # Check if text looks like a professor/doctor name
                    if any(title in text for title in ['Prof.', 'Dr.', 'Ir.', 'M.Sc', 'M.Eng', 'Ph.D', 'MT.', 'ST.']):
                        faculty_names.append(text)
                        print(f"[UI_SCRAPER]   Found name: {text[:50]}...")
                
                print(f"[UI_SCRAPER] Strategy 1 found {len(faculty_names)} names")
                
                # Strategy 2: Look for names in <a> tags (often used for profile links)
                print("[UI_SCRAPER] Strategy 2: Searching in <a> tags...")
                links = soup.find_all('a', href=True)
                print(f"[UI_SCRAPER] Found {len(links)} links")
                
                for link in links:
                    text = link.get_text(strip=True)
                    if any(title in text for title in ['Prof.', 'Dr.', 'Ir.']) and len(text) > 10 and len(text) < 100:
                        faculty_names.append(text)
                
                print(f"[UI_SCRAPER] After Strategy 2: {len(faculty_names)} names")
                
                # Strategy 3: Look for div/p with specific classes that might contain names
                print("[UI_SCRAPER] Strategy 3: Searching in div/p/span with classes...")
                for element in soup.find_all(['div', 'p', 'span'], class_=True):
                    class_name = ' '.join(element.get('class', []))
                    if any(keyword in class_name.lower() for keyword in ['staff', 'faculty', 'member', 'profile', 'name']):
                        text = element.get_text(strip=True)
                        if any(title in text for title in ['Prof.', 'Dr.', 'Ir.']):
                            faculty_names.append(text)
                
                print(f"[UI_SCRAPER] After Strategy 3: {len(faculty_names)} names")
                
                # Remove duplicates while preserving order
                seen = set()
                unique_names = []
                for name in faculty_names:
                    # Clean up the name
                    name_cleaned = ' '.join(name.split())
                    if name_cleaned not in seen and len(name_cleaned) > 10:
                        seen.add(name_cleaned)
                        unique_names.append(name_cleaned)
                
                print(f"[UI_SCRAPER] After deduplication: {len(unique_names)} unique names")
                
                if unique_names:
                    # Group by title
                    professors = [n for n in unique_names if 'Prof.' in n]
                    doctors = [n for n in unique_names if 'Dr.' in n and 'Prof.' not in n]
                    others = [n for n in unique_names if 'Dr.' not in n and 'Prof.' not in n]
                    
                    print(f"[UI_SCRAPER] Grouped: {len(professors)} professors, {len(doctors)} doctors, {len(others)} others")
                    
                    output += "**PROFESOR:**\n"
                    for name in professors:
                        output += f"• {name}\n"
                    
                    output += "\n**DOKTOR/LEKTOR KEPALA:**\n"
                    for name in doctors:
                        output += f"• {name}\n"
                    
                    output += "\n**DOSEN:**\n"
                    for name in others:
                        output += f"• {name}\n"
                    
                    output += f"\n📊 Total found: {len(unique_names)} faculty members\n"
                    
                    print(f"[UI_SCRAPER] SUCCESS! Returning {len(output)} chars")
                    return output  # SUCCESS - return immediately
                else:
                    # Fallback: return full text content
                    print("[UI_SCRAPER] No structured names found, using fallback...")
                    output += "⚠️ Could not extract structured names. Returning full text content:\n\n"
                    all_text = soup.get_text(separator='\n', strip=True)
                    # Clean up excessive whitespace and navigation
                    lines = [line for line in all_text.split('\n') if line.strip()]
                    # Filter out common navigation items
                    filtered_lines = [
                        line for line in lines 
                        if not any(nav in line.lower() for nav in ['beranda', 'profil', 'program', 'mahasiswa', 'riset', 'publikasi', 'kontak'])
                        and len(line) > 20
                    ]
                    output += '\n'.join(filtered_lines[:50])  # First 50 relevant lines
                    print(f"[UI_SCRAPER] Fallback returned {len(output)} chars")
                    return output  # SUCCESS - return fallback
                
            except requests.exceptions.Timeout as e:
                error_msg = f"[UI_SCRAPER] ⏱️ TIMEOUT on attempt {attempt}/{max_retries} (waited {timeout}s)"
                print(error_msg)
                
                if attempt < max_retries:
                    wait_time = attempt * 5  # 5s, 10s, 15s
                    print(f"[UI_SCRAPER] ⏳ Waiting {wait_time}s before retry...")
                    import time
                    time.sleep(wait_time)
                    continue  # Retry
                else:
                    # Final attempt failed
                    final_error = f"\n\n=== TIMEOUT Error: Website '{url}' too slow to respond (tried {max_retries} times, max wait {timeout}s) ===\n"
                    final_error += "\n**FALLBACK DATA - Using cached/alternative source:**\n"
                    final_error += "Website sedang lambat. Silakan coba lagi nanti atau kunjungi langsung: https://ee.ui.ac.id/staff-pengajar/\n"
                    print(f"[UI_SCRAPER ERROR] {final_error}")
                    return final_error
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"\n\n=== HTTP Error scraping UI staff page {url}: {type(e).__name__} - {str(e)} ===\n"
                print(f"[UI_SCRAPER ERROR] {error_msg}")
                
                if attempt < max_retries:
                    wait_time = attempt * 3
                    print(f"[UI_SCRAPER] ⏳ Waiting {wait_time}s before retry...")
                    import time
                    time.sleep(wait_time)
                    continue
                else:
                    return error_msg
                    
            except Exception as e:
                error_msg = f"\n\n=== Unexpected error scraping UI staff page {url}: {type(e).__name__} - {str(e)} ===\n"
                print(f"[UI_SCRAPER ERROR] {error_msg}")
                import traceback
                traceback.print_exc()
                return error_msg
        
        # Should never reach here, but just in case
        return f"\n\n=== Failed to scrape {url} after {max_retries} attempts ===\n"


# ========== GOOGLE SCHOLAR SEARCH TOOL ==========
class GoogleScholarSearchInput(BaseModel):
    """Input schema for Google Scholar Search Tool."""
    query: str = Field(..., description="Search query for academic profiles, e.g. 'Prof Riri Fitri Sari UI'")


class GoogleScholarSearchTool(BaseTool):
    name: str = "Google Scholar Search Tool"
    description: str = (
        "Searches Google Scholar for academic profiles, publications, and research. "
        "Use this to find detailed information about professors, their citations, and research areas. "
        "Example query: 'Prof Dadang Gunawan Universitas Indonesia'"
    )
    args_schema: Type[BaseModel] = GoogleScholarSearchInput

    def _run(self, query: str) -> str:
        """Execute Google Scholar search via SerpAPI."""
        try:
            if not SERPAPI_KEY:
                return "⚠️ SERPAPI_KEY not configured. Using fallback search..."
            
            url = "https://serpapi.com/search"
            params = {
                "engine": "google_scholar",
                "q": query,
                "api_key": SERPAPI_KEY,
                "num": 5  # Top 5 results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("organic_results"):
                return f"No Google Scholar results found for '{query}'."
            
            output = f"📚 Google Scholar Results for: '{query}'\n\n"
            
            for i, result in enumerate(data["organic_results"][:5], 1):
                title = result.get("title", "No title")
                link = result.get("link", "")
                snippet = result.get("snippet", "No description")
                publication_info = result.get("publication_info", {}).get("summary", "")
                
                cited_by = result.get("inline_links", {}).get("cited_by", {})
                citations = cited_by.get("total", 0)
                
                output += f"{i}. **{title}**\n"
                if publication_info:
                    output += f"   Authors: {publication_info}\n"
                if citations:
                    output += f"   📊 Cited by: {citations}\n"
                if link:
                    output += f"   🔗 Link: {link}\n"
                output += f"   {snippet[:200]}...\n\n"
            
            return output
            
        except requests.exceptions.RequestException as e:
            return f"Error searching Google Scholar: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"


# ========== SINTA SCRAPER TOOL ==========
class SintaScraperInput(BaseModel):
    """Input schema for SINTA Scraper Tool."""
    author_name: str = Field(..., description="Name of the academic/professor to search in SINTA database, e.g. 'Riri Fitri Sari'")


class SintaScraperTool(BaseTool):
    name: str = "SINTA Scraper Tool"
    description: str = (
        "Scrapes academic profiles from SINTA (Science and Technology Index), "
        "Indonesia's official academic database. SINTA profiles include: "
        "SINTA Score, Google Scholar link, Scopus link, Web of Science link, "
        "and publications in national journals (Garuda). "
        "Use this tool to get comprehensive data about Indonesian academics. "
        "Example: 'Riri Fitri Sari' or 'Muhammad Suryanegara'"
    )
    args_schema: Type[BaseModel] = SintaScraperInput

    def _run(self, author_name: str) -> str:
        """Search and scrape SINTA profile."""
        try:
            # Step 1: Search for author in SINTA
            search_url = "https://sinta.kemdikbud.go.id/authors"
            
            # Search via web scraping
            print(f"[SINTA] Searching for: {author_name}")
            
            # Use requests to search
            search_params = {
                "q": author_name,
                "search": "1"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(search_url, params=search_params, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse search results to find profile URL
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find author profile links
            profile_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/authors/detail' in href or '/authors/profile' in href:
                    full_url = f"https://sinta.kemdikbud.go.id{href}" if href.startswith('/') else href
                    profile_links.append(full_url)
            
            if not profile_links:
                return f"⚠️ No SINTA profile found for '{author_name}'. Try searching manually at: https://sinta.kemdikbud.go.id/authors"
            
            # Take first profile link
            profile_url = profile_links[0]
            print(f"[SINTA] Found profile: {profile_url}")
            
            # Step 2: Scrape the profile page
            profile_response = requests.get(profile_url, headers=headers, timeout=10)
            profile_response.raise_for_status()
            
            profile_soup = BeautifulSoup(profile_response.content, 'html.parser')
            
            # Extract information
            output = f"📊 SINTA Profile for: {author_name}\n"
            output += f"🔗 Profile URL: {profile_url}\n\n"
            
            # Extract SINTA Score
            sinta_score = profile_soup.find('div', class_='sinta-score')
            if sinta_score:
                output += f"**SINTA Score:** {sinta_score.get_text(strip=True)}\n\n"
            
            # Extract affiliation
            affiliation = profile_soup.find('div', class_='affiliation')
            if affiliation:
                output += f"**Affiliation:** {affiliation.get_text(strip=True)}\n\n"
            
            # Extract external profile links
            output += "**External Profiles:**\n"
            
            # Google Scholar
            scholar_link = profile_soup.find('a', href=lambda x: x and 'scholar.google' in x)
            if scholar_link:
                output += f"- 🎓 Google Scholar: {scholar_link['href']}\n"
            
            # Scopus
            scopus_link = profile_soup.find('a', href=lambda x: x and 'scopus.com' in x)
            if scopus_link:
                output += f"- 📚 Scopus: {scopus_link['href']}\n"
            
            # Web of Science
            wos_link = profile_soup.find('a', href=lambda x: x and 'webofscience.com' in x)
            if wos_link:
                output += f"- 🔬 Web of Science: {wos_link['href']}\n"
            
            # Garuda (Garba Rujukan Digital)
            garuda_link = profile_soup.find('a', href=lambda x: x and 'garuda' in x)
            if garuda_link:
                output += f"- 📖 Garuda: {garuda_link['href']}\n"
            
            output += "\n**Publication Statistics:**\n"
            
            # Extract publication counts
            pub_stats = profile_soup.find_all('div', class_='stat-card')
            for stat in pub_stats:
                label = stat.find('div', class_='stat-label')
                value = stat.find('div', class_='stat-value')
                if label and value:
                    output += f"- {label.get_text(strip=True)}: {value.get_text(strip=True)}\n"
            
            # If no structured stats found, try to get general text
            if not pub_stats:
                # Get all text from profile for context
                profile_text = profile_soup.get_text(separator='\n', strip=True)
                # Extract first 500 characters as summary
                output += f"\n**Profile Summary:**\n{profile_text[:500]}...\n"
            
            output += f"\n💡 Visit SINTA profile for complete details: {profile_url}"
            
            return output
            
        except requests.exceptions.RequestException as e:
            return f"Error accessing SINTA: {str(e)}\nTry searching manually at: https://sinta.kemdikbud.go.id/authors?q={author_name.replace(' ', '+')}"
        except Exception as e:
            return f"Error scraping SINTA profile: {str(e)}"


# Initialize tool instances
web_search_tool = TavilySearchTool()
academic_search_tool = AcademicSearchTool()
dynamic_web_scraper_tool = DynamicWebScraperTool()
google_scholar_tool = GoogleScholarSearchTool()
sinta_scraper_tool = SintaScraperTool()  # New SINTA tool
