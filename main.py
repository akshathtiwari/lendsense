from agents.lendsense_graph import run_lendsense

print("Lendsense is starting... type 'exit' to quit.")

while True:
    user = input("\nUser: ")
    if user.lower() in {"exit", "quit"}:
        break
    
    print("Assistant:", run_lendsense(user, thread_id="4"))
