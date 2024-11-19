from game import location
import random
import game.location as location
import game.display as display
import game.combat as combat
import game.event as event
import game.config as config
class Island (location.Location):

    def __init__ (self, x, y, w):
        super().__init__(x, y, w)
        self.name = "parker island"
        self.symbol = 'P'
        self.visitable = True
        self.locations = {}
        self.locations["stonebeach"] = Stone_Beach(self)
        self.locations["golemgrove"] = GolemGrove(self)
        self.locations["holepuzzle"] = HolePuzzle(self)
    
        self.starting_location = self.locations["stonebeach"]

    def enter (self, ship):
        display.announce ("arrived at an island", pause=False)

class Stone_Beach (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "stonebeach"
        self.verbs['south'] = self

    def enter (self):
        display.announce ("You arrive at this barren island that is just covered in stone. Your ship is anchored on the south side")

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south"):
            display.announce ("You return to your ship.")
            self.main_location.end_visit()
        elif (verb == "west"):
            config.the_player.next_loc = self.main_location.locations["golemgrove"]
        elif (verb == "north"):
            config.the_player.next_loc = self.main_location.locations["holepuzzle"]
        
        
class GolemGrove(location.SubLocation):
    def __init__ (self,m):
        super().__init__(m)
        self.name = "golemgrove"
        self.verbs['east'] = self
        self.verbs['south'] = self

        self.event_chance = 99
        self.events.append(Golems())

    def enter (self):
        display.announce("You travel to the west side of the island, the ground starts to shake.")

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south"):
            display.announce ("You return to your ship.")
            self.main_location.end_visit()
    
        #elif #need to do center      

class StoneGolem(combat.Monster):
    def __init__(self, name):
        attacks = {}
        attacks["punch"] = ["punches", random.randrange(35,51), (5,15)]
        attacks["crush"] = ["crushes", random.randrange(35,51), (5,15)]
        attacks["stomp"] = ["stomps", random.randrange(35,51), (5,15)]
        #40 to 50 hp, 35 to 55 speed (100 is "normal")
        super().__init__(name,random.randrange(40,51), attacks, 65 + random.randrange(-10,11))
        self.type_name = "Stone Golem"
    
        
class Golems(event.Event):
    def __init__ (self):
        self.name = " golem attack"
    
    def process (self,world):
        result = {}
        result["message"] = "The stone golems crumble to the ground, becoming a pile of rocks!"
        monsters = []
        n_appearing = random.randrange(2,4)
        n = 1
        while n <= n_appearing:
            monsters.append(StoneGolem("Stone Golem " + str(n)))
            n += 1
        display.announce("Rising and forming from the ground, is a group of Stone Golems!")
        combat.Combat(monsters).combat()
        if random.randrange(2) == 0:
            result["newevents"] = [ self ]
        else:
            result["newevents"] = [ ]

        return result
        

class HolePuzzle(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "holepuzzle"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['west'] = self
        self.verbs['cut'] = self
        self.rope = HolePuzzle.GetRopeColor()

    def enter(self):
        description = "You walk into the crater in the center of the island. All you see is a stone pillar and on each side is a four rope with four different colors Maybe you should cut one."
        display.announce(description)


    def process_verb (self, verb, cmd_list, nouns):
        destroy_island = False
        area_discovered = False 
        if destroy_island == False:
            if verb == "south":
                config.the_player.next_loc = self.main_location.locations["stonebeach"]
            if verb == "west":
                config.the_player.next_loc = self.main_location.locations["golemgrove"]
            if verb == "north":
                if area_discovered:
                    display.announce("You travel North to the treasure location")
                else:
                    display.announce("Theres no way to go North")
        

        if verb == "cut":
            cutRope = False
            while(not cutRope):
                
                ropeChoice = display.get_text_input("There is a red, blue, green and purple rope. Which color would you like to cut? ")
                ropeChoice = ropeChoice.lower()
                print(ropeChoice)
                
                if("leave" in ropeChoice.lower()):
                    return
                
                
                if (ropeChoice == "red" or ropeChoice == "blue" or ropeChoice == "green" or ropeChoice == "purle"):
                    if(ropeChoice == self.rope):
                        display.announce("A chime plays below and you see to the north, a set of stairs carves itself into the crater.")
                        area_discovered = True
                    else:
                        display.announce("The statue shifts open and lava starts to pool and fill the crevice")
                        destroy_island = True
                    
                    cutRope = True
            


            
        

    def GetRopeColor():
        listOfRopes = ["red", "blue", "green", "purple"]
        return random.choice(listOfRopes)
    

        #need to add cut verb with 4 differnet rope colors that hints to moss field
        #need to add other color rope with the lava consequence
        #need to add north with treasures if red was cut
