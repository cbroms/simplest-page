
def deduce_intention(author, receiver, subject):
    intents = receiver.split("@")[0].split('+')
    intentions = []
    for intent in intents:
        [command, arg] = intent.split("=") if (
            '=' in intent) else [intent, None]
        intentions.append((command, arg))

    return intentions
