# PromptPay

PromptPay is an AI-powered conversational banking solution that serves as the backend for a full-featured Android banking application. It leverages advanced LLMs to understand natural language inputs and execute real-time banking operations securely through a Django REST API framework.

## Features

- **Dual-Mode Chatbot Architecture**:
  - **RAG-based FAQ Assistant**: Uses LLaMA for contextual query answering with document retrieval
  - **Agent Mode**: Powered by Qwen 2.5, enables natural language banking operations

- **Intelligent Banking Operations**:
  - **Money Transfers**: Process transfers with entity extraction from natural language
  - **Bill Payments**: Pay bills by detecting consumer numbers and amounts
  - **Account Management**: View balance, update settings, and manage banking details
  - **Password Change**: Securely manage credentials through conversation

- **Autonomous Agent Capabilities**:
  - **Intent Recognition**: Automatically routes requests to appropriate handlers
  - **Entity Extraction**: Identifies account numbers, amounts, recipient names, and other transaction details
  - **Follow-up Management**: Intelligently handles missing information collection
  - **API Integration**: Executes real banking operations via secure REST endpoints

- **Enterprise-Grade Security**:
  - **JWT Authentication**: Secure token-based access control
  - **Token Blacklisting**: Prevents unauthorized token reuse
  - **Custom Middleware**: Additional security layers for enhanced protection

## Technology Stack

- **Backend Framework**: Django with Django REST Framework
- **Database**: MySQL (with SQLite for development)
- **Authentication**: JWT (JSON Web Tokens) with token refresh and blacklisting
- **LLM Integration**:
  - **Qwen 2.5** (14B/32B): Primary agent for banking operations
  - **LLaMA 3.3** (70B): Used for RAG-based FAQ assistance
  - **Langchain**: For LLM orchestration and RAG implementation
  - **Ollama**: For local model hosting and inference
  - **Chroma DB**: Vector storage for document retrieval

## Installation

**1. Clone this repository:**

   ```bash
   git clone https://github.com/MushafMughal/PROMPTPAY.git
   cd promptpay
   ```

**2. Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

**3. Set up your environment:**

   - Configure your database in `PROMPTPAY/settings.py`
   - Ensure you have the required LLM models available (Qwen 2.5, LLaMA)
   - Replace API keys in relevant files with your own keys

**4. Run migrations and start the server:**

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Key Components

### 1. **Router System**
The `router` function intelligently directs user queries to the appropriate handler:
- **Transfer Money**: Processes fund transfers between accounts
- **Bill Payment**: Manages utility and service bill payments
- **Password Changes**: Handles secure credential updates
- **General Queries**: Routes to the RAG system for FAQ handling

### 2. **Entity Recognition**
The `extract_entities` function identifies key transaction details from natural language:
- `account_number`: Target account for transactions
- `amount`: Transaction value
- `bank_name`: Financial institution
- `recipient_name`: Beneficiary information

### 3. **Transaction Processing**
Complete end-to-end transaction flow:
1. Intent detection via router
2. Entity extraction from natural language
3. Missing information collection
4. Confirmation and verification
5. Secure API execution with proper authentication

### 4. **RAG-based Knowledge Base**
Retrieval-Augmented Generation for contextual FAQ responses:
- Document indexing and chunking
- Vector-based similarity search
- Context-aware response generation
- Fallback mechanisms for unanswerable queries

## API Endpoints

The system exposes several RESTful endpoints:

- **`/chatbot/router/`**: Main entry point for processing natural language inputs
- **`/chatbot/transfer/`**: Handles money transfer operations
- **`/core_banking/account/`**: Retrieves account details
- **`/core_banking/card/`**: Manages card information
- **`/core_banking/payees/`**: Controls beneficiary management
- **`/authentication/`**: Handles user authentication and session management

## Use Cases

- **Conversational Banking**: "Send $500 to John's account at ABC Bank"
- **Bill Management**: "Pay my electricity bill for this month"
- **Account Inquiries**: "What's my current balance?"
- **Security Operations**: "I need to change my password"
- **General Assistance**: FAQ and help requests through the RAG system

## Development Roadmap

- **Enhanced Multi-Modal Support**: Integrate image processing for check deposits and document verification
- **Predictive Financial Insights**: Add ML-based spending analysis and recommendations
- **Cross-Platform Integration**: Extend API support for web and additional mobile platforms
- **Advanced Transaction Monitoring**: Real-time fraud detection using ML algorithms
- **Voice Integration**: Add speech-to-text capabilities for voice banking

## Contribution

We welcome contributions! To contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For major changes, please open an issue first to discuss what you would like to change.
