"""
Système de backup LLM unifié : OpenAI GPT-4o + Claude Sonnet 4
Utilisé partout dans l'application pour avoir un fallback robuste
"""
import os
import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configuration des clés API
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')

# Imports des bibliothèques
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    LlmChat = None
    UserMessage = None

print(f"🔧 LLM Backup System Initialized:")
print(f"   - OpenAI GPT-4o: {'✅' if OPENAI_AVAILABLE and OPENAI_API_KEY else '❌'}")
print(f"   - Claude Sonnet 4: {'✅' if CLAUDE_AVAILABLE and CLAUDE_API_KEY else '❌'}")


class LLMBackupSystem:
    """Système de backup LLM avec OpenAI primary et Claude secondary"""
    
    def __init__(self):
        self.openai_client = None
        self.claude_chat = None
        
        # Initialiser OpenAI si disponible
        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
                print("✅ OpenAI GPT-4o client initialized")
            except Exception as e:
                print(f"❌ OpenAI initialization error: {e}")
        
        # Initialiser Claude si disponible
        if CLAUDE_AVAILABLE and CLAUDE_API_KEY:
            try:
                self.claude_chat = LlmChat(
                    api_key=CLAUDE_API_KEY,
                    session_id="backup-system",
                    system_message="You are Claude, a helpful AI assistant. You will receive prompts that were originally designed for GPT-4o. Please provide equivalent quality responses."
                ).with_model("anthropic", "claude-4-sonnet-20250514")
                print("✅ Claude Sonnet 4 client initialized")
            except Exception as e:
                print(f"❌ Claude initialization error: {e}")
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_message: Optional[str] = None
    ) -> str:
        """
        Génère une completion avec backup automatique
        Essaie OpenAI d'abord, puis Claude en cas d'échec
        """
        
        # Construire le prompt pour Claude à partir des messages OpenAI
        if system_message:
            full_prompt = f"System: {system_message}\n\n"
        else:
            full_prompt = ""
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            full_prompt += f"{role.capitalize()}: {content}\n\n"
        
        # Tentative 1: OpenAI GPT-4o
        if self.openai_client:
            try:
                logging.info("🚀 Tentative OpenAI GPT-4o...")
                
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                result = response.choices[0].message.content
                logging.info(f"✅ OpenAI réussi - {len(result)} chars")
                return result
                
            except Exception as openai_error:
                logging.error(f"❌ OpenAI échoué: {openai_error}")
                print(f"⚠️ OpenAI failed, trying Claude backup: {str(openai_error)[:100]}...")
        
        # Tentative 2: Claude Sonnet 4 (backup)
        if self.claude_chat:
            try:
                logging.info("🔄 Backup Claude Sonnet 4...")
                
                user_message = UserMessage(text=full_prompt.strip())
                response = await self.claude_chat.send_message(user_message)
                
                logging.info(f"✅ Claude backup réussi - {len(response)} chars")
                print("✅ Claude backup successful!")
                return response
                
            except Exception as claude_error:
                logging.error(f"❌ Claude backup échoué: {claude_error}")
                print(f"❌ Claude backup failed: {str(claude_error)[:100]}...")
        
        # Si les deux échouent
        error_msg = "Both OpenAI and Claude failed"
        logging.error(error_msg)
        raise Exception(error_msg)
    
    async def analyze_website_content(
        self,
        content_data: Dict[str, Any],
        website_url: str
    ) -> Dict[str, Any]:
        """Analyse de contenu web avec backup"""
        
        # Prompt pour l'analyse de site web
        prompt = f"""
        Analyse ce site web en profondeur et réponds UNIQUEMENT par un JSON structuré avec les clés suivantes:
        {{
            "analysis_summary": "Un résumé détaillé de l'entreprise et de ses activités (200-300 mots)",
            "key_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
            "brand_tone": "le ton de communication (professionnel/décontracté/premium/accessible)",
            "target_audience": "description du public cible principal",
            "main_services": ["service1", "service2", "service3"],
            "content_suggestions": ["suggestion1", "suggestion2", "suggestion3", "suggestion4"]
        }}

        Site web: {website_url}
        Titre de la page: {content_data.get('meta_title', 'Non défini')}
        Description: {content_data.get('meta_description', 'Non définie')}
        Titres H1: {content_data.get('h1_tags', [])}
        Titres H2: {content_data.get('h2_tags', [])}
        Contenu principal: {content_data.get('text_content', 'Non disponible')[:2000]}

        IMPORTANT: Sois très généreux dans les détails. Plus c'est précis et détaillé, plus ce sera utile pour créer du contenu marketing pertinent.
        """
        
        messages = [
            {
                "role": "system",
                "content": "Tu es un expert en analyse de contenu web et marketing digital. Tu analyses les sites web en profondeur pour créer du contenu social media. Réponds UNIQUEMENT en JSON valide et structuré."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            raw_response = await self.generate_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parser la réponse JSON
            if raw_response and len(raw_response) > 50:
                # Nettoyer la réponse pour extraire le JSON
                clean_response = raw_response.strip()
                if clean_response.startswith('```json'):
                    clean_response = clean_response[7:]
                if clean_response.endswith('```'):
                    clean_response = clean_response[:-3]
                
                analysis_result = json.loads(clean_response.strip())
                
                # Valider que les clés requises sont présentes
                required_keys = ['analysis_summary', 'key_topics', 'brand_tone', 'target_audience', 'main_services', 'content_suggestions']
                if all(key in analysis_result for key in required_keys):
                    logging.info("✅ Analyse LLM backup réussie")
                    return analysis_result
                else:
                    raise ValueError("Missing required keys in response")
            
            raise ValueError("Response too short or empty")
            
        except Exception as e:
            logging.error(f"❌ LLM backup analysis failed: {e}")
            # Fallback générique si tout échoue
            return self._create_fallback_analysis(content_data, website_url)
    
    def _create_fallback_analysis(self, content_data: Dict[str, Any], website_url: str) -> Dict[str, Any]:
        """Analyse de fallback basique si tous les LLM échouent"""
        title = content_data.get('meta_title', website_url)
        
        return {
            "analysis_summary": f"Entreprise analysée : {title}. Analyse technique indisponible, veuillez réessayer.",
            "key_topics": ["entreprise", "services", "activité"],
            "brand_tone": "professionnel",
            "target_audience": "clients potentiels",
            "main_services": ["services principaux"],
            "content_suggestions": [
                "Présenter l'entreprise",
                "Partager l'expertise",
                "Montrer les réalisations",
                "Communiquer avec les clients"
            ]
        }


# Instance globale du système de backup
llm_backup = LLMBackupSystem()