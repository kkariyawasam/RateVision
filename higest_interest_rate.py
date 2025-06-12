import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
from openai import OpenAI

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Check the key

if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    print("API key found and looks good so far!")

openai = OpenAI()

# message = "Hello, GPT! This is my first ever message to you! Hi!"
# response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user", "content":message}])
# print(response.choices[0].message.content)

system_prompt = """
You are a web content analyzer. Your task is to extract the interest rate for a one-year fixed deposit from the provided webpage content.
Focus only on the relevant information and ignore unrelated text. If no information about a one-year fixed deposit is found, respond with 'Interest rate for a one-year fixed deposit not found.'
"""

# Step 2: Fetch webpage content (scraping)
bank_urls = [
    "https://www.combank.lk/business-banking/domestic-banking/fixed-deposits",  
    "https://www.peoplesbank.lk/interest-rates/",                               
    "https://www.nationstrust.com/deposit-rates"
]

bank_results = {}

for url in bank_urls:
    try:
        # Fetch webpage content
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        webpage_content = soup.get_text()

        # Define user prompt for the current bank
        user_prompt = f"""
        Analyze the following content extracted from a bank's website and find the interest rate for a one-year fixed deposit:
        {webpage_content}
        """

        # Step 4: Prepare the messages list
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Step 5: Call OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Replace with the correct model ID
            messages=messages
        )

        result = response.choices[0].message.content
        bank_results[url] = result

    except Exception as e:
        bank_results[url] = f"Error: {e}"

highest_rate = 0.0
highest_rate_bank = None

for url, result in bank_results.items():
    # Extract numeric value of interest rate from the result
    try:
        if "not found" not in result.lower():
            # Find numbers (assumes interest rate is a percentage)
            rate = float(next(filter(lambda x: "%" in x, result.split())).replace("%", ""))
            if rate > highest_rate:
                highest_rate = rate
                highest_rate_bank = url
    except Exception:
        pass  # Ignore errors during rate extraction

print("Bank Results:")
for url, result in bank_results.items():
    print(f"{url}: {result}")

if highest_rate_bank:
    print(f"\nThe highest interest rate for a one-year fixed deposit is {highest_rate}% at {highest_rate_bank}.")
else:
    print("\nNo valid interest rates found for a one-year fixed deposit.")


