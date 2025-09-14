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
    """Système de backup LLM avec OpenAI + Claude et sélection intelligente selon objectifs"""
    
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
    
    def select_primary_llm(
        self,
        business_objective: str = "equilibre",
        brand_tone: str = "professionnel", 
        platform: str = "instagram"
    ) -> tuple:
        """
        Sélectionne le LLM primaire et backup selon la stratégie business
        
        Args:
            business_objective: "conversion", "communaute", "equilibre" 
            brand_tone: ton de marque (si "storytelling" force Claude primary)
            platform: "instagram", "facebook", "linkedin"
            
        Returns:
            tuple: (primary_llm, backup_llm) où les valeurs sont "openai" ou "claude"
        """
        
        print(f"🧠 LLM Selection - Objective: {business_objective}, Tone: {brand_tone}, Platform: {platform}")
        
        # Règle 1: Si storytelling → TOUJOURS Claude primary
        if brand_tone == "storytelling":
            print("📖 Storytelling detected → Claude PRIMARY, OpenAI backup")
            return ("claude", "openai")
        
        # Règle 2: Objectif conversion → OpenAI primary
        if business_objective == "conversion":
            print("💰 Conversion objective → OpenAI PRIMARY, Claude backup")
            return ("openai", "claude")
        
        # Règle 3: Objectif communauté → Claude primary  
        if business_objective == "communaute":
            print("👥 Community objective → Claude PRIMARY, OpenAI backup")
            return ("claude", "openai")
        
        # Règle 4: Équilibré → Logique par plateforme
        if business_objective == "equilibre":
            if platform.lower() == "instagram":
                print("📸 Instagram + Equilibré → OpenAI PRIMARY, Claude backup")
                return ("openai", "claude")
            elif platform.lower() in ["facebook", "linkedin"]:
                print(f"🔗 {platform.title()} + Equilibré → Claude PRIMARY, OpenAI backup")
                return ("claude", "openai")
        
        # Défaut: OpenAI primary
        print("🔄 Default selection → OpenAI PRIMARY, Claude backup")
        return ("openai", "claude")
    
    async def generate_completion_with_strategy(
        self,
        messages: List[Dict[str, str]],
        business_objective: str = "equilibre",
        brand_tone: str = "professionnel",
        platform: str = "instagram",
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_message: Optional[str] = None
    ) -> str:
        """
        Génère une completion avec sélection intelligente LLM selon la stratégie business
        """
        
        # Sélectionner les LLM selon la stratégie
        primary_llm, backup_llm = self.select_primary_llm(business_objective, brand_tone, platform)
        
        # Construire le prompt pour Claude à partir des messages OpenAI
        if system_message:
            full_prompt = f"System: {system_message}\n\n"
        else:
            full_prompt = ""
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            full_prompt += f"{role.capitalize()}: {content}\n\n"
        
        # Tentative 1: LLM primaire
        try:
            if primary_llm == "openai" and self.openai_client:
                logging.info(f"🚀 Primary OpenAI (objective: {business_objective}, platform: {platform})...")
                
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                result = response.choices[0].message.content
                logging.info(f"✅ OpenAI primary réussi - {len(result)} chars")
                return result
                
            elif primary_llm == "claude" and self.claude_chat:
                logging.info(f"🧠 Primary Claude (objective: {business_objective}, platform: {platform})...")
                
                user_message = UserMessage(text=full_prompt.strip())
                response = await self.claude_chat.send_message(user_message)
                
                logging.info(f"✅ Claude primary réussi - {len(response)} chars")
                return response
                
        except Exception as primary_error:
            logging.error(f"❌ Primary {primary_llm} échoué: {primary_error}")
            print(f"⚠️ Primary {primary_llm} failed, trying {backup_llm} backup...")
        
        # Tentative 2: LLM backup
        try:
            if backup_llm == "openai" and self.openai_client:
                logging.info(f"🔄 Backup OpenAI...")
                
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                result = response.choices[0].message.content
                logging.info(f"✅ OpenAI backup réussi - {len(result)} chars")
                print("✅ OpenAI backup successful!")
                return result
                
            elif backup_llm == "claude" and self.claude_chat:
                logging.info(f"🔄 Backup Claude...")
                
                user_message = UserMessage(text=full_prompt.strip())
                response = await self.claude_chat.send_message(user_message)
                
                logging.info(f"✅ Claude backup réussi - {len(response)} chars")
                print("✅ Claude backup successful!")
                return response
                
        except Exception as backup_error:
            logging.error(f"❌ Backup {backup_llm} échoué: {backup_error}")
            print(f"❌ Backup {backup_llm} failed: {str(backup_error)[:100]}...")
        
        # Si les deux échouent
        error_msg = f"Both {primary_llm} (primary) and {backup_llm} (backup) failed"
        logging.error(error_msg)
        raise Exception(error_msg)
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_message: Optional[str] = None
    ) -> str:
        """
        Génère une completion avec backup automatique (mode compatible ancien système)
        Essaie OpenAI d'abord, puis Claude en cas d'échec
        """
        return await self.generate_completion_with_strategy(
            messages=messages,
            business_objective="equilibre",  # Défaut compatible
            brand_tone="professionnel",
            platform="instagram",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_message=system_message
        )
    
    async def analyze_website_content(
        self,
        content_data: Dict[str, Any],
        website_url: str
    ) -> Dict[str, Any]:
        """Analyse de contenu web avec backup"""
        
        # Prompt ULTRA-APPROFONDI pour analyse maximale (sans changer la structure JSON)
        prompt = f"""
        Tu es un analyste expert en intelligence business et marketing digital. Ta mission : analyser ce site web de manière EXHAUSTIVE pour extraire un MAXIMUM d'informations exploitables pour la création de contenu marketing et posts sociaux.

        Analyse CHAQUE élément du site en profondeur et réponds UNIQUEMENT par un JSON structuré avec les clés suivantes:
        {{
            "analysis_summary": "Un résumé ULTRA-DÉTAILLÉ de l'entreprise (400-600 mots) incluant : QUI ils sont exactement (nom, histoire, fondateurs), CE QU'ILS FONT en détail (tous leurs produits/services avec spécificités), COMMENT ils le font (processus, méthodes, approche unique), leurs SPÉCIALITÉS techniques, leur POSITIONNEMENT marché, leurs VALEURS et mission, leur EXPÉRIENCE (années, réalisations, clients), leurs DIFFÉRENCIATEURS vs concurrence, leurs TÉMOIGNAGES clients si mentionnés, leurs TARIFS/PRIX si indiqués, leur ZONE géographique, leurs CERTIFICATIONS/PRIX, leurs ÉQUIPES/EXPERTISE, tous les DÉTAILS exploitables pour créer du contenu spécifique",
            
            "key_topics": ["Extraire 8-12 sujets précis du site : tous les produits/services mentionnés, les domaines d'expertise, les mots-clés récurrents, les spécialités techniques, les valeurs/approches, les résultats/réalisations, les processus uniques, etc."],
            
            "brand_tone": "Analyser finement le ton de communication avec nuances : professionnel/décontracté/premium/accessible/expert/technique/émotionnel/storytelling - être précis sur le style exact utilisé",
            
            "target_audience": "Description ULTRA-PRÉCISE du public cible en analysant tous les indices : âge estimé, profession/secteur, niveau de revenus suggéré, problématiques adressées, motivations, comportements d'achat, canaux préférés, langage utilisé pour s'adresser à eux, exemples de clients mentionnés",
            
            "main_services": ["Lister TOUS les services/produits trouvés avec leurs spécificités exactes : 'Service X - processus Y - bénéfice Z - cible W - prix P si mentionné', inclure tous les détails trouvés : durées, méthodologies, outils utilisés, livrables, garanties, etc."],
            
            "content_suggestions": ["Générer 6-8 suggestions de posts TRÈS SPÉCIFIQUES basées sur les éléments concrets trouvés : 'Post produit X avec caractéristique Y pour problème Z', 'Post témoignage client A avec résultat B', 'Post processus C avec étapes D-E-F', 'Post expertise G avec conseil H', 'Post coulisses I avec équipe J', 'Post réalisation K avec chiffres L', etc. - chaque suggestion doit être exploitable immédiatement"]
        }}

        CONTENU DU SITE À ANALYSER EN PROFONDEUR :
        
        URL du site: {website_url}
        Titre principal: {content_data.get('meta_title', 'Non défini')}
        Description meta: {content_data.get('meta_description', 'Non définie')}
        
        TOUS les titres H1 (très importants): {content_data.get('h1_tags', [])}
        TOUS les titres H2 (structure du contenu): {content_data.get('h2_tags', [])}
        
        CONTENU TEXTUEL COMPLET (à analyser mot par mot):
        {content_data.get('text_content', 'Non disponible')[:4000]}
        
        PAGES ANALYSÉES: {len(content_data.get('pages_analyzed', []))} pages
        Détails des pages: {[page.get('title', 'Sans titre') + ' - ' + page.get('url', '') for page in content_data.get('pages_analyzed', [])[:10]]}

        INSTRUCTIONS ULTRA-SPÉCIFIQUES :
        
        🔍 EXTRACTION MAXIMALE :
        - IDENTIFIE tous les produits/services avec noms exacts, caractéristiques, prix, processus
        - RELÈVE tous les témoignages, noms de clients, chiffres de résultats, réalisations
        - DÉTECTE tous les mots-clés métier, jargon technique, termes spécialisés
        - ANALYSE le vocabulaire pour identifier le niveau d'expertise et le public visé  
        - REPÈRE tous les éléments différenciants, points forts, avantages concurrentiels
        - EXTRAIT les informations sur l'équipe, l'histoire, les valeurs, la mission
        - NOTE tous les détails géographiques, horaires, contacts, modalités pratiques
        
        💡 PENSÉE MARKETING :
        - CHAQUE information extraite doit être exploitable pour créer un post spécifique
        - PRIORISE les éléments qui peuvent générer de l'engagement social
        - IDENTIFIE les angles de contenu : expertise, coulisses, résultats, processus, équipe
        - SUGGÈRE des posts concrets avec les éléments factuels trouvés
        
        📊 FACTUALITÉ TOTALE :
        - Utilise les TERMES EXACTS trouvés sur le site (pas de paraphrase)
        - CITE les chiffres, prix, durées, noms précis mentionnés
        - BASE-toi uniquement sur ce qui est réellement écrit (pas d'invention)
        - STRUCTURE les informations de manière exploitable pour le marketing
        
        OBJECTIF : Extraire suffisamment d'informations détaillées pour créer 50+ posts différents et ciblés !
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
                temperature=0.6,  # Équilibre entre créativité et précision
                max_tokens=3500   # Plus de tokens pour des réponses ultra-détaillées
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