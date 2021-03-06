# Name: Fireworks
# Author: G.G.Otto
# Date: 3/4/2021
# Version: 2.2

import pygame, math, random
import gamesetup as gs
from pygame.locals import *

class Rocket(gs.Sprite):
    '''represents a rocket'''

    def __init__(self, game, color, pos):
        '''Rocket(game, color, pos) -> Rocket
        constructs a rocket with color
        lanuches from pos'''
        gs.Sprite.__init__(self, game, pygame.image.load(f"rocket_{color}.png"))
        self.game = game
        self.color = color
        self.pos(pos)
        self.tilt(-90)
        self.heading(90)
        self.launched = False
        self.exploded = False
        self.restoring = False
        self.clock = gs.Clock(0.5)
        self.length = random.randrange(300,400)
        self.originPos = pos

        # color dictionary
        colors = {"red":(255,0,0), "green":(0,255,0), "blue":(0,0,255), "yellow":(255,201,14), "pink":(255,0,255)}
        self.color = colors[color]

        # particles for explosion
        self.particles = []
        for i in range(50):
            particle = Particle(game, colors[color], (self.pos()[0], 520-self.length))
            self.particles.append(particle)
            self.game.add_particle(particle)

    def launch(self):
        '''Rocket.launch() -> None
        launches the rocket'''
        if not self.launched:
            self.launched = True
            self.clock.start()

            # move rocket to end of list
            rockets = self.game.get_rockets()
            rockets.remove(self)
            rockets.append(self)

            # move particles to end of list
            particles = self.game.get_particles()
            for particle in self.particles:
                particles.remove(particle)
                particles.append(particle)

    def update(self):
        '''Rocket.update() -> None
        updates the rocket'''
        if self.launched and not self.restoring:
            self.pos((self.pos()[0], 520-self.length*self.clock.get_time()/self.clock.get_max()))

            # explode rocket
            if self.clock.get_time() == self.clock.get_max() and not self.exploded:
                self.exploded = True
                for particle in self.particles:
                    particle.set_pos(self.pos())
                    particle.go()
                
                # reset rocket
                self.game.after(2000, self.restore)

        # restore
        if self.restoring:
            self.pos((self.pos()[0], self.originPos[1]+200-200*self.clock.get_time()/self.clock.get_max()))
            if self.clock.get_max() == self.clock.get_time():
                self.restoring = False
                self.launched = False
                self.clock.set_max(0.5)
                self.clock.reset()
                
        if not self.exploded: gs.Sprite.update(self)

    def restore(self):
        '''Particle.restore() -> None
        restores the rocket'''
        self.restoring = True
        self.exploded = False
        self.pos((self.originPos[0], self.originPos[1]+200))
        self.length = random.randrange(300,400)
        self.clock.reset()
        self.clock.set_max(0.5)
        self.clock.start()

        for particle in self.particles:
            particle.reset()

class Particle:
    '''represents a particle in an explosion'''

    def __init__(self, game, color, pos):
        '''Particle(game, color, pos) -> Particle
        constructs a particle for explosion'''
        self.moving = False
        self.max = 1.5
        self.moveClock = gs.Clock(self.max)
        self.pos = pos
        self.positions = []
        self.originPos = pos
        self.power = random.randint(24,26)
        self.speed = 6
        self.color = color
        self.game = game
        self.glitter = [random.randrange(0,100) for i in range(10)]

    def set_pos(self, pos):
        '''Particle.set_pos(pos) -> None
        sets the position of the particle'''
        self.pos = pos
        self.originPos = pos
        
    def go(self):
        '''Particle.go() -> None
        start the particle's movement'''
        self.originHead = math.radians(random.randrange(0,360))
        self.moving = True
        self.moveClock.start()

        # direction: left or right
        self.factor = 1
        if self.originHead > 90:
            self.originHead = 180-self.originHead
            self.factor = -1

    def fade(self, color):
        '''Particle.fade(color) -> rgb
        returns a faded color'''
        sub = 1
        time = max(self.moveClock.get_time()-sub,0)
        return (color[0]-color[0]*time/(self.max-sub),
          color[1]-color[1]*time/(self.max-sub),
          color[2]-(color[2]-70)*time/(self.max-sub))

    def update(self):
        '''Particle.update() -> None
        updates the particle'''
        if not self.moving:
            return

        clock = self.moveClock.get_time()
        color = self.fade(self.color)
        glitter = self.fade((255,255,255))
                 
        # add position to position list
        if len(self.positions) == 0:
            self.positions.append((self.pos, clock))
        else:
            self.positions.insert(0, (self.pos, clock))
            
        self.pos = self.parametric_x(clock*self.speed), self.parametric_y(clock*self.speed)
        pygame.draw.circle(self.game.get_screen(), color, self.pos, 5)

        # trail for firework
        last = self.positions[0][0]
        for pos in self.positions:
            if clock-pos[1] < 0.5 and pos != last:
                lineColor = color
                if self.positions.index(pos) in self.glitter:
                    lineColor = glitter
                pygame.draw.line(self.game.get_screen(), lineColor, last, pos[0], 5)
                last = pos[0]

        # end
        if clock == self.max:
            self.moving = False
                 
    def parametric_x(self, t):
        '''Particle.parametric_x(t) -> float
        returns the x coordinate for time'''
        return self.originPos[0]+self.factor*(self.power*math.cos(self.originHead))*t

    def parametric_y(self, t):
        '''Particle.parametric_y(t) -> float
        returns the y coordinate for time'''
        return self.originPos[1]-((self.power*math.sin(self.originHead))*t-9.81*t**2/2)

    def reset(self):
        '''Particle.reset() -> None
        resets the particle'''
        self.__init__(self.game, self.color, self.originPos)
        
class Fireworks(gs.Game):
    '''represents the window for fireworks'''

    def __init__(self):
        '''Fireworks() -> Fireworks
        constructs the fireworks'''
        gs.Game.__init__(self)

        # set up screen
        pygame.display.set_caption("Fireworks")
        self.screen = pygame.display.set_mode((600,625))

        # rockets and buttons
        self.particles = []
        self.rockets = []
        self.buttons = []
        rockets = [("red", 100), ("green", 200), ("blue", 300), ("pink", 400), ("yellow", 500)]
        for rocket in rockets:
            newRocket = Rocket(self, rocket[0], (rocket[1], 520))
            self.rockets.append(newRocket)
            self.buttons.append(gs.Button(self, pygame.image.load("launch_button.png"), pos=(rocket[1],570),
                hover=pygame.image.load("launch_button_hover.png"), command=newRocket.launch))

        # finale button
        self.buttons.append(gs.Button(self, pygame.image.load("finale_button.png"), pos=(300, 605),
            hover=pygame.image.load("finale_button_hover.png"), command=self.launch_all))
        
        self.bind(KEYDOWN, self.launch_all, "finale")

    def get_rockets(self):
        '''Fireworks.get_rockets() -> None
        returns all rockets'''
        return self.rockets

    def get_particles(self):
        '''Fireworks.get_particles() -> list
        returns all partcles'''
        return self.particles

    def launch_all(self, event=None):
        '''Fireworks.launch_all() -> None
        launches all the fireworks'''
        if event == None or event.key == K_SPACE:
            for rocket in self.rockets[:]:
                rocket.launch()

    def add_particle(self, particle):
        '''Firework.add_particle(particle) -> None
        adds particles to be updated before rockets'''
        self.particles.append(particle)

    def update(self):
        '''Fireworks.update() -> None
        updates the fireworks'''
        self.screen.fill((0,0,70))

        # update particles buttons and rockets
        for particle in self.particles: particle.update()
        for rocket in self.rockets: rocket.update()
        for button in self.buttons: button.update()
            
        pygame.display.update()

pygame.init()
Fireworks().mainloop()
                           
