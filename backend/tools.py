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
from bs4 import BeautifulSoup
import sinta  # Fixed: was 'import sinta_scraper'

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
            
            # DYNAMIC LIMIT: Adjust based on query type
            # For "list all" queries, get MORE results to ensure completeness
            limit = 50  # Default: increased to 50 for comprehensive results
            
            results = collection.find(
                sort={"$vector": query_vector},
                limit=limit,
                projection={"*": 1}
            )

            docs = list(results)
            
            print(f"[ACADEMIC_SEARCH] Query: {query}")
            print(f"[ACADEMIC_SEARCH] Found {len(docs)} documents")
            
            context_parts = []
            for idx, doc in enumerate(docs):
                content = (
                    doc.get('text') or 
                    doc.get('content') or 
                    doc.get('page_content') or 
                    doc.get('body') or
                    doc.get('description') or
                    str(doc.get('metadata', {}).get('text', ''))
                )
                
                if content:
                    source_url = doc.get('source_url', 'Unknown')
                    print(f"[ACADEMIC_SEARCH]   [{idx+1}] {len(content)} chars from {source_url[:50]}...")
                    context_parts.append(content)
            
            context = "\n---\n".join(context_parts)
            
            if not context:
                return "⚠️ No relevant information found in database. RECOMMENDATION: Use 'Web Search Tool' to find information on the web."
            
            print(f"[ACADEMIC_SEARCH] Total context: {len(context)} characters")
            return context
            
        except Exception as e:
            print(f"[ACADEMIC_SEARCH ERROR] {e}")
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


# ========== GOOGLE SCHOLAR TOOLS (SerpAPI) ==========

class ScholarProfilesSearchInput(BaseModel):
    """Input schema for Google Scholar Profiles Search Tool."""
    query: str = Field(..., description="Search query for finding academic profiles (e.g., 'Riri Fitri Sari', 'UI Electrical Engineering professor')")


class GoogleScholarProfilesSearchTool(BaseTool):
    name: str = "Google Scholar Profiles Search"
    description: str = (
        "Search for academic profiles on Google Scholar by name, affiliation, or research area. "
        "Use this to find professor profiles, their Google Scholar IDs, affiliations, and email addresses. "
        "Returns a list of matching profiles with their basic information and citation counts."
    )
    args_schema: Type[BaseModel] = ScholarProfilesSearchInput

    def _run(self, query: str) -> str:
        """Search for Google Scholar profiles."""
        try:
            if not SERPAPI_KEY:
                return "❌ Error: SERPAPI_KEY not found. Please add it to your .env file to use Google Scholar features."
            
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "google_scholar_profiles",
                "mauthors": query,
                "api_key": SERPAPI_KEY,
                "hl": "en"
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            profiles = data.get("profiles", [])
            
            if not profiles:
                return f"❌ No Google Scholar profiles found for '{query}'. Try different keywords or check spelling."
            
            output = f"🎓 **Google Scholar Profiles for: '{query}'**\n\n"
            output += f"Found {len(profiles)} profile(s):\n\n"
            
            for i, profile in enumerate(profiles[:10], 1):  # Limit to 10 results
                name = profile.get("name", "Unknown")
                author_id = profile.get("author_id", "")
                affiliations = profile.get("affiliations", "No affiliation listed")
                email = profile.get("email", "No email")
                cited_by = profile.get("cited_by", 0)
                interests = profile.get("interests", [])
                
                output += f"{i}. **{name}**\n"
                output += f"   📧 {email}\n"
                output += f"   🏛️ {affiliations}\n"
                output += f"   📊 Citations: {cited_by:,}\n"
                
                if interests:
                    output += f"   🔬 Research: {', '.join(interests[:3])}\n"
                
                output += f"   🔑 Author ID: `{author_id}`\n"
                output += f"   💡 Use 'Google Scholar Author Profile Tool' with this ID to get full details\n\n"
            
            return output
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error searching Google Scholar profiles: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"


class ScholarAuthorProfileInput(BaseModel):
    """Input schema for Google Scholar Author Profile Tool."""
    author_id: str = Field(..., description="Google Scholar author ID (e.g., 'LSsXyncAAAAJ')")


class GoogleScholarAuthorProfileTool(BaseTool):
    name: str = "Google Scholar Author Profile Tool"
    description: str = (
        "Get complete profile details for a specific Google Scholar author using their author_id. "
        "Returns comprehensive information including: full name, affiliation, all publications, "
        "citation metrics (h-index, i10-index), citation graph, co-authors, and research interests. "
        "Use this after finding an author_id from 'Google Scholar Profiles Search'."
    )
    args_schema: Type[BaseModel] = ScholarAuthorProfileInput

    def _run(self, author_id: str) -> str:
        """Get detailed Google Scholar author profile."""
        try:
            if not SERPAPI_KEY:
                return "❌ Error: SERPAPI_KEY not found. Please add it to your .env file."
            
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "google_scholar_author",
                "author_id": author_id,
                "api_key": SERPAPI_KEY,
                "hl": "en",
                "num": 100  # Get up to 100 publications
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Extract author info
            author = data.get("author", {})
            articles = data.get("articles", [])
            cited_by = data.get("cited_by", {})
            co_authors = data.get("co_authors", [])
            
            if not author:
                return f"❌ No profile found for author_id: {author_id}"
            
            # Build comprehensive output
            output = f"👤 **Google Scholar Author Profile**\n\n"
            output += f"**Name:** {author.get('name', 'Unknown')}\n"
            output += f"**Affiliation:** {author.get('affiliations', 'Not listed')}\n"
            output += f"**Email:** {author.get('email', 'Not listed')}\n"
            
            # Research interests
            interests = author.get("interests", [])
            if interests:
                interest_names = [i.get("title") for i in interests if i.get("title")]
                output += f"**Research Interests:** {', '.join(interest_names[:5])}\n"
            
            # Citation metrics
            output += f"\n📊 **Citation Metrics:**\n"
            table = cited_by.get("table", [])
            for metric in table:
                for key, value in metric.items():
                    metric_name = key.replace('_', ' ').title()
                    all_time = value.get("all", 0)
                    since_2016 = value.get("since_2016", 0)
                    output += f"   • {metric_name}: {all_time:,} (since 2016: {since_2016:,})\n"
            
            # Top publications
            output += f"\n📚 **Publications (Top 10):**\n"
            for i, article in enumerate(articles[:10], 1):
                title = article.get("title", "No title")
                authors = article.get("authors", "Unknown authors")
                year = article.get("year", "N/A")
                cited = article.get("cited_by", {}).get("value", 0)
                
                output += f"\n{i}. **{title}** ({year})\n"
                output += f"   Authors: {authors[:100]}{'...' if len(authors) > 100 else ''}\n"
                output += f"   Citations: {cited:,}\n"
            
            if len(articles) > 10:
                output += f"\n   ... and {len(articles) - 10} more publications\n"
            
            output += f"\n**Total Publications:** {len(articles)}\n"
            
            # Co-authors
            if co_authors:
                output += f"\n👥 **Frequent Co-authors:**\n"
                for i, coauthor in enumerate(co_authors[:5], 1):
                    co_name = coauthor.get("name", "Unknown")
                    co_affil = coauthor.get("affiliations", "")
                    output += f"   {i}. {co_name} - {co_affil}\n"
            
            return output
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error fetching author profile: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"


class ScholarPublicationsSearchInput(BaseModel):
    """Input schema for Google Scholar Publications Search Tool."""
    query: str = Field(..., description="Search query for finding academic papers (e.g., 'machine learning UI', 'wireless networks Indonesia')")


class GoogleScholarPublicationsSearchTool(BaseTool):
    name: str = "Google Scholar Publications Search"
    description: str = (
        "Search for academic papers and publications on Google Scholar. "
        "Returns paper titles, authors, publication info, citation counts, and PDF links if available. "
        "Use this to find research papers, verify publications, or explore research topics."
    )
    args_schema: Type[BaseModel] = ScholarPublicationsSearchInput

    def _run(self, query: str) -> str:
        """Search for publications on Google Scholar."""
        try:
            if not SERPAPI_KEY:
                return "❌ Error: SERPAPI_KEY not found. Please add it to your .env file."
            
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "google_scholar",
                "q": query,
                "api_key": SERPAPI_KEY,
                "hl": "en",
                "num": 20  # Get 20 results
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            organic_results = data.get("organic_results", [])
            
            if not organic_results:
                return f"❌ No publications found for '{query}'. Try different keywords."
            
            output = f"📄 **Google Scholar Publications: '{query}'**\n\n"
            output += f"Found {len(organic_results)} result(s):\n\n"
            
            for i, result in enumerate(organic_results[:10], 1):
                title = result.get("title", "No title")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                
                # Publication info
                pub_info = result.get("publication_info", {})
                summary = pub_info.get("summary", "")
                
                # Citation info
                inline_links = result.get("inline_links", {})
                cited_by = inline_links.get("cited_by", {})
                citations = cited_by.get("total", 0)
                
                # Resources (PDF links)
                resources = result.get("resources", [])
                
                output += f"{i}. **{title}**\n"
                
                if summary:
                    output += f"   📝 {summary}\n"
                
                if snippet:
                    snippet_short = snippet[:150] + "..." if len(snippet) > 150 else snippet
                    output += f"   💬 {snippet_short}\n"
                
                if citations:
                    output += f"   📊 Cited by: {citations:,}\n"
                
                if resources:
                    pdf_links = [r.get("link") for r in resources if r.get("file_format") == "PDF"]
                    if pdf_links:
                        output += f"   📥 PDF: {pdf_links[0]}\n"
                
                if link:
                    output += f"   🔗 {link}\n"
                
                output += "\n"
            
            return output
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error searching publications: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"


class ScholarCitedByInput(BaseModel):
    """Input schema for Google Scholar Cited By Tool."""
    cluster_id: str = Field(..., description="Google Scholar cluster ID of the paper to get citations for")


class GoogleScholarCitedByTool(BaseTool):
    name: str = "Google Scholar Cited By Tool"
    description: str = (
        "Get papers that cite a specific research paper using its Google Scholar cluster_id. "
        "Returns a list of citing papers with titles, authors, publication info, and citation counts. "
        "Use this to analyze citation networks and see who is building on specific research. "
        "The cluster_id can be found in the 'cited_by' link from publication search results."
    )
    args_schema: Type[BaseModel] = ScholarCitedByInput

    def _run(self, cluster_id: str) -> str:
        """Get papers that cite a specific work."""
        try:
            if not SERPAPI_KEY:
                return "❌ Error: SERPAPI_KEY not found. Please add it to your .env file."
            
            url = "https://serpapi.com/search.json"
            params = {
                "engine": "google_scholar",
                "cites": cluster_id,
                "api_key": SERPAPI_KEY,
                "hl": "en",
                "num": 20
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            organic_results = data.get("organic_results", [])
            
            if not organic_results:
                return f"❌ No citing papers found for cluster_id: {cluster_id}"
            
            # Get search info
            search_info = data.get("search_information", {})
            total_results = search_info.get("total_results", "Unknown")
            
            output = f"📊 **Papers Citing This Work**\n\n"
            output += f"**Total Citations:** {total_results}\n"
            output += f"**Showing:** Top {len(organic_results)} papers\n\n"
            
            for i, result in enumerate(organic_results[:10], 1):
                title = result.get("title", "No title")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                
                # Publication info
                pub_info = result.get("publication_info", {})
                summary = pub_info.get("summary", "")
                
                # Citation info
                inline_links = result.get("inline_links", {})
                cited_by = inline_links.get("cited_by", {})
                citations = cited_by.get("total", 0)
                
                output += f"{i}. **{title}**\n"
                
                if summary:
                    output += f"   📝 {summary}\n"
                
                if snippet:
                    snippet_short = snippet[:150] + "..." if len(snippet) > 150 else snippet
                    output += f"   💬 {snippet_short}\n"
                
                if citations:
                    output += f"   📊 Cited by: {citations:,}\n"
                
                if link:
                    output += f"   🔗 {link}\n"
                
                output += "\n"
            
            return output
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error fetching citing papers: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"


# ========== SINTA TOOL REMOVED ==========
# SINTA scraper was unreliable and error-prone.
# Use UI Scholar (scholar.ui.ac.id) instead for UI faculty data.
# Use Google Scholar tools for general academic metrics.

# ========== CV GENERATOR TOOL ==========
class CVGeneratorInput(BaseModel):
    """Input schema for CV Generator Tool."""
    professor_name: str = Field(..., description="Full name of the professor/lecturer to generate CV for")


class CVGeneratorTool(BaseTool):
    name: str = "CV Generator Tool"
    description: str = (
        "Generates a professional academic Curriculum Vitae (CV) in PDF format for a specific professor or lecturer. "
        "This tool MUST be used when user explicitly asks to 'generate CV', 'create CV', 'make CV', or 'download CV'. "
        "The tool will automatically gather all available information from database, SINTA, and Google Scholar "
        "to create a comprehensive CV document. "
        "Input: professor_name (e.g., 'Prof. Dr. Riri Fitri Sari' or 'Muhammad Suryanegara')"
    )
    args_schema: Type[BaseModel] = CVGeneratorInput

    def _run(self, professor_name: str) -> str:
        """Generate CV by collecting comprehensive data about the professor."""
        print(f"\n[CV_GENERATOR] Starting CV generation for: {professor_name}")
        
        collected_data = []
        
        # Step 1: Search database
        print("[CV_GENERATOR] Step 1/4: Searching database...")
        try:
            db_result = academic_search_tool._run(professor_name)
            if db_result and "No relevant information" not in db_result:
                collected_data.append(f"=== DATABASE INFO ===\n{db_result}")
                print(f"  ✓ Database: {len(db_result)} chars")
        except Exception as e:
            print(f"  ✗ Database error: {e}")
        
        # Step 2: Search SINTA
        print("[CV_GENERATOR] Step 2/4: Searching SINTA...")
        try:
            sinta_result = sinta_scraper_tool._run(professor_name)
            if sinta_result and "Error" not in sinta_result and "No SINTA profile" not in sinta_result:
                collected_data.append(f"=== SINTA PROFILE ===\n{sinta_result}")
                print(f"  ✓ SINTA: {len(sinta_result)} chars")
        except Exception as e:
            print(f"  ✗ SINTA error: {e}")
        
        # Step 3: Search Google Scholar
        print("[CV_GENERATOR] Step 3/4: Searching Google Scholar...")
        try:
            scholar_result = google_scholar_tool._run(professor_name)
            if scholar_result and "Error" not in scholar_result and "No Google Scholar" not in scholar_result:
                collected_data.append(f"=== GOOGLE SCHOLAR ===\n{scholar_result}")
                print(f"  ✓ Scholar: {len(scholar_result)} chars")
        except Exception as e:
            print(f"  ✗ Scholar error: {e}")
        
        # Step 4: Web search for additional info
        print("[CV_GENERATOR] Step 4/4: Web search for additional information...")
        try:
            web_result = web_search_tool._run(f"{professor_name} Universitas Indonesia publications research")
            if web_result and len(web_result) > 100:
                collected_data.append(f"=== WEB SEARCH ===\n{web_result[:1500]}")
                print(f"  ✓ Web: {len(web_result)} chars")
        except Exception as e:
            print(f"  ✗ Web error: {e}")
        
        if not collected_data:
            return f"❌ CV Generation Failed: No data found for '{professor_name}'. Please try a different name or check if the professor exists in the database."
        
        # Combine all data
        full_profile = "\n\n".join(collected_data)
        
        print(f"[CV_GENERATOR] ✓ Collected {len(full_profile)} characters of data")
        print(f"[CV_GENERATOR] CV data ready for PDF generation")
        
        # Return structured message for agent
        return f"""✅ CV DATA COLLECTED SUCCESSFULLY FOR: {professor_name}

📊 Data Sources Used:
{len(collected_data)} sources compiled

📄 CV Generation Status: READY

The CV will be automatically generated when user clicks the download button.

Would you like me to summarize the key information I found about {professor_name}?

Profile Data Preview:
{full_profile[:500]}...

[Note: Full CV with all details will be available in the PDF download]
"""


# ========== UI SCHOLAR SEARCH TOOL (NEW!) ==========
class UIScholarSearchInput(BaseModel):
    """Input schema for UI Scholar Search Tool."""
    query: str = Field(..., description="Search query for publications (e.g., 'Riri Fitri Sari publications', 'computer networks research UI', 'IoT publications')")


class UIScholarSearchTool(BaseTool):
    name: str = "UI Scholar Publication Search"
    description: str = (
        "Searches scholar.ui.ac.id (Universitas Indonesia's official research publication database) "
        "for academic papers, research, and publications from UI faculty and researchers. "
        "This is the PRIMARY source for finding publications from UI Electrical Engineering department. "
        "Use this when user asks about: publications, papers, research output, scientific articles. "
        "Returns: paper titles, authors, publication year, journal/conference names, and links."
    )
    args_schema: Type[BaseModel] = UIScholarSearchInput

    def _run(self, query: str) -> str:
        """Search UI Scholar - UPDATED: Now uses direct person URL to avoid 403 errors."""
        print(f"\n[UI_SCHOLAR] Searching for: '{query}'")
        
        # NEW STRATEGY: Try to extract person name and use direct URL
        person_name = self._extract_person_name(query)
        
        if person_name:
            print(f"[UI_SCHOLAR] Detected person name: {person_name}")
            print(f"[UI_SCHOLAR] Strategy: Direct person URL (bypasses anti-bot)")
            
            # Normalize name for URL: "Benyamin Kusumo Putro" -> "benyamin-kusumo-putro"
            normalized_name = person_name.lower().replace(' ', '-').replace('.', '')
            person_url = f"https://scholar.ui.ac.id/en/persons/{normalized_name}/"
            
            print(f"[UI_SCHOLAR] Trying person URL: {person_url}")
            
            # Try to scrape person page directly
            try:
                result = self._scrape_person_page(person_url, person_name)
                if result and len(result) > 200:
                    return result
                else:
                    print(f"[UI_SCHOLAR] Person page not found, trying alternative...")
            except Exception as e:
                print(f"[UI_SCHOLAR] Person page error: {e}")
        
        # FALLBACK: If person URL fails, recommend manual access
        return self._fallback_response(query, person_name)
    
    def _extract_person_name(self, query: str) -> str:
        """Extract person name from query."""
        query_clean = query.lower()
        for keyword in ['publications', 'research', 'papers', 'publikasi', 'riset', 'karya']:
            query_clean = query_clean.replace(keyword, '')
        
        query_clean = query_clean.strip()
        
        # Look for capitalized names (likely person name)
        import re
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'
        match = re.search(name_pattern, query)
        
        if match:
            return match.group(1)
        
        return None
    
    def _scrape_person_page(self, url: str, person_name: str) -> str:
        """Scrape person's profile page directly."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            print(f"[UI_SCHOLAR] Fetching: {url}")
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 404:
                print(f"[UI_SCHOLAR] ✗ Person page not found (404)")
                return None
            
            response.raise_for_status()
            print(f"[UI_SCHOLAR] ✓ HTTP {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            publications = []
            
            # Look for publication links
            pub_links = soup.find_all('a', href=lambda x: x and '/publications/' in str(x))
            
            for link in pub_links[:15]:
                title = link.get_text(strip=True)
                href = link.get('href')
                
                if len(title) > 20 and title not in ['Publications', 'View', 'More']:
                    publications.append({
                        'title': title,
                        'link': f"https://scholar.ui.ac.id{href}" if not href.startswith('http') else href,
                        'authors': person_name,
                        'year': '',
                        'journal': ''
                    })
            
            if publications:
                output = f"📚 **Publications by {person_name}** (from scholar.ui.ac.id)\n\n"
                output += f"Found {len(publications)} publication(s):\n\n"
                
                for i, pub in enumerate(publications, 1):
                    output += f"{i}. **{pub['title']}**\n"
                    if pub['authors']:
                        output += f"   👥 {pub['authors']}\n"
                    if pub['link']:
                        output += f"   🔗 {pub['link']}\n"
                    output += "\n"
                
                output += f"\n💡 **Source:** Direct person profile on scholar.ui.ac.id\n"
                print(f"[UI_SCHOLAR] ✓ Extracted {len(publications)} publications")
                return output
            else:
                print(f"[UI_SCHOLAR] ✗ No publications found")
                return None
                
        except Exception as e:
            print(f"[UI_SCHOLAR] Error: {e}")
            return None
    
    def _fallback_response(self, query: str, person_name: str = None) -> str:
        """Provide fallback response with manual access instructions."""
        if person_name:
            normalized_name = person_name.lower().replace(' ', '-').replace('.', '')
            direct_url = f"https://scholar.ui.ac.id/en/persons/{normalized_name}/"
            
            return f"""⚠️ **Unable to automatically access scholar.ui.ac.id**

**Recommended Actions:**

1. **Visit Person Page Directly**:
   {direct_url}
   
2. **Browse Department Publications**:
   https://scholar.ui.ac.id/en/organisations/electrical-engineering/publications/

3. **Alternative Search**:
   - Use "Google Scholar Search Tool" for publications by {person_name}

**Why this happened:**
scholar.ui.ac.id blocks automated search queries but allows direct page access."""
        
        else:
            return f"""⚠️ **scholar.ui.ac.id search unavailable**

**Alternative Solutions:**

1. **Visit Directly**: https://scholar.ui.ac.id/en/publications/

2. **Use Department Page**: 
   https://scholar.ui.ac.id/en/organisations/electrical-engineering/publications/

3. **Try Google Scholar Search Tool** for broader publication search"""


# ========== ENG.UI.AC.ID PERSONNEL SCRAPER TOOL (NEW!) ==========
class EngUIPersonnelInput(BaseModel):
    """Input schema for ENG.UI.AC.ID Personnel Scraper Tool."""
    professor_name: str = Field(..., description="Name of the professor/lecturer (e.g., 'Mia Rizkinia', 'Abdul Muis', 'Riri Fitri Sari')")


class EngUIPersonnelScraperTool(BaseTool):
    name: str = "ENG.UI.AC.ID Personnel Page Scraper"
    description: str = (
        "Scrapes official personnel pages from eng.ui.ac.id (Faculty of Engineering UI website). "
        "This is the OFFICIAL source for: Education history, Research expertise, Latest publications, Position/title. "
        "Use this tool when user asks about a specific professor from UI Electrical Engineering department. "
        "Returns: Complete education history (Bachelor/Master/Doctoral with universities and years), "
        "Research interests, Latest 3-5 publications with titles and years, Academic position."
    )
    args_schema: Type[BaseModel] = EngUIPersonnelInput

    def _run(self, professor_name: str) -> str:
        """Scrape eng.ui.ac.id personnel page for comprehensive professor data."""
        print(f"\n[ENG_UI_SCRAPER] Scraping personnel page for: {professor_name}")
        
        try:
            # Import scraper function
            from eng_ui_scraper import scrape_eng_ui_personnel, format_eng_ui_data
            
            # Scrape the page
            data = scrape_eng_ui_personnel(professor_name)
            
            if not data:
                return f"""⚠️ **Personnel page not found for '{professor_name}'** on eng.ui.ac.id

**Possible reasons:**
1. Name spelling might be different on the website
2. Professor might not have a page yet
3. Page might be under a different URL structure

**Recommendations:**
- Try variations of the name (with/without title, middle name)
- Use 'Web Search Tool' to find their information
- Check the full faculty directory: https://eng.ui.ac.id/personnel/"""
            
            # Format the data into readable output
            formatted_output = format_eng_ui_data(data)
            
            print(f"[ENG_UI_SCRAPER] ✅ Successfully scraped {len(formatted_output)} chars")
            return formatted_output
            
        except ImportError as e:
            error_msg = f"❌ Error: eng_ui_scraper module not found. {str(e)}"
            print(f"[ENG_UI_SCRAPER] {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"❌ Unexpected error scraping eng.ui.ac.id: {type(e).__name__} - {str(e)}"
            print(f"[ENG_UI_SCRAPER] {error_msg}")
            return error_msg

# ========== PDF SEARCH TOOL (USER UPLOADED) ==========
class PDFSearchInput(BaseModel):
    """Input schema for PDF Search Tool."""
    query: str = Field(..., description="Search query to find information within uploaded PDF documents")


class PDFSearchTool(BaseTool):
    name: str = "User PDF Search Tool"
    description: str = (
        "Searches through user-uploaded PDF documents for relevant information. "
        "This tool ONLY works if the user has uploaded PDF files. "
        "Use this when user asks questions about their uploaded documents. "
        "Returns relevant text excerpts from the uploaded PDFs that match the query."
    )
    args_schema: Type[BaseModel] = PDFSearchInput

    def _run(self, query: str) -> str:
        """Search through uploaded PDF content stored in database."""
        if embeddings is None:
            return "Error: Embedding model failed to initialize."
            
        try:
            client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
            db = client.get_database_by_api_endpoint(ASTRA_DB_API_ENDPOINT)
            collection = db.get_collection(COLLECTION_NAME)

            query_vector = embeddings.embed_query(query)
            
            # Search for PDF content specifically
            results = collection.find(
                filter={"source_type": "user_pdf"},
                sort={"$vector": query_vector},
                limit=10,
                projection={"*": 1}
            )

            docs = list(results)
            
            print(f"[PDF_SEARCH] Query: {query}")
            print(f"[PDF_SEARCH] Found {len(docs)} PDF chunks")
            
            if not docs:
                return "⚠️ No uploaded PDF documents found. Please upload a PDF file first using the 'Add New Source' button."
            
            context_parts = []
            pdf_files = set()
            
            for idx, doc in enumerate(docs):
                content = (
                    doc.get('text') or 
                    doc.get('content') or 
                    doc.get('page_content') or 
                    str(doc)
                )
                
                if content:
                    pdf_name = doc.get('pdf_name', 'Unknown PDF')
                    page_num = doc.get('page_number', '?')
                    pdf_files.add(pdf_name)
                    
                    context_parts.append(f"[From: {pdf_name}, Page {page_num}]\n{content}")
                    print(f"[PDF_SEARCH]   [{idx+1}] {len(content)} chars from {pdf_name} (page {page_num})")
            
            context = "\n\n---\n\n".join(context_parts)
            
            result = f"📄 **Information from {len(pdf_files)} uploaded PDF(s):**\n\n"
            result += f"Files: {', '.join(pdf_files)}\n\n"
            result += f"**Relevant Content:**\n\n{context}"
            
            print(f"[PDF_SEARCH] Total context: {len(context)} characters from {len(pdf_files)} files")
            return result
            
        except Exception as e:
            print(f"[PDF_SEARCH ERROR] {e}")
            return f"Error searching PDF documents: {e}"


# Initialize tool instances
web_search_tool = TavilySearchTool()
academic_search_tool = AcademicSearchTool()
dynamic_web_scraper_tool = DynamicWebScraperTool()
google_scholar_tool = GoogleScholarSearchTool()
google_scholar_profiles_tool = GoogleScholarProfilesSearchTool()
google_scholar_author_tool = GoogleScholarAuthorProfileTool()
google_scholar_publications_tool = GoogleScholarPublicationsSearchTool()
google_scholar_cited_by_tool = GoogleScholarCitedByTool()
# sinta_scraper_tool removed - use ui_scholar_search_tool instead
cv_generator_tool = CVGeneratorTool()
ui_scholar_search_tool = UIScholarSearchTool()
eng_ui_personnel_scraper_tool = EngUIPersonnelScraperTool()  # NEW: ENG.UI.AC.ID scraper
pdf_search_tool = PDFSearchTool()  # New PDF search tool
