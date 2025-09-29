#!/usr/bin/env python3
"""
REACT BUG VALIDATION TEST - Website Analysis Data Structure
Testing the backend data structure to validate React bug fixes

CONTEXTE CRITIQUE:
Bug React identifié et corrigé : "Objects are not valid as a React child" causé par 
company_expertise, products_services_details, et unique_value_proposition qui sont 
des objets mais affichés directement dans <p> React.

OBJECTIF CRITIQUE:
Confirmer que le backend retourne bien ces champs comme objets (pas strings) 
pour justifier la correction React typeof + JSON.stringify.

URL DE TEST: https://social-pub-hub.preview.emergentagent.com/api
CREDENTIALS: lperpere@yahoo.fr / L@Reunion974!
"""

import requests
import json
import time
from datetime import datetime

# Configuration from review request
BACKEND_URL = "https://social-pub-hub.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "email": "lperpere@yahoo.fr",
    "password": "L@Reunion974!"
}
TEST_WEBSITE = "https://myownwatch.fr"

class ReactBugValidationTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'React-Bug-Validation-Test/1.0'
        })
        self.access_token = None
        self.user_id = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """Step 1: Authenticate with provided credentials"""
        self.log("🔐 STEP 1: Authentication Test")
        
        try:
            response = self.session.post(
                f"{BACKEND_URL}/auth/login-robust",
                json=TEST_CREDENTIALS,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.user_id = data.get("user_id")
                
                # Configure session headers
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })
                
                self.log(f"✅ Authentication successful")
                self.log(f"   User ID: {self.user_id}")
                self.log(f"   Token: {self.access_token[:20]}..." if self.access_token else "No token")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code}")
                self.log(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_website_analysis_data_structure(self):
        """Step 2: Test website analysis and validate data structure for React bug"""
        self.log(f"🔍 STEP 2: Website Analysis Data Structure Test")
        self.log(f"   Target website: {TEST_WEBSITE}")
        
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{BACKEND_URL}/website/analyze",
                json={"website_url": TEST_WEBSITE},
                timeout=120
            )
            
            analysis_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Website analysis completed in {analysis_time:.1f} seconds")
                
                # Debug: Print actual response structure
                self.log(f"🔍 DEBUG: Response structure analysis:")
                self.log(f"   Total fields in response: {len(data)}")
                
                return data
            else:
                self.log(f"❌ Website analysis failed: {response.status_code}")
                self.log(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            self.log(f"❌ Website analysis error: {str(e)}")
            return None
    
    def validate_react_bug_fields(self, data):
        """Step 3: Validate the specific fields that caused React bug"""
        self.log(f"🐛 STEP 3: React Bug Fields Validation")
        
        # The 3 fields mentioned in the review request that caused React bug
        critical_fields = [
            "company_expertise",
            "products_services_details", 
            "unique_value_proposition"
        ]
        
        validation_results = {}
        
        for field in critical_fields:
            self.log(f"   🔍 Analyzing field: {field}")
            
            if field in data:
                value = data[field]
                field_type = type(value).__name__
                
                self.log(f"     ✅ Field present: {field}")
                self.log(f"     📊 Type: {field_type}")
                
                if isinstance(value, dict):
                    self.log(f"     🎯 CONFIRMED: {field} is an OBJECT (dict)")
                    self.log(f"     🔑 Object keys: {list(value.keys())}")
                    
                    # Show sample content for each key
                    for key, val in value.items():
                        if isinstance(val, str):
                            preview = val[:100] + "..." if len(val) > 100 else val
                            self.log(f"       • {key}: {type(val).__name__} ({len(val)} chars) - {preview}")
                        elif isinstance(val, list):
                            self.log(f"       • {key}: {type(val).__name__} ({len(val)} items)")
                        else:
                            self.log(f"       • {key}: {type(val).__name__} - {val}")
                    
                    validation_results[field] = {
                        "present": True,
                        "is_object": True,
                        "type": field_type,
                        "keys": list(value.keys()) if isinstance(value, dict) else None,
                        "justifies_react_fix": True
                    }
                    
                elif isinstance(value, str):
                    self.log(f"     ⚠️ UNEXPECTED: {field} is a STRING, not an object")
                    self.log(f"     📝 Content preview: {value[:200]}...")
                    
                    validation_results[field] = {
                        "present": True,
                        "is_object": False,
                        "type": field_type,
                        "content_length": len(value),
                        "justifies_react_fix": False
                    }
                    
                else:
                    self.log(f"     ❓ UNEXPECTED TYPE: {field} is {field_type}")
                    self.log(f"     📝 Value: {value}")
                    
                    validation_results[field] = {
                        "present": True,
                        "is_object": False,
                        "type": field_type,
                        "value": value,
                        "justifies_react_fix": False
                    }
                    
            else:
                self.log(f"     ❌ Field missing: {field}")
                validation_results[field] = {
                    "present": False,
                    "is_object": False,
                    "type": None,
                    "justifies_react_fix": False
                }
        
        return validation_results
    
    def validate_expected_object_structure(self, data):
        """Step 4: Validate expected object structures from review request"""
        self.log(f"📋 STEP 4: Expected Object Structure Validation")
        
        # Expected structures from review request
        expected_structures = {
            "company_expertise": {
                "expected_keys": ["founder_info", "team_size", "key_skills", "certifications", "experience_years"],
                "description": "Company expertise with founder info, team details, skills, certifications"
            },
            "products_services_details": {
                "expected_keys": [],  # Structure not specified in review request
                "description": "Structured product/service details"
            },
            "unique_value_proposition": {
                "expected_keys": [],  # Structure not specified in review request
                "description": "Structured unique value proposition"
            }
        }
        
        structure_validation = {}
        
        for field, expected in expected_structures.items():
            self.log(f"   🔍 Validating structure: {field}")
            
            if field in data and isinstance(data[field], dict):
                actual_keys = list(data[field].keys())
                expected_keys = expected["expected_keys"]
                
                self.log(f"     ✅ Field is object as expected")
                self.log(f"     🔑 Actual keys: {actual_keys}")
                
                if expected_keys:
                    self.log(f"     🎯 Expected keys: {expected_keys}")
                    
                    matching_keys = [key for key in expected_keys if key in actual_keys]
                    missing_keys = [key for key in expected_keys if key not in actual_keys]
                    extra_keys = [key for key in actual_keys if key not in expected_keys]
                    
                    self.log(f"     ✅ Matching keys: {matching_keys} ({len(matching_keys)}/{len(expected_keys)})")
                    if missing_keys:
                        self.log(f"     ❌ Missing keys: {missing_keys}")
                    if extra_keys:
                        self.log(f"     ➕ Extra keys: {extra_keys}")
                    
                    structure_match = len(matching_keys) / len(expected_keys) * 100
                    self.log(f"     📊 Structure match: {structure_match:.1f}%")
                    
                    structure_validation[field] = {
                        "is_object": True,
                        "structure_match": structure_match,
                        "matching_keys": matching_keys,
                        "missing_keys": missing_keys,
                        "extra_keys": extra_keys
                    }
                else:
                    self.log(f"     📝 No specific structure expected, validating as generic object")
                    structure_validation[field] = {
                        "is_object": True,
                        "structure_match": 100,  # No specific requirements
                        "keys_count": len(actual_keys)
                    }
                    
            elif field in data:
                self.log(f"     ❌ Field exists but is not an object: {type(data[field])}")
                structure_validation[field] = {
                    "is_object": False,
                    "actual_type": type(data[field]).__name__
                }
            else:
                self.log(f"     ❌ Field missing from response")
                structure_validation[field] = {
                    "is_object": False,
                    "present": False
                }
        
        return structure_validation
    
    def validate_other_fields_consistency(self, data):
        """Step 5: Validate that other fields remain strings as expected"""
        self.log(f"🔍 STEP 5: Other Fields Consistency Check")
        
        # Fields that should remain strings according to review request
        string_fields = [
            "analysis_summary",
            "storytelling_analysis"
        ]
        
        consistency_results = {}
        
        for field in string_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    self.log(f"     ✅ {field}: Correctly remains string ({len(value)} chars)")
                    consistency_results[field] = {
                        "correct_type": True,
                        "type": "string",
                        "length": len(value)
                    }
                else:
                    self.log(f"     ⚠️ {field}: Unexpected type {type(value).__name__}")
                    consistency_results[field] = {
                        "correct_type": False,
                        "type": type(value).__name__
                    }
            else:
                self.log(f"     ❌ {field}: Missing from response")
                consistency_results[field] = {
                    "correct_type": False,
                    "present": False
                }
        
        return consistency_results
    
    def generate_react_fix_validation_report(self, bug_validation, structure_validation, consistency_results):
        """Step 6: Generate final validation report for React fix"""
        self.log(f"📋 STEP 6: React Fix Validation Report")
        
        self.log(f"=" * 60)
        self.log(f"🐛 REACT BUG FIX VALIDATION REPORT")
        self.log(f"=" * 60)
        
        # Count fields that justify the React fix
        fields_justifying_fix = 0
        total_critical_fields = 3
        
        for field, validation in bug_validation.items():
            if validation.get("justifies_react_fix", False):
                fields_justifying_fix += 1
        
        fix_justification_rate = (fields_justifying_fix / total_critical_fields) * 100
        
        self.log(f"🎯 CRITICAL FINDINGS:")
        self.log(f"   Fields causing React bug: {fields_justifying_fix}/{total_critical_fields}")
        self.log(f"   Fix justification rate: {fix_justification_rate:.1f}%")
        
        # Detailed field analysis
        self.log(f"\n📊 DETAILED FIELD ANALYSIS:")
        for field, validation in bug_validation.items():
            status = "✅ JUSTIFIES FIX" if validation.get("justifies_react_fix") else "❌ NO FIX NEEDED"
            self.log(f"   {field}: {status}")
            self.log(f"     Present: {validation.get('present', False)}")
            self.log(f"     Is Object: {validation.get('is_object', False)}")
            self.log(f"     Type: {validation.get('type', 'unknown')}")
            
            if validation.get("keys"):
                self.log(f"     Object Keys: {validation['keys']}")
        
        # React fix recommendation
        self.log(f"\n🔧 REACT FIX RECOMMENDATION:")
        if fix_justification_rate >= 100:
            self.log(f"   ✅ FULLY JUSTIFIED: All 3 fields are objects requiring typeof + JSON.stringify")
            self.log(f"   ✅ The React correction is the CORRECT solution")
        elif fix_justification_rate >= 66:
            self.log(f"   ⚠️ PARTIALLY JUSTIFIED: {fields_justifying_fix}/3 fields are objects")
            self.log(f"   ⚠️ React fix is appropriate for object fields")
        else:
            self.log(f"   ❌ NOT JUSTIFIED: Only {fields_justifying_fix}/3 fields are objects")
            self.log(f"   ❌ React fix may not be necessary")
        
        # Expected vs Actual structure
        self.log(f"\n📋 STRUCTURE VALIDATION:")
        for field, struct_val in structure_validation.items():
            if struct_val.get("is_object"):
                match_rate = struct_val.get("structure_match", 0)
                self.log(f"   {field}: {match_rate:.1f}% structure match")
            else:
                self.log(f"   {field}: Not an object or missing")
        
        return {
            "fix_justified": fix_justification_rate >= 66,
            "justification_rate": fix_justification_rate,
            "fields_justifying": fields_justifying_fix,
            "total_fields": total_critical_fields,
            "recommendation": "APPLY_REACT_FIX" if fix_justification_rate >= 66 else "INVESTIGATE_FURTHER"
        }
    
    def run_validation_test(self):
        """Run the complete React bug validation test"""
        self.log("🚀 REACT BUG VALIDATION TEST - Website Analysis Data Structure")
        self.log("=" * 70)
        self.log(f"Backend: {BACKEND_URL}")
        self.log(f"Test Website: {TEST_WEBSITE}")
        self.log(f"Credentials: {TEST_CREDENTIALS['email']}")
        self.log(f"Focus: Validate data structure for React typeof + JSON.stringify fix")
        self.log("=" * 70)
        
        # Step 1: Authentication
        if not self.authenticate():
            self.log("❌ CRITICAL: Authentication failed - cannot proceed with validation")
            return False
        
        # Step 2: Website Analysis
        analysis_data = self.test_website_analysis_data_structure()
        if not analysis_data:
            self.log("❌ CRITICAL: Website analysis failed - cannot validate data structure")
            return False
        
        # Step 3: Validate React bug fields
        bug_validation = self.validate_react_bug_fields(analysis_data)
        
        # Step 4: Validate expected object structures
        structure_validation = self.validate_expected_object_structure(analysis_data)
        
        # Step 5: Validate other fields consistency
        consistency_results = self.validate_other_fields_consistency(analysis_data)
        
        # Step 6: Generate final validation report
        final_report = self.generate_react_fix_validation_report(
            bug_validation, structure_validation, consistency_results
        )
        
        # Final conclusion
        self.log(f"\n🎯 FINAL CONCLUSION:")
        self.log(f"=" * 40)
        
        if final_report["fix_justified"]:
            self.log(f"✅ REACT FIX VALIDATION: SUCCESSFUL")
            self.log(f"   The typeof + JSON.stringify correction is JUSTIFIED")
            self.log(f"   Backend returns {final_report['fields_justifying']}/3 fields as objects")
            self.log(f"   React would crash trying to render these objects directly")
            self.log(f"   Recommendation: {final_report['recommendation']}")
        else:
            self.log(f"❌ REACT FIX VALIDATION: QUESTIONABLE")
            self.log(f"   Only {final_report['fields_justifying']}/3 fields are objects")
            self.log(f"   React fix may not be necessary for all fields")
            self.log(f"   Recommendation: {final_report['recommendation']}")
        
        return final_report["fix_justified"]

if __name__ == "__main__":
    tester = ReactBugValidationTest()
    success = tester.run_validation_test()
    
    if success:
        print(f"\n🎉 REACT BUG VALIDATION: CONFIRMED - Fix is justified")
    else:
        print(f"\n💥 REACT BUG VALIDATION: INCONCLUSIVE - Further investigation needed")