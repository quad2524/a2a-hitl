
import gradio as gr
import requests

AGENT_URL = "http://127.0.0.1:8000"

def chat_interface(message, history):
    response = requests.post(f"{AGENT_URL}/ask", json={"query": message})
    data = response.json()

    if data.get("confirmation_required"):
        return f"{data['response']}\nDo you want to proceed?", gr.update(visible=True), gr.update(visible=True)
    else:
        return data['response'], gr.update(visible=False), gr.update(visible=False)

def handle_approval(history):
    response = requests.post(f"{AGENT_URL}/execute_task", json={"task": "cut_hair"})
    data = response.json()
    history[-1][1] = data['response']
    return history, gr.update(visible=False), gr.update(visible=False)

def handle_denial(history):
    history[-1][1] = "Okay, I won't do that."
    return history, gr.update(visible=False), gr.update(visible=False)

with gr.Blocks() as demo:
    gr.Markdown("# Human-in-the-Loop Agent Demo")
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    with gr.Row() as buttons:
        approve_button = gr.Button("Approve", visible=False)
        deny_button = gr.Button("Deny", visible=False)

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        user_message = history[-1][0]
        bot_message, approve_visible, deny_visible = chat_interface(user_message, history)
        history[-1][1] = bot_message
        return history, approve_visible, deny_visible

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, [chatbot, approve_button, deny_button]
    ).then(lambda: "", None, msg, queue=False)

    approve_button.click(lambda: (None, gr.update(visible=False), gr.update(visible=False)), [], [chatbot, approve_button, deny_button]).then(handle_approval, [], [chatbot, approve_button, deny_button])
    deny_button.click(lambda: (None, gr.update(visible=False), gr.update(visible=False)), [], [chatbot, approve_button, deny_button]).then(handle_denial, [], [chatbot, approve_button, deny_button])

demo.launch()
