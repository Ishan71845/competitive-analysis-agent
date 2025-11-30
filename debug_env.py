from dotenv import load_dotenv
import os

load_dotenv()

print("\n🔍 DEBUGGING ENVIRONMENT\n")
print("PowerShell env:", os.getenv("GOOGLE_API_KEY"))
print("Raw env list contains GOOGLE_API_KEY:", "GOOGLE_API_KEY" in os.environ)
