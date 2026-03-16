import sys
from main_agent import run_agent
from scraper import run_scraper

def run_app():
    print("=========================================")
    print("      🚀 X (Twitter) Command Center      ")
    print("=========================================")
    print("1. Draft & Post to X (with AI Rewriting)")
    print("2. Run Deep Analytics & Q/A on X")
    print("=========================================")
    
    choice = input("Select an option (1 or 2): ").strip()
    
    if choice == "1":
        print("\n--- Initializing Posting Agent ---")
        run_agent()
    elif choice == "2":
        print("\n--- Initializing Scraper & Analytics Agent ---")
        run_scraper()
    else:
        print("Invalid choice. Exiting Command Center.")
        sys.exit(1)

if __name__ == "__main__":
    run_app()
