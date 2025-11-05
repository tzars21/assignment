from nicegui import ui
import httpx
import asyncio
import json

API_BASE = "http://127.0.0.1:8000"


def start_ui():
    with ui.column().style("width: 800px; margin: 20px"):
        ui.label("RAG Chatbot — NiceGUI demo").classes("text-xl")

        upload = ui.upload(on_upload=None)
        status_label = ui.label("")
        status_label.visible = False

        chat_input = ui.input(
            label="Enter your question", placeholder="Ask about the uploaded PDF"
        )

        output = ui.markdown("### Chat output\n")
        session_id = "demo-session"

        async def send_query(question: str, status_label):
            if not question:
                ui.notify("Please enter a question", color="orange")
                return

            status_label.visible = True
            status_label.text = "Analyzing → Searching → Generating"
            output.text = ""

            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    f"{API_BASE}/chat/stream",
                    json={"session_id": session_id, "query": question},
                ) as resp:
                    if resp.status_code != 200:
                        ui.notify(f"Chat error: {resp.status_code}", color="red")
                        return

                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        try:
                            payload = json.loads(line)
                        except Exception:
                            payload = {"token": line, "done": False}

                        if payload.get("step"):
                            status_label.text = payload["step"]
                        if payload.get("token"):
                            output.text += payload["token"]
                            await asyncio.sleep(0)  # allow UI to update
                        if payload.get("done"):
                            status_label.visible = False
                            ui.notify("Done", color="white")
                            break

        ui.button(
            "Send",
            on_click=lambda: asyncio.create_task(
                send_query(chat_input.value, status_label)
            ),
        )


if __name__ in {"__main__", "__mp_main__"}:
    start_ui()
    ui.run()
