import gradio as gr
import requests

AGENT_URL = "http://127.0.0.1:8000"

def get_agent_response(history):
    response = requests.post(f"{AGENT_URL}/ask", json={"history": history})
    return response.json()

def handle_approval(history):
    response = requests.post(f"{AGENT_URL}/execute_task", json={"task": "cut_hair"})
    data = response.json()
    history.append({"role": "assistant", "content": data['response']})
    return history, gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)

def handle_denial(history):
    history.append({"role": "assistant", "content": "Okay, I won't do that."})
    return history, gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)

with gr.Blocks() as demo:
    gr.Markdown("# Human-in-the-Loop Agent Demo")
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox()
    with gr.Row():
        approve_button = gr.Button("Approve", visible=False)
        deny_button = gr.Button("Deny", visible=False)

    def user(user_message, history):
        return "", history + [{"role": "user", "content": user_message}]

    def bot(history):
        agent_response = get_agent_response(history)
        history.append({"role": "assistant", "content": agent_response['response']})

        show_buttons = agent_response.get("confirmation_required", False)
        # Hi
        return history, gr.update(visible=show_buttons), gr.update(visible=show_buttons), gr.update(visible=not show_buttons)

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, [chatbot, approve_button, deny_button, msg]
    ).then(lambda: "", None, msg, queue=False)

    approve_button.click(
        handle_approval, chatbot, [chatbot, approve_button, deny_button, msg]
    )

    deny_button.click(
        handle_denial, chatbot, [chatbot, approve_button, deny_button, msg]
    )

if __name__ == "__main__":
    demo.launch()
