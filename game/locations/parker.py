from game import location
from game.items import Item
from game.display import menu
import random

import game.location as location
import game.display as display
import game.combat as combat
import game.event as event
import game.config as config
import game.crewmate as crewmate

class Island (location.Location): #main Island class

    def __init__ (self, x, y, w):
        super().__init__(x, y, w)
        self.name = "parker island"
        self.symbol = 'P'
        self.visitable = True
        self.locations = {}
        self.locations["stonebeach"] = Stone_Beach(self)
        self.locations["golemgrove"] = GolemGrove(self)
        self.locations["holepuzzle"] = HolePuzzle(self)
        self.locations["treasurecliff"] = TreasureCliff(self)
        self.locations["mossmeadow"] = MossMeadow(self)
    
        self.starting_location = self.locations["stonebeach"]

    def enter (self, ship):
        display.announce ("arrived at an island", pause=False)

class Stone_Beach (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "stonebeach"
        self.verbs['south'] = self

    def enter (self):
        display.announce ("You arrive at this barren island that is just covered in stone. Your ship is anchored on the south side.")

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south"):
            display.announce ("You return to your ship.")
            self.main_location.end_visit()
        elif (verb == "west"):
            config.the_player.next_loc = self.main_location.locations["golemgrove"]
        elif (verb == "north"):
            config.the_player.next_loc = self.main_location.locations["holepuzzle"]
        elif (verb == "east"):
            config.the_player.next_loc = self.main_location.locations["mossmeadow"]
        
class GolemGrove(location.SubLocation): #west size battle zone of island
    def __init__ (self,m):
        super().__init__(m)
        self.name = "golemgrove"
        self.verbs['east'] = self
        self.verbs['south'] = self

        self.event_chance = 100
        self.events.append(Golems())

    def enter (self):
        display.announce("You travel to the west side of the island, the ground starts to shake.")

    def process_verb (self, verb, cmd_list, nouns):
        if verb == "south":
                config.the_player.next_loc = self.main_location.locations["stonebeach"]
        if verb == "east":
                config.the_player.next_loc = self.main_location.locations["holepuzzle"]
    
            

class StoneGolem(combat.Monster): #stone golem combat class
    def __init__(self, name):
        attacks = {}
        attacks["punch"] = ["punches", random.randrange(35,51), (5,15)]
        attacks["crush"] = ["crushes", random.randrange(35,51), (5,15)]
        attacks["stomp"] = ["stomps", random.randrange(35,51), (5,15)]
        #40 to 50 hp, 35 to 55 speed (100 is "normal")
        super().__init__(name,random.randrange(40,51), attacks, 65 + random.randrange(-10,11))
        self.type_name = "Stone Golem"
    
        
class Golems(event.Event):  #golem event
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
        result["newevents"] = [ self ]
       
        return result
        

class HolePuzzle(location.SubLocation): #center of island
    def __init__(self, m):
        super().__init__(m)
        self.name = "holepuzzle"
        self.verbs['north'] = self
        self.verbs['east'] = self
        self.verbs['south'] = self
        self.verbs['west'] = self
        self.verbs['cut'] = self
        self.flag = False
        self.area_discovered = False
        self.crater_filled = False
        self.rope = HolePuzzle.GetRopeColor()

    def enter(self):
        if self.area_discovered and not self.crater_filled:
            display.announce("You go back to the crater and you again see the pillar in the center and the carved stone stairs to the north.")
        elif not self.area_discovered and not self.crater_filled:
            description = "You walk into the crater in the center of the island. All you see is a stone pillar and on each side is a four rope with four different colors Maybe you should cut one."
            display.announce(description)
        else:
            display.announce("You approach the crater and see it filled to the brim with lava. You decide it's a good idea to not touch it.")
        

    #need to add east
    def process_verb (self, verb, cmd_list, nouns):
        if verb == "east":
            config.the_player.next_loc = self.main_location.locations["mossmeadow"]
        if verb == "south":
            config.the_player.next_loc = self.main_location.locations["stonebeach"]
        if verb == "west":
            config.the_player.next_loc = self.main_location.locations["golemgrove"]
        if verb == "north":
            if self.area_discovered:
                display.announce("You travel North up the mysterious stairs.")
                config.the_player.next_loc = self.main_location.locations["treasurecliff"]
            else:
                display.announce("Theres no way to go North")
        
        if not self.flag:   #flag to indicate if rope cut has happened yet
            if verb == "cut":
                cutRope = False
                while(not cutRope):
                    
                    ropeChoice = display.get_text_input("There is a red, blue, green and purple rope. Which color would you like to cut? ")
                    ropeChoice = ropeChoice.lower() #choose a rope to cut
                    
                    if("leave" in ropeChoice.lower()):  #leave if youd like
                        return
                    
                    if (ropeChoice == "red" or ropeChoice == "blue" or ropeChoice == "green" or ropeChoice == "purple"):
                        if(ropeChoice == self.rope):
                            display.announce("A chime plays below and you see to the north, a set of stairs carves itself into the crater.")
                            self.area_discovered = True
                        else:
                            display.announce("The statue shifts open and lava starts to pool and fill the crevice. Your crew quickly gets out of the crevice as it fills to the brim.")
                            self.crater_filled = True
                    #if rope is correct, secret area is discovered, else center is coated in lava and can't be accessed again
                        
                        cutRope = True
                        self.flag = True
                verb = 'none'

    def GetRopeColor(): #rope list
        listOfRopes = ["red", "blue", "green", "purple"]
        return random.choice(listOfRopes)
    


class TreasureCliff(location.SubLocation): #secret area from puzzle
    def __init__(self, m):
        super().__init__(m)
        self.name = "treasurecliff"
        self.verbs['south'] = self
        self.verbs['open'] = self
        self.chestOpen = False

    def enter(self):
        if not self.chestOpen:
            description = "You climb the stone stairs. At the top you see a cliffside with beautiful blue waters thousands of feet below.\nThe floor is lined with intricate and precise patterns carved into the stone floor.\n The carvings point towards this beautifully made stone chest. Do you open it?"
            display.announce(description)
        else:
            description = "You return to this beautiful location with its nice cool breeze and beautiful stonework on the massive cliff side.\n You see the chest you previous opened glowing in the sunlight."
            display.announce(description)

    def process_verb(self, verb, cmd_list, nouns):
        if verb == "south":
                config.the_player.next_loc = self.main_location.locations["holepuzzle"]
        if not self.chestOpen:
            if verb == "open":
                display.announce("You carefully open the chest, as it lid comes up, you see an odd weapon.\nYou pick it up.")
                if random.randrange(2) == 0: #two items to choose from in chest
                    display.announce("You received the curved barrel shotgun. It looks confusing but ...useful.")
                    config.the_player.add_to_inventory([CurvedBarrelShotgun()])

                else:
                    display.announce("You received the 90 degree pistol. This weapon makes zero sense but you keep it anyway.")
                    config.the_player.add_to_inventory([BentBarrelPistol()])
                self.chestOpen = True

        
class CurvedBarrelShotgun(Item):
    #does decent damage, however who you shoot and how many you hit is random

    def __init__(self):
        super().__init__("curved-shotgun", 10)
        self.damage = (8,50)
        self.skill = "guns"
        self.verb = "shoot"
        self.verb2 = "shoots"

    def pickTargets(self, action, attacker, allies, enemies):
        number_of_attacks = random.randrange(1,4)
    
        if(len(enemies) <= number_of_attacks):
            return enemies
        else:
            options = []
            for t in enemies:
                options.append("attack " + t.name)
            targets = []

        while(len(targets) <= number_of_attacks):
            display.announce(f"Pick target number {len(targets) + 1}.", pause=False)
            choice = menu(options)
            choice = random.randrange(1, len(targets)+1)
            if(not choice in targets):
                targets.append(enemies[choice])
        return targets
        
class BentBarrelPistol(Item):
    #you shoot yourself in the foot and take damage

    def __init__(self):
        super().__init__("bentbarrel-pistol", 5)
        self.damage = (10,20)
        self.skill = "guns"
        self.verb = "shoot"
        self.verb2 = "shoots"
        self.NUMBER_OF_ATTACKS = 1

    def pickTargets(self, actions, attacker, allies, enemies):
        display.announce(f"{attacker.get_name()} has shot towards their foot!")
        return [attacker]
        

class MossMeadow(location.SubLocation): # east side of island
    def __init__ (self, m):
        super().__init__(m)
        self.name = "mossmeadow"
        self.verbs['south'] = self
        self.verbs['west'] = self
        self.verbs['eat'] = self
        self.moss_color = self.main_location.locations["holepuzzle"].rope
        self.flag = False

    def enter(self):
        display.announce(f"You enter this side of the island that is coated in a {self.moss_color} colored moss.")
        if (not self.flag):
            display.announce("You have been told in the past that it may be a good idea to eat some for a boost.")
            display.announce("Would you like to eat some?")
        else:
            display.announce("You can still see where you had a nice snack.")

    def process_verb (self, verb, cmd_list, nouns):
        game = config.the_player

        if (verb == "west"):
            config.the_player.next_loc = self.main_location.locations["holepuzzle"]
        if (verb == "south"):
            config.the_player.next_loc = self.main_location.locations["stonebeach"]

        if not self.flag:   #gives you choice to eat moss
            if (verb == "eat"):
                consumedMoss = False
                while(not consumedMoss):
                    eatMoss = display.get_text_input("Are you sure? Yes or no? ")
                    eatMoss = eatMoss.lower()

                    if ("no" in eatMoss):
                        return
                    
                    if (eatMoss == "yes"):
                        display.announce(f"You eat the {self.moss_color} colored moss.")
                        if (self.moss_color == "green"):    #green moss hurts you
                            game.add_to_inventory([GreenMoss()])
                            randomPirate = random.choice(game.get_pirates())
                            randomPirate.inflict_damage(10, " disturbing nature.")
                            display.announce(f"{randomPirate.get_name()} feels a burning pain in their stomach.")
                        elif (self.moss_color == "blue"):   #blue moss kills you
                            randomPirate = random.choice(game.get_pirates())
                            randomPirate.inflict_damage(100, " disturbing nature.")
                            display.announce(f"{randomPirate.get_name()} takes a forever nap.")
                        elif (self.moss_color == "purple"): #purple moss makes you sick
                            game.add_to_inventory([PurpleMoss()])
                            randomPirate = random.choice(game.get_pirates())
                            randomPirate.sick = True
                            display.announce(f"{randomPirate.get_name()} feels weakended.")
                        elif (self.moss_color == "red"):    #red moss makes you lucky
                            game.add_to_inventory([RedMoss()])
                            randomPirate = random.choice(game.get_pirates())
                            randomPirate.lucky = True
                            display.announce(f"{randomPirate.get_name()} is ready to buy a lotto ticket.")
                        consumedMoss = True
                        self.flag = True
                verb = 'none'

class GreenMoss(Item):  # 5 free score with the price of pain
    def __init__(self):
        super().__init__("green-moss", 5)

class PurpleMoss(Item): # 5 free score with stomach ache
    def __init__(self):
        super().__init__("purple-moss", 5)

class RedMoss(Item):    # 50 free score with the lucky moss
    def __init__(self):
        super().__init__("red-moss", 50)

                




    

                
