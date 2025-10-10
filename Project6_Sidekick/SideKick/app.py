# Fallback dependency installation for Hugging Face Spaces
try:
    import gradio as gr
    from sidekick import Sidekick
except ImportError as e:
    import subprocess
    import sys
    print(f"Missing dependency: {e}")
    print("Installing missing packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio", "langgraph", "langchain", "langchain_community", "langchain-groq", "langchain_core", "python-dotenv", "requests", "typing_extensions", "pydantic", "IPython"])
    import gradio as gr
    from sidekick import Sidekick

async def setup():
    sidekick=Sidekick()
    await sidekick.setup()
    return sidekick

async def process_message(sidekick, message, success_criteria, history):
    results= await sidekick.run_superstep(message, success_criteria, history)
    return results, sidekick

async def reset():
    new_sidekick=Sidekick()
    await new_sidekick.setup()
    return "", "", None, new_sidekick

def free_resources(sidekick):
    print("Cleaning Up")
    try:
        if sidekick:
            sidekick.free_resources()
    except Exception as e:
        print(f"Exception during cleanup : {e}")

with gr.Blocks(theme=gr.themes.Default(primary_hue="emerald")) as demo:
    gr.Markdown("## Sidekick Personal Co-worker")
    sidekick=gr.State(delete_callback=free_resources)

    with gr.Row():
        chatbot = gr.Chatbot(label="Sidekick", height=450, type="messages")
    with gr.Group():
        with gr.Row():
            message = gr.Textbox(show_label=False, placeholder="Your request to Sidekick")
        with gr.Row():
            # Instead of empty or vague criteria, provide better defaults
                success_criteria = gr.Textbox(
                    show_label=False, 
                    placeholder="Success criteria (e.g.: Provide current exchange rate with source)",
                    value="Provide accurate, helpful information that addresses the user's question"
                    )
    with gr.Row():
        reset_button = gr.Button("Reset",variant="stop")
        go_button = gr.Button("Go!", variant="primary")

    demo.load(setup, [], [sidekick])
    message.submit(process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick])
    success_criteria.submit(process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick])
    go_button.click(process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick])
    reset_button.click(reset, [], [message, success_criteria, chatbot, sidekick])


demo.launch(share=False, debug=True, inbrowser=True)