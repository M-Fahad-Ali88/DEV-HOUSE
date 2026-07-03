message = input("> ")
words = message.split(" ")

emojis = {
    ":)" : "😊",
    ":(" : "😢"

}
for word in words:
    print(emojis.get(word,word), end = " ")
