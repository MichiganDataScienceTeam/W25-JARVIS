from ollama import ChatResponse, chat

def add_two_numbers(a: int, b: int) -> int:
    """
    Add two numbers

    Args:
        a (int): The first number
        b (int): The second number

    Returns:
        int: The sum of the two numbers
    """
    return int(a) + int(b)

def subtract_two_numbers(a: int, b: int) -> int:
    """
    Subtract two numbers

    Args:
        a (int): The first number
        b (int): The second number

    Returns:
        int: The difference of the two numbers
    """
    return int(a) - int(b)

def search_in_browser(query):
    import webbrowser
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url, new=2)

available_functions = {
    "add_two_numbers": add_two_numbers,
    "subtract_two_numbers": subtract_two_numbers,
    "search_in_browser": search_in_browser
}

def handle_chat(messages):
    response: ChatResponse = chat(
        "llama3.2:latest",
        messages=messages,
        tools=[add_two_numbers, subtract_two_numbers, search_in_browser],
    )
    
    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            function_to_call = available_functions.get(tool.function.name)
            if function_to_call:
                output = function_to_call(**tool.function.arguments)
                messages.append({'role': 'tool', 'content': str(output), 'name': tool.function.name})
                final_response = chat("llama3.2:latest", messages=messages)
                return final_response.message.content
