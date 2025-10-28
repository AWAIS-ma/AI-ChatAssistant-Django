import requests
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

API_URL = "base URL of Model"
MODEL = "Your LLM Model"
API_KEY = "Your API key "  

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

MAX_TOKENS = 1000

def call_chat_api(messages):
   
    messages = messages[-6:]
    data = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
    }
    response = requests.post(API_URL, headers=HEADERS, json=data)
    if response.status_code == 200:
        res_json = response.json()
        return res_json['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"

@csrf_exempt
def assistant(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    if request.method == "POST":
        user_input = request.POST.get("user_input", "").strip()
        if user_input:
            chat_history = request.session['chat_history']

            # Append user query
            chat_history.append({"role": "user", "content": user_input})

            # Veterinary-specialized bot response
            # Here we inject context for veterinary domain
            vet_prompt = (
                "You are a professional assistant. "
                "Your role is to analyze question and provide detail:\n"
                "Always keep your answer structured, clear, and practical.\n\n"
                f"squery: {user_input}"
            )

            # Call to AI model with vet-focused prompt
            bot_response = call_chat_api(chat_history + [{"role": "system", "content": vet_prompt}])

            # Append assistant's answer
            chat_history.append({"role": "assistant", "content": bot_response})

            request.session['chat_history'] = chat_history
            request.session.modified = True

    # Preparing history for display
    display_history = []
    for msg in request.session.get('chat_history', []):
        sender = 'user' if msg['role'] == 'user' else 'bot'
        display_history.append({'sender': sender, 'text': msg['content']})

    return render(request, "chat.html", {"chat_history": display_history})

@csrf_exempt
def clear_chat(request):
    if request.method == "POST":
        if 'chat_history' in request.session:
            del request.session['chat_history']
            request.session.modified = True
    return redirect('assistant')

def home(request):
    return render(request, 'home.html')
