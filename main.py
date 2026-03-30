from graph import graph
from state import AgentState
from utils.logger import update_session_log, save_complaint, get_last_session_id

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()


def run_app():
    console.print(Panel(Text("🤖 Multi-Agent Complaint System", style="bold cyan"), subtitle="Powered by LangGraph"))
    # 🔹 Session Management
    last_id = get_last_session_id()
    session_id = last_id + 1
    initial_query = None
    config = {"configurable": {"thread_id": f"session_{session_id}"}}

    console.print("\n💡 [dim]Type 'exit' at any time to close the application[/dim]")

    while True:
        # 🔹 [PHASE: IDLE]
        update_session_log({"session_id": session_id, "initial_query": initial_query}, phase="idle")
        
        user_query = Prompt.ask("\n[bold green]Enter your query[/bold green]").strip()

        if user_query.lower() == "exit":
            # 🔹 [PHASE: COMPLETED] for exit
            update_session_log({
                "session_id": session_id, 
                "initial_query": initial_query,
                "user_query": "exit",
                "response": "Exiting... Goodbye!"
            }, phase="completed")
            console.print("[bold yellow]👋 Exiting...[/bold yellow]")
            break
            
        if not initial_query:
            initial_query = user_query

        # 🔹 [PHASE: PROCESSING]
        update_session_log({
            "session_id": session_id, 
            "initial_query": initial_query,
            "user_query": user_query
        }, phase="processing")

        # Run the graph
        graph.invoke({
            "user_query": user_query, 
            "initial_query": initial_query, 
            "session_id": session_id,
            "response": None, 
            "intent": None, 
            "flow": []
        }, config=config)

        while True:
            current_state = graph.get_state(config)
            
            # 🏁 If no next nodes, we are done with this turn
            if not current_state.next:
                break

            next_node = current_state.next[0]

            # ⏸️ Handle Interrupt: After Supervisor (Ask for Email)
            if next_node in ["complaint", "info"]:
                intent = current_state.values.get("intent")
                user_email = current_state.values.get("user_email")
                
                # ONLY ask if it's a complaint AND we don't have the email yet
                if intent == "complaint" and not user_email:
                    console.print(Panel("📋 [bold yellow]Info Required:[/bold yellow] This looks like a complaint. We need your email for updates.", border_style="yellow"))
                    user_email = Prompt.ask("[bold cyan]Enter your email[/bold cyan]").strip()
                    graph.update_state(config, {"user_email": user_email})
                
                # Resume
                graph.invoke(None, config=config)

            # ⏸️ Handle Interrupt: Before Human (Ask for Approval)
            elif next_node == "human":
                console.print(Panel(
                    f"Issue: {current_state.values.get('issue')}\n"
                    f"Order ID: {current_state.values.get('order_id')}\n"
                    f"Urgency: [bold red]{current_state.values.get('urgency')}[/bold red]",
                    title="⚠️ [bold red]MANAGER APPROVAL REQUIRED[/bold red]",
                    border_style="red"
                ))
                
                approval = Prompt.ask("[bold red]Approve escalation?[/bold red]", choices=["yes", "no"]).strip().lower()
                
                graph.update_state(config, {"approval": approval})
                
                # Resume
                graph.invoke(None, config=config)
            
            else:
                # Direct resume for any other nodes that might trigger a breakpoint
                graph.invoke(None, config=config)

        # 🔹 [PHASE: COMPLETED]
        final_state = graph.get_state(config).values
        final_state["initial_query"] = initial_query
        
        console.print("\n[bold magenta]✅ Response:[/bold magenta]")
        response = final_state.get("response")
        console.print(Panel(response if response else "No response generated.", border_style="magenta"))

        update_session_log(final_state, phase="completed")
        save_complaint(final_state)

        console.print("\n" + "━" * 100 + "\n")


if __name__ == "__main__":
    run_app()
