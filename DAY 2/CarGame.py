print("========== CAR GAME ==========")

g=""
started = False
while True:
    g=input("<")
    if g=='help':
        print("""
start - to start the car
stop - to stop the car
quit - to exit
        """)
    elif g == 'start':
        if started:
            print("Car is already started!")
        else:
            started = True
            print("Car started...Ready to go!")
    elif g == 'stop':
        if not started:
            print("Car is already stopped!")
        else:
            started = False
            print("Car stopped.")
    elif g == 'quit':
        break;
    else:
        print("I dont't understand that...")