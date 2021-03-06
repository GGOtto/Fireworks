# Name: Game Setup Module
# Author: G.G.Otto
# Date: 1/25/2021
# Version 1.3.2
#
# Used with the module pygame
# You may use this for any use
#
# This module is to make setting up your game easier.
# It also in a variety of different objects to make
# coding your game easier in general.

import pygame, time, math, random

class Clock:
    '''represents a stopwatch that keeps track of time in seconds
   the clock starts out paused, so don't forget to play it!'''

    def __init__(self, maxTime=None):
        '''Clock() -> Clock
        constructs a clock.
        the clock starts with 0 seconds.
        don't forget to start it!'''
        self.startTime = None
        self.saved = 0
        self.maxTime = maxTime

    def get_max(self):
        '''Clock.get_max() -> float/int
        returns the max time of the clock'''
        return self.maxTime

    def set_max(self, maxTime):
        '''Clock.set_max(maxTime) -> None
        sets the max time of the clock'''
        self.maxTime = maxTime

    def get_time(self):
        '''Clock.get_time() -> float
        returns the current time on the stopwatch'''
        if self.startTime == None: return self.saved
        currentTime = time.time()-self.startTime+self.saved
        if self.maxTime != None and currentTime > self.maxTime:
            return self.maxTime
        return currentTime

    def set_time(self, newTime):
        '''Clock.set_time(newTime) -> None
        sets the current time on the stopwatch
        pauses the clock in the process'''
        self.saved = newTime
        self.startTime = None

    def reset(self):
        '''Clock.reset() -> None
        resets the clock back to 0
        pauses the clock in the process'''
        self.set_time(0)

    def stop(self):
        '''Clock.stop() -> None
        pauses the stopwatch.
        stopwatch may be resumed using Clock.start()'''
        self.saved = self.get_time()
        self.startTime = None

    def start(self):
        '''Clock.start() -> None
        starts the stopwatch.
        stopwatch may be stopped using Clock.stop()'''
        self.startTime = time.time()

class Sprite:
    '''sprite object to inherit from'''

    def __init__(self, game, surface):
        '''Sprite(game, surface) -> Sprite
        constructs an object'''
        self.keepImg = surface
        self.origin = surface
        self.image  = surface
        self.position = (0,0)
        self.head = 0
        self.game = game

    def heading(self, heading=None):
        '''Sprite.get_heading(heading) -> int
        returns the heading of the object if heading not given
        otherwise sets heading'''
        if heading == None:
            return math.degrees(self.head)
        self.image = pygame.transform.rotozoom(self.origin, heading, 1)
        self.head = math.radians(heading)

    def tilt(self, heading):
        '''Sprite.tilt(heading) -> None
        tilts the image so that heading for image is 0 for sprite'''
        self.origin = pygame.transform.rotozoom(self.keepImg, heading, 1)

    def towards(self, pos):
        '''Sprite.towards(pos) -> float
        returns the heading towards pos'''
        x, y = pos[0]-self.pos()[0], self.pos()[1]-pos[1]

        # cases
        if x == 0:
            if y >= 0: return 90
            else: return 270
                
        elif y == 0:
            if x >= 0: return 0
            else: return 180

        heading = math.degrees(math.atan(y/x))
        if (x < 0 and y > 0) or (x < 0 and y < 0):
            heading += 180
        return heading

    def pos(self, pos=None):
        '''Sprite.pos(pos) -> int
        returns the position of the object if heading not given
        otherwise sets pos'''
        if pos == None:
            return self.position
        self.position = pos

    def forward(self, distance):
        '''Sprite.forward(distance) -> None
        moves the object forward by distance'''
        self.position = self.position[0]+distance*math.cos(self.head), self.position[1]-distance*math.sin(self.head)

    def update(self):
        '''Sprite.update() -> None
        keeps updating the sprite'''
        self.game.blit(self.image, self.position, True, True)
        
class Widget(dict):
    '''represents a widget for in-module objects'''

    def __init__(self, game, rect, defaults={}, **attributes):
        '''Widget(game, rect, defaults, **attributes) -> Widget
        constructs the widget
        rect is pygame.Rect, defaults is dict'''
        dict.__init__(self, defaults)
        for arg in attributes:
            if arg not in defaults:
                raise GameSetupError(arg+" not in widget attributes. Must be in\n"+str(defaults))
            self[arg] = attributes[arg]

        self.id = len(game.get_widgets())
        self.rect = rect
        game.add_widget(self, self.id)
        self.game = game
        self.events = {}

    def __eq__(self, other):
        '''Widget == other -> bool
        returns if self is other'''
        return isinstance(other, Widget) and other.id == self.id

    def __str__(self):
        '''str(Widget) -> str
        converts widget to str'''
        return f"<Widget -ID: {self.id} -Rect: {self.rect} -Events: {self.events}>"

    def get_clear_ID(self):
        '''Widget.ID() -> str
        returns a clear event ID'''
        i = 0
        while True:
            ID = f"generated_event_id_{i}"
            if ID not in self.events:
                return ID
            i += 1
            
    def is_over(self, pos):
        '''Widget.is_over(pos) -> bool
        returns if pos is over widget'''
        return self.rect[0] < pos[0] < self.rect[0]+self.rect[2] and \
            self.rect[1] < pos[1] < self.rect[1]+self.rect[3]

    def is_event(self, eventId):
        '''Widget.is_event(eventId) -> bool
        returns whether eventId is attached to an event'''
        return eventId in self.events

    def get_rect(self):
        '''Widget.get_rect() -> tuple
        returns the rectangle of the widget'''
        return self.rect

    def set_rect(self, newRect):
        '''Widget.set_rect(newRect) -> None
        setter for rect attribute'''
        self.rect = newRect

    def get_id(self):
        '''Widget.get_id() -> float
        returns the widgets ID'''
        return self.id

    def configure(self, key, value):
        '''Widget.configure(key, value) -> None
        changes attribute key to value'''
        if key in self:
            self[key] = value

    def move(self, pos, center=True):
        '''Widget.move(pos, center=True) -> None
        moves the widget to pos (centered if center is True)'''
        if center: pos = pos[0]-self.rect[2]/2, pos[1]-self.rect[3]/2
        self.rect = pos[0], pos[1], self.rect[2], self.rect[3]

    def set_focus_var(self, boolean):
        '''Widget.set_focus_var(boolean) -> None
        simple setter for self.focus attribute'''
        self.focus = boolean

    def focus(self, focus=None):
        '''Widget.focus(focus) -> None/bool
        if focus specified, sets focus. otherwise returns focus'''
        if focus == None:
            return self.game.focus() == self
        if focus == False:
            self.game.focus(False)
        else:
            self.game.focus(self)

    def event(self, event):
        '''Widget.event(event) -> None
        filler for method to checks an event'''
        pass

    def process_event(self, event):
        '''Widget.process_event(event) -> None
        processes an event for bindings'''
        perform = []
        for eventID in self.events:
            eventInfo = self.events[eventID]
            
            # on click and on release
            if ((eventInfo[0] == "onclick" and event.type == pygame.MOUSEBUTTONDOWN and event.button == eventInfo[2]) or \
               (eventInfo[0] == "onrelease" and event.type == pygame.MOUSEBUTTONUP and event.button == eventInfo[2])) and \
               self.is_over(event.pos):
                perform.append(eventInfo[1])

            # on key and on key release
            elif (eventInfo[0] == "onkey" and event.type == pygame.KEYDOWN and event.key == eventInfo[2]) or \
                (eventInfo[0] == "onkeyrelease" and event.type == pygame.KEYUP and event.key == eventInfo[2]):
                perform.append(eventInfo[1])

            # on key press
            elif eventInfo[0] == "onkeypress" and pygame.key.get_pressed()[eventInfo[2]] == 1:
                perform.append(eventInfo[1])

        for method in perform:
            try:
                method(event)
            except TypeError:
                method()

        self.event(event)

    def onclick(self, eventId, command=None, num=1):
        '''Widget.onclick(eventId, command=None, num=None) -> None
        sets up an event using eventId. If command=None, removes exisiting event
        eventId is any str or int, num is the mouse button number (1,2, or 3)
        auto generates ID if eventId is None
        ---
        onclick will call command when the mouse button is clicked'''
        if command == None:
            self.remove_event(eventId)
        if eventId== None:
            eventId = self.get_clear_ID()
        self.events[eventId] = ("onclick", command, num)

    def onrelease(self, eventId, command=None, num=1):
        '''Widget.onrelease(eventId, command=None, num=1) -> ID
        sets up an event using eventId. If command=None, removes exsiting event
        eventId is any str or int, num is the mouse button number (1,2, or 3)
        auto generates ID if eventId is None
        ---
        onrelease will call command when the mouse button is released'''
        if command == None:
            self.remove_event(eventId)
        if eventId == None:
            eventId = self.get_clear_ID()
        self.events[eventId] = ("onrelease", command, num)
        return eventId

    def onkey(self, eventId, command=None, key=None):
        '''Widget.onkey(eventId, command=None, key=None) -> None
        sets up an event with eventId. If command=None, removes exsisting event
        key is the key number, eventId is any str or int
        auto generates ID if eventId is None
        ---
        onkey will call command everytime key is pressed down'''
        if command == None:
            self.remove_event(eventId)
        if eventId == None:
            eventId = self.get_clear_ID()
        self.events[eventId] = ("onkey", command, key)
        return eventId

    def onkeyrelease(self, eventId, command=None, key=None):
        '''Widget.onkeyrelease(eventId, command=None, key=None) -> None
        sets up an event with eventId. If command=None, removes exsisting event
        key is the key number, eventId is any str or int
        auto generates ID if eventId is None
        ---
        onkeyrelease will call command everytime key is released'''
        if command == None:
            self.remove_event(eventId)
        if eventId == None:
            eventId = self.get_clear_ID()
        self.events[eventId] = ("onkeyrelease", command, key)
        return eventId

    def onkeypress(self, eventId, command=None, key=None):
        '''Widget.onkeypress(eventId, command=None, key=None) -> None
        sets up an event with eventId. If command=None, removes exsisting event
        key is the key number, eventId is any str or int
        auto generates ID if eventId is None
        ---
        onkeypress will call command every 50 milliseconds if key is pressed'''
        if command == None:
            self.remove_event(eventId)
        if eventId == None:
            eventId = self.get_clear_ID()
        self.events[eventId] = ("onkeypress", command, key)
        return eventId

    def remove_event(self, eventId):
        '''Widget.remove_event(eventId) -> None
        deactivates the event connected to eventId'''
        if eventId in self.events:
            self.events.pop(eventId)

class Button(Widget):
    '''represents a button to click
   inherits from Widget'''

    def __init__(self, game, img, **attributes):
        '''Button(game, img, **attribtues) -> Button
        constructs a button using for game using attributes

        if img not a surface, img should be (width, height)

        attributes to use:
         pos: sets the position of the button
         command: the function/method called on click
         hover: surface of button on hover
         click: surface of button on click
         disable: surface of button when disabled
         disabled: boolean if disabled'''
        defaults = {
          "pos":(0,0), "command":None, "hover":None,
          "click":None, "disable":None, "disabled":False }

        if isinstance(img, pygame.Surface):
            rect = img.get_rect()
        else:
            rect = (0,0,img[0],img[1])
            
        Widget.__init__(self, game, rect, defaults, **attributes)
        self.move(self["pos"])
        self.img = img
        
        # bindings
        self.clicked = False
        self.onclick(None, self.perform)
        self.onrelease(None, self.perform)

    def set_disabled(self, boolean):
        '''Button.set_disabled(boolean) -> None
        sets whether the button is disabled'''
        self["disabled"] = boolean

    def set_img(self, newImg):
        '''Button.get_img(newImg) -> None
        setter for main button image'''
        self.img = newImg
        
    def perform(self, event):
        '''Button.perform(event) -> None
        performs the command'''
        if event.type == pygame.MOUSEBUTTONUP:
            if self["command"] != None and not self["disabled"] and self.clicked:
                self["command"]()
            self.clicked = False
        elif not self.clicked:
            self.clicked = True
        
    def update(self):
        '''Button.update() -> None
        updates the button'''
        img = None
        
        # disabled img
        if self["disabled"]:
            if self["disable"] != None:
                img = self["disable"]
                
        # click img
        elif self.clicked and self["click"] != None:
            if not self.is_over(pygame.mouse.get_pos()):
                self.clicked = False
            else:
                img = self["click"]
                
        # hover img
        elif self.is_over(pygame.mouse.get_pos()) and self["hover"] != None:
            img = self["hover"]

        if img == None:
            img = self.img

        if isinstance(img, pygame.Surface):
            self.set_rect(img.get_rect())
            self.move(self["pos"])
            self.game.blit(img, self["pos"], True, True)
        else:
            self.set_rect((self["pos"][0], self["pos"][1], self.img[0], self.img[1]))

class Popup(Widget):
    '''represents a popup widget'''

    def __init__(self, game, img):
        '''Popup(game, img) -> Popup
        sets up a popup for game

        call Popup.add_button(rect, command) to set up buttons
        call Popup.update() to update the popup on the screen'''
        Widget.__init__(self, game, img.get_rect())
        self.game = game
        self.img = img
        self.buttons = []
        self.isopen = False
        self.width, self.height = pygame.display.get_window_size()

    def is_open(self):
        '''Popup.is_open() -> bool
        returns if the popup is open or not'''
        return self.isopen

    def get_buttons(self):
        '''Popup.get_buttons() -> list
        returns a list of all buttons'''
        return self.buttons
        
    def add_button(self, rect, command):
        '''Popup.add_button(rect, command) -> Button
        creates and returns the button at rect
        treat the top-left corner of the popup as (0,0)'''
        button = Button(self.game, (rect[2], rect[3]), pos=(rect[0]+self.width/2-self.img.get_rect()[2]/2,
            rect[1]+self.height/2-self.img.get_rect()[3]/2), command=lambda: self.command(command))
        self.buttons.append(button)
        return button

    def command(self, command):
        '''Popup.command(command) -> Button
        performs command if popup is open'''
        if self.isopen: command()

    def open(self):
        '''Popup.open() -> None
        opens the popup'''
        self.isopen = True

    def close(self):
        '''Popup.close() -> None
        closes the popup'''
        self.isopen = False

    def toggle(self):
        '''Popup.toggle() -> None
        if popup is open, closes popup, else opens popup'''
        self.isopen = not self.isopen

    def update(self):
        '''Popup.update() -> None
        updates the popup on the screen'''
        if not self.isopen: return
        self.game.blit(self.img, (self.width/2, self.height/2), True, True)

        for button in self.buttons:
            button.update()
        
class Slider:
    '''a type of "sprite" that moves steadily with a internal clock'''

    def __init__(self, pos, heading):
        '''Slider(game, heading, speed) -> Slider
        constructs the Slider object'''
        self.head = heading
        self.moving = False
        self.position = pos
        self.clock = Clock()

    def get_clock(self):
        '''Slider.get_clock() -> Clock
        returns the clock'''
        return self.clock

    def get_pos(self):
        '''Slider.get_pos() -> (x,y)
        returns the position of the object'''
        if not self.moving: return self.position
        return self.position[0]+(self.distance*self.clock.get_time()/self.speed)*math.cos(math.radians(self.head)), \
            self.position[1]+(self.distance*self.clock.get_time()/self.speed)*math.sin(math.radians(self.head))

    def set_pos(self, pos):
        '''Slider.set_pos(pos) -> None
        sets the position of the object'''
        self.position = pos

    def get_heading(self):
        '''Slider.get_heading() -> int/float
        returns the heading of the object'''
        return self.head

    def set_heading(self, heading):
        '''Slider.set_heading(heading) -> None
        sets the heading of the object'''
        self.head = heading

    def forward(self, distance, seconds):
        '''Slider.forward(distance, seconds)
        sets up object to go forward distance in seconds'''
        self.position = self.get_pos()
        self.moving = True
        self.distance = distance
        self.speed = seconds
        self.clock.reset()
        self.clock.set_max(seconds)
        self.clock.start()

    def stop(self):
        '''Slider.stop() -> None
        stops the object from moving'''
        self.position = self.get_pos()
        self.moving = False
        self.clock.reset()

class AfterEvent:
    '''private class for after events'''

    def __init__(self, eventList, ms, command):
        '''AfterEvent(eventList, ms, command) -> AfterEvent
        constructs the event object for after'''
        self.ms = ms
        self.command = command
        self.clock = Clock()
        self.clock.start()
        self.eventList = eventList
        self.eventList.append(self)
        self.completed = False

    def check(self):
        '''AfterEvent.check() -> None
        checks if the event is ready'''
        if self.clock.get_time() > self.ms/1000 and not self.completed:
            self.command()
            self.eventList.remove(self)
            self.completed = True

class Sound(pygame.mixer.Sound):
    '''represents a sound object to be played, muted, unmuted'''

    def __init__(self, game, file):
        '''Sound(game, file) -> Sound
        constructs the sound'''
        pygame.mixer.Sound.__init__(self, file)
        self.game = game
        self.unmute()
        if game.is_muted(): self.mute()

    def set_volume(self, newVolume):
        '''Sound.set_volume(newVolume) -> None
        sets the background volume'''
        self.originVolume = newVolume
        if not self.game.is_muted(): self.unmute()

    def mute(self):
        '''Sound.mute() -> None
        mutes the sound'''
        pygame.mixer.Sound.set_volume(self, 0)

    def unmute(self):
        '''Sound.unmute() -> None
        unmutes the sound'''
        pygame.mixer.Sound.set_volume(self, self.originVolume)
        
class Game:
    '''represents the game object
    intended to be inherited from. includes methods like after
    you must include an update method and your display
    you must call Game.mainloop() to start your game
    your Game.update() method will be called every iteration of mainloop'''

    def __init__(self):
        '''Game() -> Game
        constructs the game'''
        self.restarting = False
        self.isGameRunning = True
        self.afterEvents = []
        self.soundsList = []
        self.isGameMuted = False
        self.screen = None
        self.widgets = {}
        self.gameFocusedWidget = None
        self.bindings = {}

    def focus(self, focus=None):
        '''Game.focus(focus=None) -> type
        if focus is specified, sets widget supplied to focus
        Otherwise returns the current widget in focus
        if focus is False, removes all focus'''
        if focus == None:
            return self.gameFocusedWidget
        elif not focus:
            self.gameFocusedWidget = None
        elif not isinstance(focus, Widget):
            raise GameSetupError("Cannot set focus to a non-widget.")

        self.gameFocusedWidget = focus

    def get_screen(self):
        '''Game.get_screen() -> type
        returns the game screen'''
        return self.screen

    def is_muted(self):
        '''Game.is_muted() -> bool
        returns whether the game is muted or not'''
        return self.isGameMuted

    def get_widgets(self):
        '''Game.get_widgets() -> dict
        returns all widgets'''
        return self.widgets

    def get_widget(self, widgetID):
        '''Game.get_widget(widgetID) -> Widget
        returns the widget connected to ID'
        returns None if not found'''
        if widgetID in self.widgets:
            return self.widgets[widgetID]

    def add_widget(self, widget, widgetID):
        '''Game.add_widget() -> None
        adds widget to game'''
        self.widgets[widgetID] = widget

    def after(self, ms, command):
        '''Game.after(ms, command) -> time
        performs command after ms milliseconds'''
        self.afterEvents.append(AfterEvent(self.afterEvents, ms, command))

    def sound(self, file, volume=1):
        '''Game.sound(file, volume=1) -> Sound
        sets up and then returns a sound object'''
        newSound = Sound(self, file)
        newSound.set_volume(volume)
        self.soundsList.append(newSound)
        return newSound

    def mute(self):
        '''Game.mute() -> None
        mutes all sounds'''
        for sound in self.soundsList:
            sound.mute()
        self.isGameMuted = True

    def unmute(self):
        '''Game.unmute() -> None
        unmutes all sounds'''
        for sound in self.soundsList:
            sound.unmute()
        self.isGameMuted = False

    def restart(self):
        '''Game.restart() -> None
        completely restarts the game
        restarts pygame as well'''
        self.isGameRunning = False
        self.restarting = True

    def close(self):
        '''Game.close() -> None
        closes the game window'''
        self.isGameRunning = False

    def update(self):
        '''Game.update() -> None
        place holder. This method is meant to be overridden
        don't forget to update your display!'''
        pass

    def event(self, event):
        '''Game.event(event) -> None
        checks up an event. This method is meant to be overridden'''
        pass

    def blit(self, surface, pos, centerx=False, centery=False):
        '''Game.center(surface, pos) -> None
        centers surface on pos'''
        if centerx:
            pos = pos[0]-surface.get_rect().width/2, pos[1]
        if centery:
            pos = pos[0], pos[1]-surface.get_rect().height/2
            
        self.screen.blit(surface, pos)

    def bind(self, eventType, command, ID=None):
        '''Game.bind(ID, eventType, command) -> None
        binds eventType to command and returns ID
        if ID not given, ID will be automatically a non-used ID'''
        if ID == None:
            ID = self.get_clear_id()
        self.bindings[ID] = (eventType, command)
        return ID

    def unbind(self, ID=None):
        '''Game.unbind(eventType) -> None
        unbinds event from ID
        if ID not given, unbinds all'''
        if eventType == None:
            self.bindings.clear()
        if eventType in self.bindings:
            self.bindings.pop(ID)

    def get_clear_id(self):
        '''Game.get_clear_id() -> str
        returns an id that is not bound'''
        i = 0
        while True:
            ID = f"generated_event_id_{i}"
            if ID not in self.bindings:
                return ID
            i += 1
            
    def mainloop(self):
        '''Game.mainloop() -> None
        starts the mainloop for the game'''
        while self.isGameRunning:
            # check all after events
            for event in self.afterEvents[:]:
                event.check()

            # other events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()

                # process event in widgets
                for widget in self.widgets:
                    self.widgets[widget].process_event(event)

                # process event for bindings
                for binding in self.bindings:
                    if event.type == self.bindings[binding][0]:
                        try:
                            self.bindings[binding][1](event)
                        except TypeError:
                            self.bindings[binding][1]()
                    
                self.event(event)

            self.update()

        # quit or restart
        pygame.quit()
        if self.restarting:
            pygame.init()
            self.__init__()
