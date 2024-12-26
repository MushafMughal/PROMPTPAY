# PromptPay

PromptPay is an innovative integration of Mistral and Gemini models designed to streamline banking tasks through intuitive natural language prompts. Perform actions like sending money, paying bills, retrieving account statements, and more—quickly and securely, all in one seamless experience.

## Features

- **Seamless Classification**: Automatically classifies user intents into three categories (`MISTRAL`, `TRANSFER`, or `IRRELEVANT`) to handle banking requests appropriately.
- **Entity Extraction**: Identifies essential information such as account numbers, amounts, recipient names, and bank names from user inputs.
- **Follow-Up Automation**: Guides users in filling missing details and confirms transactions for a complete banking workflow.
- **Safety Controls**: Utilizes Google's safety settings to mitigate inappropriate or harmful prompts.

## Installation

**1. Clone this repository:**

   ```bash
   git clone https://github.com/MushafMughal/PROMPTPAY.git
   cd promptpay
   ```

**2. Install dependencies:**

   ```bash
   pip install google-generativeai
   ```
**3. Set up your API key:**

   Replace the placeholder api_key in the code with your Google Generative AI API key.

## Usage
### Key Functionalities

### 1. **Classification**
The `classifier_model` function categorizes user inputs into one of the following three categories:
- **MISTRAL**: Handles general banking queries and frequently asked questions (FAQs).
- **TRANSACTION**: Manages money transfers, bill payments, and similar transaction-related requests.
- **IRRELEVANT**: Filters out unrelated or invalid queries to streamline processing.

### 2. **Entity Recognition**
The `ner_model` function extracts key details from user inputs required for processing transactions, including:
- `account_number`: The account number involved in the transaction.
- `amount`: The monetary amount specified.
- `bank_name`: The name of the bank.
- `recipient_name`: The recipient's name.

### 3. **Follow-Up**
The `follow_up_model` function ensures that all missing transaction details are collected and verifies the user's intent to proceed. It helps maintain accuracy and completion in user interactions.

## How It Works
1. **Input Classification**: When a user submits a query, the `classifier_model` determines whether it is a general query, a transfer request, or irrelevant.
2. **Entity Extraction**: For transfer-related queries, the `ner_model` identifies essential transaction details.
3. **Follow-Up Process**: If any details are missing, the `follow_up_model` prompts the user to provide the required information and confirms their intent to proceed.

## Use Cases
- Automating responses to general banking FAQs.
- Streamlining the process of handling money transfers and bill payments.
- Filtering irrelevant queries to focus on actionable inputs.

### Example
```python
user_input = "I want to transfer $500 to John Doe at ABC Bank."

# Step 1: Classify the input
category = classifier_model(user_input)
if category.strip() == "TRANSACTION":
    # Step 2: Extract transaction details
    transaction_details = ner_model(user_input)
    
    # Step 3: Follow up if necessary
    follow_up_needed = any(value is None for value in parsed_response.values())
    if follow_up_needed:
      followup_response = follow_up_model(transaction_details)
      print(followup_response)
    else:
      print("Transaction is ready to be processed.")
else:
    print("Query classified as:", category.strip())
```

## Configuration
The app uses robust safety settings to prevent inappropriate responses:
```python
safe = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
```

These settings ensure compliance with ethical guidelines and user safety.


## Roadmap
 - **Mistral Integration:** Enhance support for banking FAQs and natural conversations.
 - **Multi-Language Support:** Expand accessibility to users across different languages.
 - **Extended Banking Features:** Include bill payment and account statement retrieval.

## Contribution
We welcome contributions! Here's how you can help:
 - Fork the repository.
 - Create a branch for your feature or bug fix.
 - Submit a pull request with a detailed explanation of your changes.

For significant changes, please open an issue to discuss your ideas before proceeding.
