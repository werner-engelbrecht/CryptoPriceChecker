# *************************************************************************************************
#                                           Main Code
# *************************************************************************************************

# Call sys.path() to get a list of strings that specifies the
# search paths for modules.
# Call list.append(dir), with dir as "." to add the current
# directory as a path to search for modules.
from Class import PriceChecker
import sys
sys.path.append(".")

# Import the PriceChecker class from the Class file (make it available to this code).

# Create a copy (object) of the PriceChecker class in memory.
# Call it checkerObject.
checkerObject = PriceChecker()

# Load levelsList from the records in levelsFile
checkerObject.readLevelsFromFile()

# Display the levelsList and Menu; and then get user input for what actions to take
userInput = 99
while userInput != 0:
    checkerObject.displayList()
    userInput = checkerObject.displayMenu()
    if(userInput == 1):
        checkerObject.addLevel()
        checkerObject.writeLevelsToFile()  #  Write levelsList to LevelsFile
    elif(userInput == 2):
        checkerObject.removeLevel()
        checkerObject.writeLevelsToFile()  #  Write levelsList to LevelsFile
    elif(userInput == 3):
        checkerObject.removeAllLevels()
        checkerObject.writeLevelsToFile()  #  Write levelsList to LevelsFile
    elif(userInput == 4):
        checkerObject.updateMenuPrice()
    elif(userInput == 5):
        # The timer that we will create in the monitorLevels() method, will run on a separate thread.
        # Since that thread is not controlled by this menu, the user will have to press Cntrl+C repeatedly to stop it.
        # Prevent this “while loop” and main thread from continuing (by pretending that the user entered 0).
        userInput = 0
        # Call the monitorLevels() method
        checkerObject.monitorLevels()
