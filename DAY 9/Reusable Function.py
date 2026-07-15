def reusableFunc(message):
    wording = message.split(" ")
    return wording
emojis = {
    ":)" : "😊",
    ":(" : "😢 "
    } 


message = input("> ")
wording  = reusableFunc(message)
for word in wording:
        print(emojis.get(word,word), end = " ")
