# 🤖 AI Chat Assistant Setup Guide

## Overview

The AI Chat Assistant provides bilingual (Arabic/English) support for understanding drug interaction results. It uses Google's Gemini 2.5 Flash model to generate intelligent, context-aware responses.

## Features

✅ **Automatic Bilingual Summaries**: When users open the chat, they receive an automatic summary in both Arabic and English  
✅ **Context-Aware Responses**: AI has full context of the interaction result  
✅ **Language Detection**: Automatically detects if user is writing in Arabic or English  
✅ **Medical Expertise**: Specialized prompts for drug interaction explanations  
✅ **Safety First**: Always emphasizes consulting healthcare professionals  

## Setup Instructions

### 1. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Configure Environment Variables

Add your Gemini API key to the `.env` file:

```bash
cd Backend
cp .env.example .env
nano .env  # or use your preferred editor
```

Add this line:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install google-generativeai==0.3.2

# Or install all requirements
pip install -r requirements.txt
```

### 4. Test the Service

```bash
cd src
python gemini_service.py
```

You should see:
```
Testing Gemini Chat Service...
============================================================
Generating initial summary...
============================================================

🇬🇧 English Summary:
[Summary in English]

🇦🇪 Arabic Summary:
[Summary in Arabic]

✅ Service test completed successfully!
```

### 5. Start Server with AI Chat

```bash
cd ..
./start_server_firebase.sh
```

Look for this line in the startup logs:
```
✅ Gemini AI Chat Service initialized
```

## API Endpoints

### Generate Initial Summary

**POST** `/chat/summary`

Generates a bilingual summary of an interaction result.

**Request:**
```json
{
  "interaction_id": "abc123",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "success": true,
  "english": "Hello! I've analyzed the interaction between...",
  "arabic": "مرحباً! لقد قمت بتحليل التفاعل بين...",
  "full_text": "🇬🇧 English:\n...\n\n🇦🇪 Arabic:\n...",
  "timestamp": "2025-11-05T18:50:00Z"
}
```

### Send Chat Message

**POST** `/chat/message`

Send a message to the AI assistant.

**Request:**
```json
{
  "interaction_id": "abc123",
  "message": "What should I do if I'm already taking both?",
  "user_id": "user123",
  "chat_history": [
    {
      "role": "user",
      "content": "Previous message"
    },
    {
      "role": "assistant",
      "content": "Previous response"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "response": "🇬🇧 English:\nIf you're already taking both...\n\n🇦🇪 Arabic:\nإذا كنت تتناول كلا الدواءين...",
  "timestamp": "2025-11-05T18:51:00Z",
  "language_detected": "en"
}
```

## Usage in Flutter App

### 1. When User Opens Chat

```dart
// Call summary endpoint
final response = await http.post(
  Uri.parse('$baseUrl/chat/summary'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'interaction_id': interactionId,
    'user_id': userId,
  }),
);

final data = jsonDecode(response.body);
// Display data['english'] and data['arabic'] as initial message
```

### 2. When User Sends Message

```dart
// Call message endpoint
final response = await http.post(
  Uri.parse('$baseUrl/chat/message'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'interaction_id': interactionId,
    'message': userMessage,
    'user_id': userId,
    'chat_history': chatHistory,
  }),
);

final data = jsonDecode(response.body);
// Display data['response'] in chat
```

## Customization

### Modify System Prompt

Edit `Backend/src/gemini_service.py`:

```python
self.system_prompt = """Your custom prompt here..."""
```

### Adjust Response Temperature

In `gemini_service.py`, modify the `generation_config`:

```python
generation_config={
    'temperature': 0.7,  # Lower = more focused, Higher = more creative
    'top_p': 0.9,
    'max_output_tokens': 1024,
}
```

## Troubleshooting

### Error: "GEMINI_API_KEY not found"

**Solution:** Make sure you've added the API key to `.env` file and restarted the server.

### Error: "AI Chat service not available"

**Solution:** Check the server startup logs. If Gemini initialization failed, the error message will explain why.

### Responses are too long/short

**Solution:** Adjust `max_output_tokens` in `gemini_service.py`

### Responses are not bilingual

**Solution:** The system prompt enforces bilingual responses. If this fails, check if you're using the correct Gemini model version.

## Cost Considerations

### Gemini 2.5 Flash Pricing (as of 2024)

- **Free Tier**: 15 requests per minute, 1 million tokens per day
- **Paid Tier**: Very affordable, ~$0.00025 per 1K characters

For a typical app:
- Initial summary: ~500 tokens
- Chat message: ~300 tokens
- **Estimated cost**: <$0.01 per conversation

## Security Best Practices

1. ✅ **Never commit `.env` file** - Already in `.gitignore`
2. ✅ **Use environment variables** - Already configured
3. ✅ **Validate user ownership** - Already implemented in endpoints
4. ✅ **Rate limiting** - Consider adding for production

## Next Steps

1. ✅ Backend setup complete
2. 🔄 Create Flutter chat UI
3. 🔄 Integrate with interaction results screen
4. 🔄 Add chat history persistence
5. 🔄 Add loading states and error handling

## Support

For issues or questions:
- Check the logs: `Backend/logs/` (if configured)
- Test the service: `python src/gemini_service.py`
- Review API docs: `http://localhost:5000/docs`

---

**Created**: 2025-11-05  
**Last Updated**: 2025-11-05  
**Version**: 1.0.0
