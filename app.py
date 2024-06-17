import threading
from time import sleep
from flask import Flask, render_template, request, jsonify
import cohere
import random

app = Flask(__name__)
responses = ["", "", ""]
response_locks = [threading.Lock() for _ in range(3)]

def make_api_call(thread_id, max_tokens, temperature, system_message, user_message, presence_penalty):
    try:
        client = cohere.Client(api_key="")
        response = client.chat(
            model="command-r-plus",
            preamble=f"{system_message} {random.randint(1, 1000000000000000)}",
            message=user_message,
            temperature=float(temperature),
            max_tokens=int(max_tokens),
            presence_penalty=float(presence_penalty),  # Adding presence_penalty parameter
            seed=random.randint(1, 9999999)
        )
        with response_locks[thread_id]:
            responses[thread_id] = response.text
    except Exception as e:
        with response_locks[thread_id]:
            responses[thread_id] = f"Error: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    max_tokens = request.form.get('max_tokens')
    temperature = request.form.get('temperature')
    system_message = request.form.get('system_message')
    user_message = request.form.get('user_message')
    presence_penalty = request.form.get('presence_penalty')  # Default presence_penalty to 0.5

    threads = []
    for i in range(3):
        thread = threading.Thread(target=make_api_call, args=(
            i, max_tokens, temperature, system_message, user_message, presence_penalty
        ))
        threads.append(thread)
        thread.start()
        sleep(5)

    for thread in threads:
        thread.join()

    return jsonify(responses)

if __name__ == '__main__':
    app.run(debug=True)
