
def deduce_intention(author, receiver, subject):
    print(author, receiver, subject)
    intents = receiver.split("@")[0].split('+')
    intentions = []
    for intent in intents:
        [command, arg] = intent.split("=")
        intentions.append((command, arg))

    return intentions
