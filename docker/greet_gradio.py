import gradio as gr
import os 

SERVER_NAME = os.environ.get("SERVER_NAME", "127.0.0.1")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "7860"))

def greet(x, n):
    return (x+"\n")*n

def greet_interface(greeting: str, times: int):
    return greet(greeting, times)

interface = gr.Interface(
    fn=greet_interface,
    inputs=["text", "number"],
    outputs="text",
    title="Greet App",
    description="A simple app that repeats a greeting a number of times."
)

if __name__ == "__main__":
    interface.launch(server_name=SERVER_NAME, server_port=SERVER_PORT)