import bitmex
import json
import threading
from datetime import datetime
import winsound


class Tick():
    def __init__(self, time, price):
        self.time = time
        self.price = price


class PriceChecker():
    # Constructor/Initializer
    def __init__(self):
        self.levelsList = []
        self.currentPrice = 0.0
        self.BitmexClient = bitmex.bitmex(test=False)
        self.PreviousPrice = 0.0

    # Class Methods
    # =============

    # Method: Sort and Display the levelsList
    def displayList(self):
        print(chr(27) + "[2J")  # Clear the screen
        print(" ")
        print("Price Levels In The List")
        print("========================")
        # Sort the list in reverse order
        self.levelsList.sort(reverse=True)
        # Print the items in the list (Based on the above sort, numbers should appear from large to small.)
        for level in self.levelsList:
            print(f'${level: ,}')

    # Display the menu and get user input about what methods to execute next
    def displayMenu(self):
        min = 0
        max = 5
        errorMsg = "Please enter a valid option between " + \
            str(min) + " and " + str(max)

        print(" ")
        print("MENU OPTIONS")
        print("============")
        print("1. Add a price level")
        print("2. Remove a price level")
        print("3. Remove all price levels")
        if(self.currentPrice > 0):
            print("4. Display the current Bitcoin price here: " +
                  f"${self.currentPrice:,}")
        else:
            print("4. Display current Bitcoin price here")
        print("5. Start the monitoring")
        print("0. Exit the program")
        print(" ")

        # Get user input. Keep on requesting input until the user enters a valid number between min and max
        selection = 99
        while selection < min or selection > max:
            try:
                selection = int(input("Please enter one of the options: "))
            except:
                print(errorMsg)  # user did not enter a number
                continue  # skip the following if statement
            if(selection < min or selection > max):
                # user entered a number outside the required range
                print(errorMsg)
        # When this return is finally reached, selection will have a value between (and including) min and max
        return selection

    # Method: Append a new price level to the levelsList
    def addLevel(self):
        try:
            # Let the user enter a new float value and append it to the list
            leveladd = float(input('Please enter a level: '))
            self.levelsList.append(leveladd)
        except:
            # Print and error message if the user entered invalid input
            print('*sorry wrong input*')

    # Method: Remove an existing price level from the levelsList
    def removeLevel(self):
        try:
            # Let the user enter a new float value. If found in the list, remove it from the list
            levelremove = float(
                input('Please enter a level you want to remove: '))
            if levelremove in self.levelsList:
                self.levelsList.remove(levelremove)
        except:
            # Print and error message if the user entered invalid input
            print('*Sorry wrong input*')

    # Method: Set levelsList to an empty list
    def removeAllLevels(self):
        # Set levelsList to an empty list
        self.levelsList.clear()

        # Method: Load levelsList using the data in levelsFile 
    def readLevelsFromFile(self):
        try:
            # Set levelsList to an empty list 
            self.levelsList = []
            # Open the file
            file = open('levelsFile.txt')
            # Use a loop to read through the file line by line
            for level in file:
                # This code is inside the loop:
                # Convert the line to a float and then append it to levelsList
                level = float(level)
                self.levelsList.append(level)
            # Close the file
            file.close()
        except:
            return

    # Method: Write levelsList to levelsFile (override the existing file)
    def writeLevelsToFile(self):
        # Open the file in a way that will override the existing file (if it already exists)
        f = open('levelsFile.txt', 'w')
        # Use a loop to iterate over levelsList item by item
        for level in self.levelsList:
            # This code is inside the loop:
            # Convert everything in the item to a string and then add \n to it - before writing it to the file
            level = str(level) + '\n'
            f.write(level)
        # Close the file
        f.close

    # Function: Update the value of currentPrice – to be displayed with menu item 4
    def updateMenuPrice(self):
        # Get the latest Bitcoin info (as a Tick object) from getBitMexPrice(). Name it tickObj.
        tickObj = self.getBitMexPrice()
        # Update the currentPrice variable with the Bitcoin price stored in tickObj.
        self.currentPrice = tickObj.price

    # Function: Call the Bitmex Exchange
    def getBitMexPrice(self):
        # Send a request to the exchange for data.
        # The XBTUSD data is extracted from the json and converted into a tuple which we name responseTuple.
        responseTuple = self.BitmexClient.Instrument.Instrument_get(
            filter=json.dumps({'symbol': 'XBTUSD'})).result()
        # The tuple contains, amongst others, the Bitcoin information (in the form of a dictionary with key=>value pairs)
        # plus some additional meta data received from the exchange.
        # Extract only the dictionary section from the tuple.
        responseDictionary = responseTuple[0:1][0][0]
        # Create a Tick object and set its variables to the timestamp and lastPrice data from the dictionary.
        return Tick(responseDictionary["timestamp"], responseDictionary['lastPrice'])

    # Once this method has been called, it uses a Timer to execute itself every 2 seconds
    def monitorLevels(self):

        red = '\033[41m'
        green = '\033[42m'
        blue = '\033[44m'
        RESET = "\033[0;0m"
        # Create timer to call this method every 2 seconds on a different thread
        threading.Timer(2.0, self.monitorLevels).start()

        # Since we will obtain the latest current price from the exchange,
        # store the existing value of currentPrice in previousPrice
        self.previousPrice = self.currentPrice

        # Similar to updateMenuPrice(), call the getBitMexPrice() method to get
        # a Ticker object containing the latest Bitcoin information. Then store
        # its Bitcoin price in currentPrice
        tickObj = self.getBitMexPrice()
        self.currentPrice = tickObj.price

        # During the first loop of this method, previousPrice will still be 0 here,
        # because it was set to currentPrice above, which also was 0 before we updated
        # it above via getBitMexPrice().
        # So, when we reach this point during the first loop, previousPrice will be 0
        # while currentPrice would have just been updated via getBitMexPrice().
        # We don't want to create the impression that the price shot up from 0 to
        # currentPrice.
        # Therefore, if previousPrice == 0.0, it must be set equal to currentPrice here.
        if self.previousPrice == 0.0:
            self.previousPrice = self.currentPrice

        # Print the current date and time plus instructions for stopping the app while this
        # method is looping.
        print('')
        print('Price Check at ' + str(datetime.now()) +
              '   (Press Ctrl+C repeatedly to stop the monitoring)')
        print('============================================================================================')

        # Each time this method executes, we want to print the items in levelsList together with previousPrice
        # and currentPrice - in the right order. However, as we loop through levelsList, how do we know where to
        # insert previousPrice and currentPrice - especially if currentPrice crossed one or two of our price
        # levels?
        # We could try to use an elaborate set of IF-statements (I dare you to try this), but a much easier
        # way is to simply add previousPrice and currentPrice to the list and then sort the list.
        #
        # However, we cannot simply use levelsList for this purpose, because it only stores values, while we
        # also want to print labeling text with these values - such as 'Price Level', 'Current Price' and
        # 'Previous Price'.
        # Therefore, we need to create a temporary list - called displayList - used for displaying purposes only.
        # This new list must consist of sub-lists. Each sub-List will contain two items.
        # The first item will be the display-data we want to print - consisting of the labeling text and the price.
        # The second item consists of the price only.
        # We will use the second item to sort the list - since it makes no sense to sort the list based on
        # the label (the first item).
        #
        # Example of displayList (containing sub-lists) after it was sorted:
        #
        #       [
        #           ['Price Level:    9700.00',    9700.00],
        #           ['Price Level:    9690.00',    9690.00],
        #           ['Current Price:  9689.08',    9689.08],
        #           ['Previous Price: 9688.69',    9688.69],
        #           ['Price Level:    9680.00',    9680.00],
        #       ]

        # Create displayList
        displayList = []

        # Loop through the prices in levelsList.
        # During each loop:
        # - Create a sublist consisting of display-data and the price.
        #   The display-data must consist of the text 'Price Level:    ' followed by the price.
        # - Append the sub-List to displayList.
        for price in self.levelsList:
            sublist = [f'Price level: ${str(price)}', price]
            displayList.append(sublist)

        # Create a sublist consisting of display-data and the previousPrice.
        # The display-data must consist of the text 'Previous Price:    ' followed by the
        # value in the previousPrice variable.
        # Append the sub-List to displayList.
        displayList.append(
            [f'{blue}Previous Price: ${str(self.previousPrice)}{RESET}', self.previousPrice])

        # Create a sublist consisting of display-data and the currentPrice.
        # The display-data must consist of the text ‘Current Price:    ' followed by the
        # value in the currentPrice variable.
        # Append the sub-List to displayList.
        if self.currentPrice > self.previousPrice:
            displayList.append(
                [f'{green}Current Price: ${str(self.currentPrice)}{RESET}', self.currentPrice])
        elif self.currentPrice < self.previousPrice:
            displayList.append(
                [f'{red}Current Price: ${str(self.currentPrice)}{RESET}', self.currentPrice])
        elif self.currentPrice == self.previousPrice:
            displayList.append(
                [f'{blue}Current Price: ${str(self.currentPrice)}{RESET}', self.currentPrice])

        # Sort displayList using the SECOND item (price) in its sub-lists
        displaylist2 = sorted(displayList, key=lambda x: x[1], reverse=True)

        # For each sub-List in displayList, print only the FIRST item (display-data) in the sub-List
        for i in displaylist2:
            print(i[0])

            alarm = False
            # Loop through displayList
        for i in displaylist2:
            # for i in range(0,len(displayList)):
            # Test if the sub-list in the current loop contains the text "Price Level“
            # Tip: Remember that each sub-list is a list within a list (displayList). So you have
            # to access its items via displayList followed by TWO indexes.
            # Extract the second item from the current sub-list into a variable called priceLevel
            if 'Price level' in i[0]:
                priceLevel = i[1]
                # Test if priceLevel is between previousPrice and currentPrice OR
                #         priceLevel == previousPrice OR
                #         priceLevel == currentPrice
                if(self.previousPrice > priceLevel > self.currentPrice or
                        self.previousPrice < priceLevel < self.currentPrice or
                        priceLevel == self.previousPrice or
                        priceLevel == self.currentPrice):
                    # Sound the alarm. Pass in the frequency and duration.
                    if self.currentPrice > self.previousPrice:
                        frequency = 800
                        duration = 700
                    else:
                        frequency = 400
                        duration = 700
                    winsound.Beep(frequency, duration)
                    alarm = True

                    # Print the text 'Alarm' with a green background colour, so that the user
                    # can go back into the historical data to see what prices raised the alarm.
            if alarm:
                print(f'{green}ALARM!!!{RESET}')
                alarm = False
