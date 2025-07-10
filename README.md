# Family Chatbot

This project is a simple family chatbot that uses Google Gemini AI to answer natural language questions and assist with tasks. The bot's name is Bell.

## Features
- Answers natural language questions
- User-friendly, continuous conversation
- Uses the Google Gemini AI API

## Planned Features
- Multi-user support
- Conversation history and context awareness
- Integration with calendar and reminders
- Voice input and output
- Web or mobile interface
- Customizable personality and response style

## Prerequisites

1. **Install Python**
   - Recommended: Python 3.8 or newer

2. **Install dependencies**
   - (Optional) Create a virtual environment:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - Windows:
       ```bash
       .\venv\Scripts\activate
       ```
     - Linux/Mac:
       ```bash
       source venv/bin/activate
       ```
   - Install the required packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Google API key**
   - Obtain a Google Gemini API key.

## Usage

To start the chatbot:
```bash
python basic_bot.py
```

Then, enter your question or command in the terminal. To exit, type: `bye`, `exit`, or `quit`.

## Main files
- `basic_bot.py` – The main program of the chatbot

## Notes
- The chatbot will only work if the Google API key is provided correctly.
- The project is intended for educational and demonstration purposes only.

## License
This project is free to use and modify, but not recommended for commercial purposes.
