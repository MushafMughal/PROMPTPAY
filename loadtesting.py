import requests
import concurrent.futures
import json
import time
import random

# API URL
url = "http://localhost:8000//api/extract/"
headers = {"Content-Type": "application/json"}

# List of different payloads
payloads = [
    {"user_input": "i want to send money in meezan bank"},
    {"user_input": "i want to send money"},
    {"user_input": "send money to shaz in HBL"},
    {"user_input": "send money to account PK23412421412 nayapay to mushaf"},
    {"user_input": "transfer 5000 to Ali in UBL"},
    {"user_input": "wire 100 dollars to my dad in Dubai"},
    {"user_input": "make a payment to JazzCash for bill"},
    {"user_input": "fund transfer to Standard Chartered for Sarah"},
    {"user_input": "move funds to EasyPaisa wallet"},
    {"user_input": "deposit 10,000 PKR to my savings account in MCB"}
]

# Number of concurrent requests
num_requests = 500

def send_request():
    payload = random.choice(payloads)  # Select a random payload
    try:
        response = requests.post(url, json=payload, headers=headers)
        return {"payload": payload, "response": response.json()} if response.status_code == 200 else {"payload": payload, "error": response.text}
    except Exception as e:
        return {"payload": payload, "error": str(e)}

def main():
    results = []

    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(send_request) for _ in range(num_requests)]
        
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    # Save responses to a JSON file
    with open("stress_test_results.json", "w") as file:
        json.dump(results, file, indent=4)
    
    print(f"Stress test completed. Results saved to 'stress_test_results.json'")
    print(f"Time taken: {time.time() - start_time} seconds")

if __name__ == "__main__":
    main()
