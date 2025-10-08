#!/usr/bin/env python3
"""
Test de l'endpoint de diagnostic selon la demande française
DIAGNOSTIC IMMÉDIAT : Tester l'endpoint /api/content/_debug pour identifier le mismatch de filtre.
"""

import requests
import json
import time

# Configuration - Using the correct backend URL from frontend/.env
BACKEND_URL = "https://post-restore.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials as specified in review request
TEST_EMAIL = "lperpere@yahoo.fr"
TEST_PASSWORD = "L@Reunion974!"

class DiagnosticTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details="", error=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "error": error
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
        print()
    
    def authenticate(self):
        """Step 1: Authentifier avec lperpere@yahoo.fr / L@Reunion974!"""
        print("🔐 STEP 1: Authentication avec credentials spécifiés")
        print("=" * 50)
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log_result(
                    "Authentication", 
                    True, 
                    f"Successfully authenticated as {TEST_EMAIL}, User ID: {self.user_id}"
                )
                return True
            else:
                self.log_result(
                    "Authentication", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, error=str(e))
            return False
    
    def test_debug_endpoint(self):
        """Step 2: Tester GET /api/content/_debug pour voir les counts et diagnostics"""
        print("🔍 STEP 2: Test GET /api/content/_debug")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/_debug")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key diagnostic information
                db_name = data.get("db", "unknown")
                user_id = data.get("user_id", "unknown")
                filter_used = data.get("filter_used", {})
                counts = data.get("counts", {})
                one_any = data.get("one_any", {})
                one_mine = data.get("one_mine", "None")
                
                # Analyze counts
                count_any = counts.get("any", 0)
                count_mine = counts.get("mine", 0)
                
                # Analyze document structure from one_any
                owner_id_value = None
                owner_id_type = "unknown"
                document_keys = []
                
                if one_any:
                    owner_id_value = one_any.get("owner_id")
                    document_keys = one_any.get("keys", [])
                    
                    if owner_id_value:
                        owner_id_type = type(owner_id_value).__name__
                
                # Build detailed analysis
                details = f"DATABASE: {db_name}, "
                details += f"USER_ID: {user_id}, "
                details += f"COUNTS: any={count_any} (≈39 attendu), mine={count_mine} (>0 attendu), "
                details += f"FILTER_USED: {filter_used}, "
                details += f"DOCUMENT_KEYS: {document_keys}, "
                details += f"OWNER_ID_VALUE: {owner_id_value}, "
                details += f"OWNER_ID_TYPE: {owner_id_type}, "
                details += f"ONE_MINE: {one_mine}"
                
                # Determine if there's a mismatch
                has_mismatch = count_mine == 0 and count_any > 0
                mismatch_analysis = ""
                
                if has_mismatch:
                    mismatch_analysis = "🚨 MISMATCH DÉTECTÉ: Documents existent (any>0) mais aucun n'appartient à l'utilisateur (mine=0). "
                    
                    # Analyze potential causes
                    if "owner_id" in document_keys and "ownerId" in document_keys:
                        mismatch_analysis += "CAUSE POSSIBLE: Champs owner_id ET ownerId présents (conflit de noms). "
                    elif "owner_id" not in document_keys and "ownerId" in document_keys:
                        mismatch_analysis += "CAUSE POSSIBLE: Documents utilisent 'ownerId' mais filtre cherche 'owner_id'. "
                    elif owner_id_type == "ObjectId" and isinstance(user_id, str):
                        mismatch_analysis += "CAUSE POSSIBLE: Type mismatch - owner_id est ObjectId mais user_id est string. "
                    else:
                        mismatch_analysis += "CAUSE INCONNUE: Analyser le filtre et les types de données. "
                else:
                    mismatch_analysis = "✅ PAS DE MISMATCH: L'utilisateur a accès à ses documents. "
                
                self.log_result(
                    "Debug Endpoint Analysis", 
                    True, 
                    details + mismatch_analysis
                )
                
                # Store for comparison
                self.debug_data = {
                    "db": db_name,
                    "user_id": user_id,
                    "count_any": count_any,
                    "count_mine": count_mine,
                    "filter_used": filter_used,
                    "document_keys": document_keys,
                    "owner_id_value": owner_id_value,
                    "owner_id_type": owner_id_type,
                    "has_mismatch": has_mismatch,
                    "mismatch_analysis": mismatch_analysis
                }
                
                return True
            else:
                self.log_result(
                    "Debug Endpoint Analysis", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Debug Endpoint Analysis", False, error=str(e))
            return False
    
    def test_pending_content_with_tolerant_filter(self):
        """Step 3: Tester la nouvelle route GET /api/content/pending avec le filtre tolérant"""
        print("🔧 STEP 3: Test GET /api/content/pending avec filtre tolérant")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{API_BASE}/content/pending?limit=50")
            
            if response.status_code == 200:
                data = response.json()
                
                content = data.get("content", [])
                total = data.get("total", 0)
                loaded = data.get("loaded", 0)
                
                # Analyze content structure
                sample_content = content[0] if content else None
                content_keys = list(sample_content.keys()) if sample_content else []
                
                details = f"PENDING_CONTENT: total={total}, loaded={loaded}, "
                details += f"content_count={len(content)}, "
                details += f"sample_keys={content_keys}"
                
                # Compare with debug data if available
                if hasattr(self, 'debug_data'):
                    debug_count_mine = self.debug_data.get("count_mine", 0)
                    
                    if len(content) > debug_count_mine:
                        details += f" 🎯 FILTRE TOLÉRANT FONCTIONNE: pending_content ({len(content)}) > debug_mine ({debug_count_mine})"
                    elif len(content) == debug_count_mine and debug_count_mine > 0:
                        details += f" ✅ FILTRE COHÉRENT: pending_content ({len(content)}) = debug_mine ({debug_count_mine})"
                    else:
                        details += f" ⚠️ FILTRE PROBLÉMATIQUE: pending_content ({len(content)}) ≤ debug_mine ({debug_count_mine})"
                
                self.log_result(
                    "Pending Content with Tolerant Filter", 
                    len(content) > 0, 
                    details
                )
                
                # Store for comparison
                self.pending_data = {
                    "total": total,
                    "loaded": loaded,
                    "content_count": len(content),
                    "sample_keys": content_keys
                }
                
                return len(content) > 0
            else:
                self.log_result(
                    "Pending Content with Tolerant Filter", 
                    False, 
                    f"Status: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Pending Content with Tolerant Filter", False, error=str(e))
            return False
    
    def compare_results_before_after_patch(self):
        """Step 4: Comparer les résultats avant/après le patch"""
        print("📊 STEP 4: Comparaison avant/après patch")
        print("=" * 50)
        
        if not hasattr(self, 'debug_data') or not hasattr(self, 'pending_data'):
            self.log_result(
                "Before/After Patch Comparison", 
                False, 
                "Missing debug_data or pending_data for comparison"
            )
            return False
        
        try:
            debug_data = self.debug_data
            pending_data = self.pending_data
            
            # Key comparison metrics
            debug_mine = debug_data.get("count_mine", 0)
            debug_any = debug_data.get("count_any", 0)
            pending_count = pending_data.get("content_count", 0)
            
            # Analysis
            comparison_details = f"COMPARAISON RÉSULTATS: "
            comparison_details += f"debug_any={debug_any}, debug_mine={debug_mine}, pending_content={pending_count}. "
            
            # Determine patch effectiveness
            patch_effective = False
            patch_analysis = ""
            
            if debug_data.get("has_mismatch", False):
                # There was a mismatch in debug
                if pending_count > debug_mine:
                    patch_effective = True
                    patch_analysis = "✅ PATCH EFFICACE: Le filtre tolérant a résolu le mismatch - plus de contenu accessible via pending_content. "
                else:
                    patch_analysis = "❌ PATCH INEFFICACE: Le mismatch persiste - pending_content n'a pas plus de résultats. "
            else:
                # No mismatch detected
                if pending_count == debug_mine and debug_mine > 0:
                    patch_effective = True
                    patch_analysis = "✅ SYSTÈME COHÉRENT: Pas de mismatch détecté, les résultats sont cohérents. "
                else:
                    patch_analysis = "⚠️ RÉSULTATS INCOHÉRENTS: Différence inattendue entre debug et pending_content. "
            
            # Root cause identification
            root_cause = ""
            if debug_data.get("has_mismatch", False):
                mismatch_analysis = debug_data.get("mismatch_analysis", "")
                root_cause = f"CAUSE RACINE IDENTIFIÉE: {mismatch_analysis}"
            
            final_details = comparison_details + patch_analysis + root_cause
            
            self.log_result(
                "Before/After Patch Comparison", 
                True, 
                final_details
            )
            
            # Store final analysis
            self.final_analysis = {
                "patch_effective": patch_effective,
                "debug_mine": debug_mine,
                "debug_any": debug_any,
                "pending_count": pending_count,
                "patch_analysis": patch_analysis,
                "root_cause": root_cause
            }
            
            return True
            
        except Exception as e:
            self.log_result("Before/After Patch Comparison", False, error=str(e))
            return False
    
    def run_diagnostic_tests(self):
        """Run all diagnostic tests as requested in French review"""
        print("🚀 TEST DE L'ENDPOINT DE DIAGNOSTIC - DEMANDE FRANÇAISE")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_EMAIL}")
        print(f"OBJECTIF: Identifier le mismatch de filtre et vérifier le patch")
        print("=" * 60)
        print()
        
        # Run tests in sequence
        tests = [
            self.authenticate,
            self.test_debug_endpoint,
            self.test_pending_content_with_tolerant_filter,
            self.compare_results_before_after_patch
        ]
        
        for test in tests:
            if not test():
                print("❌ Test failed, continuing with remaining tests...")
            print()
        
        # Summary
        print("📋 RÉSUMÉ DU DIAGNOSTIC")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Diagnostic specific summary
        print("DIAGNOSTIC SELON LA DEMANDE FRANÇAISE:")
        print("-" * 40)
        
        if hasattr(self, 'debug_data'):
            debug = self.debug_data
            print(f"1. DATABASE: {debug.get('db', 'unknown')}")
            print(f"2. COUNTS: any={debug.get('count_any', 0)} (≈39 attendu), mine={debug.get('count_mine', 0)} (>0 attendu)")
            print(f"3. DOCUMENT KEYS: {debug.get('document_keys', [])}")
            print(f"4. OWNER_ID TYPE: {debug.get('owner_id_type', 'unknown')}")
            print(f"5. MISMATCH: {'OUI' if debug.get('has_mismatch', False) else 'NON'}")
            print()
        
        if hasattr(self, 'final_analysis'):
            analysis = self.final_analysis
            print(f"EFFICACITÉ DU PATCH: {'✅ EFFICACE' if analysis.get('patch_effective', False) else '❌ INEFFICACE'}")
            print(f"ANALYSE: {analysis.get('patch_analysis', 'N/A')}")
            print(f"CAUSE RACINE: {analysis.get('root_cause', 'N/A')}")
            print()
        
        # Detailed results
        for result in self.test_results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
            if result['error']:
                print(f"   Error: {result['error']}")
        
        print()
        print("🎯 DIAGNOSTIC ENDPOINT TESTING COMPLETED")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = DiagnosticTester()
    success = tester.run_diagnostic_tests()
    
    if success:
        print("✅ Overall diagnostic testing: SUCCESS")
        exit(0)
    else:
        print("❌ Overall diagnostic testing: FAILED")
        exit(1)