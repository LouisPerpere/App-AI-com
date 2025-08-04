#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "User requested to start with Facebook/Instagram social media API integration for their social media automation SaaS application. They want to implement OAuth authentication and posting capabilities for both Facebook pages and Instagram business accounts."

backend:
  - task: "Facebook/Instagram OAuth Authentication"
    implemented: true
    working: "NA"  # Needs testing
    file: "/app/backend/social_media.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implemented complete Facebook OAuth flow with state management, token exchange, and long-lived token generation. Includes FacebookOAuthManager class with security features."

  - task: "Facebook API Client"
    implemented: true
    working: "NA"  # Needs testing
    file: "/app/backend/social_media.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implemented FacebookAPIClient with user info retrieval, page management, and posting capabilities. Handles page access tokens and posting to Facebook pages."

  - task: "Instagram Business API Client"
    implemented: true
    working: "NA"  # Needs testing
    file: "/app/backend/social_media.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implemented InstagramAPIClient with media container creation, publishing workflow, and account info retrieval. Handles two-step Instagram posting process."

  - task: "Social Media API Endpoints"
    implemented: true
    working: "NA"  # Needs testing
    file: "/app/backend/social_media.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added REST API endpoints: /api/social/facebook/auth-url, /api/social/facebook/callback, /api/social/connections, /api/social/post, /api/social/connection/{id} for complete social media management."

  - task: "Database Schema Updates"
    implemented: true
    working: "NA"  # Needs testing
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Updated SocialMediaConnection model to include instagram_user_id, platform_user_id, platform_username fields. Added support for multiple connection types."

  - task: "Integration with Existing Post System"
    implemented: true
    working: "NA"  # Needs testing
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added endpoints for content description, post generation, approval workflow, and immediate publishing to connected social accounts. Integrated with existing AI content generation."

  - task: "Environment Configuration"
    implemented: true
    working: "NA"  # Needs testing
    file: "/app/backend/.env"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_REDIRECT_URI environment variables to .env file. Ready for Facebook Developer App configuration."

  - task: "Dependencies Installation"
    implemented: true
    working: "NA"  # Needs testing
    file: "/app/backend/requirements.txt"
    stuck_count: 0
    priority: "low"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added facebook-sdk>=3.1.0, httpx>=0.27.0 to requirements.txt. All dependencies should be installed."

frontend:
  - task: "Social Media Connection UI"
    implemented: false
    working: false
    file: "TBD"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "Need to implement frontend UI for connecting Facebook/Instagram accounts, showing connection status, and managing social media posting."

  - task: "OAuth Callback Handler"
    implemented: false
    working: false
    file: "TBD"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "Need to implement React route handler for Facebook OAuth callback at /auth/facebook/callback."

  - task: "Post Publishing Interface"
    implemented: false
    working: false
    file: "TBD"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: false
        agent: "main"
        comment: "Need to add buttons and interface for publishing posts immediately to connected social media accounts."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Facebook/Instagram OAuth Authentication"
    - "Facebook API Client"
    - "Instagram Business API Client"
    - "Social Media API Endpoints"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "Implemented complete Facebook/Instagram integration backend with OAuth authentication, API clients, and REST endpoints. Ready for backend testing before proceeding with frontend implementation. Need to test OAuth flow, API connections, and posting functionality. Note: Facebook Developer App credentials need to be configured for full testing."