import threading
import numpy as np
from math import inf
from tkinter import Tk, Canvas, PhotoImage, mainloop

class Ball():
    def __init__(self, r, color, pos, shine, mirror):
        self.r = r
        self.color = color
        self.pos = pos
        self.shine = shine
        self.mirror = mirror
        self.r2 = r*r

class Light():
    def __init__(self, tip, intensive, pos= (0, 0, 0), direction= (0, 0, 0)):
        self.tip = tip
        self.intensive = intensive
        self.pos = pos
        self.direction = direction
    
class Render():
    def __init__(self, balls, light):
        self.balls = balls
        self.light = light
    
    def reflect_ray(self, R, N):
        return 2 * N * np.dot(N, R) - R
        
    def add_light(self, P, N, V, s):
        length = lambda a: (np.sqrt(np.dot(a, a)))
        i = .0
        for light in self.light:
            if light.tip == 'ambient':
                i += light.intensive
            else:
                if light.tip == 'point':
                    L = light.pos - P
                    t_max = 1
                elif light.tip == 'directional':
                    L = light.direction
                    t_max = inf
                    
                shadow_ball, shadow_t = self.closest_intersection(P, L, 0.001, t_max)
                if shadow_ball is not None:
                    continue
                
                n_dot_l = np.dot(N, L)
                if n_dot_l > 0:
                    i += light.intensive * n_dot_l / (length(N) * length(L))
                    
                if s != 0:
                    R = self.reflect_ray(L, N)
                    r_dot_v = np.dot(R, V)
                    if r_dot_v > 0:
                        i += light.intensive * pow((r_dot_v / (length(R) * length(V))), s)
                    
        return i
    
    def intersect_ball(self, O, D, ball, k1):
        C = ball.pos
        OC = O - C
        k2 = 2 * np.dot(OC, D)
        k3 = np.dot(OC, OC) - ball.r2
        
        discr = k2*k2 - 4*k1*k3
        if discr < 0:
            return inf, inf
        
        t1 = (-k2 + np.sqrt(discr)) / (2*k1)
        t2 = (-k2 - np.sqrt(discr)) / (2*k1)
        
        return t1, t2
    
    def closest_intersection(self, O, D, t_min, t_max):
        closest_t = inf
        closest_obj = None
        k1 = np.dot(D, D)
        for ball in self.balls:
            t1, t2 = self.intersect_ball(O, D, ball, k1)
            if t_min <= t1 <= t_max and t1 < closest_t:
                closest_t = t1
                closest_obj = ball
            if t_min <= t2 <= t_max and t2 < closest_t:
                closest_t = t2
                closest_obj = ball
        
        # for cube in self.cubes:
        #     t1, t2 = self.intersect_cube(O, D, cube, k1)
        #     if t_min <= t1 <= t_max and t1 > closest_t:
        #         closest_t = t1
        #         closest_obj = cube
        #     if t_min <= t2 <= t_max and t2 > closest_t:
        #         closest_t = t2
        #         closest_obj = cube

        return closest_obj, closest_t
    
    def render_pixel(self, O, D, t_min, t_max, depth):
        length = lambda a: (np.sqrt(np.dot(a, a)))
        
        closest_obj, closest_t = self.closest_intersection(O, D, t_min, t_max)
            
        if closest_obj is None:
            return [0, 0, 0]
            
        P = O + closest_t * D
        N = P - closest_obj.pos
        N = N / length(N)
        local_color = [0, 0, 0]
        a = self.add_light(P, N, -D, closest_obj.shine)
        for i in (0, 1, 2):
            local_color[i] = int(closest_obj.color[i] * a)
            if local_color[i] > 255:
                local_color[i] = 255
        
        r = closest_obj.mirror
        if depth <= 0 or r <= 0:
            return local_color
        
        R = self.reflect_ray(-D, N)
        reflect_color = self.render_pixel(P, R, 0.01, inf, depth - 1)
        color = [0, 0, 0]
        for i in (0, 1, 2):
            color[i] = int(local_color[i] * (1 - r) + reflect_color[i] * r)
        return color
        

class MainApp():
    def __init__(self):
        self.width, self.height = 400, 300
        window = Tk()
        self.canvas = Canvas(window, width= self.width, height= self.height, bg= '#000000')
        self.canvas.pack()
        self.img = PhotoImage(width= self.width, height= self.height)
        self.canvas.create_image((self.width/2, self.height/2), image= self.img, state= "normal")
        
        self.O = np.array([.0, .0, .0])
        
        self.balls = [Ball(r= 1, color= (255, 0, 0), pos= np.array([-2, .3, 5]), shine= 10, mirror= 0),\
            Ball(r= 1, color= (0, 255, 0), pos= np.array([0, 1, 4]), shine= 500, mirror= .4),\
            Ball(r= 1, color= (0, 255, 255), pos= np.array([2, -1, 5]), shine= 500, mirror= 0.5),\
            # Ball(r= 500, color= (100, 100, 100), pos= np.array([0, 501.5, 50]), shine= 500, mirror= .3),\
            Ball(r= 6, color= (255, 255, 255), pos= np.array([0.5, -1, 13]), shine= 500, mirror= 0.5)]
            # Ball(r= .6, color= (255, 255, 255), pos= np.array([1.7, 1.8, 3]), shine= 500, mirror= .4),\
            # Ball(r= .4, color= (255, 255, 255), pos= np.array([1.7, 1.1, 3]), shine= 500, mirror= .4),\
            # Ball(r= .3, color= (255, 255, 255), pos= np.array([1.7, .6, 3]), shine= 500, mirror= .4),\
            # Ball(r= .1, color= (255, 153, 0), pos= np.array([1.59, .6, 2.7]), shine= 500, mirror= .4)]

        # self.cubes = [Cube(r= 1, color= (0, 255, 0), pos= np.array([0, 1, 3]), shine= 500, mirror= .4)]

        self.light = [Light(tip= 'point', intensive= 0.4, pos= (2, -4, 2)),\
                    Light(tip= 'ambient', intensive= 0.2),\
                    Light(tip= 'directional', intensive= 0.4, direction= (-1, -1, -1))]
        
        self.rend = Render(self.balls, self.light)
        t1 = threading.Thread(target=self.render_image_1, args=())
        t2 = threading.Thread(target=self.render_image_2, args=())
        t1.start()
        t2.start()
        mainloop()
        t1.join()
        t2.join()
        print("thread kill")

    def canvas_to_wport(self, x, y):
        return np.array([x / self.width, y / self.height, .6])
    
    def rgb_to_hex(self, rgb):
        return ('%02x%02x%02x' % rgb)
    
    def render_image_1(self):
        for y in range(int(-self.height/2), int(self.height/2)):
            for x in range(int(-self.width/2), 0):
                D = self.canvas_to_wport(x, y)
                col = self.rend.render_pixel(self.O, D, 1, inf, 1)
                color = tuple(col)
                color = '#' + self.rgb_to_hex(color)
                self.img.put(color, (int(x + self.width/2), int(y  + self.height/2)))
                
    def render_image_2(self):
        for y in range(int(self.height/2), int(-self.height/2), -1):
            for x in range(0, int(self.width/2)):
                D = self.canvas_to_wport(x, y)
                col = self.rend.render_pixel(self.O, D, 1, inf, 1)
                color = tuple(col)
                color = '#' + self.rgb_to_hex(color)
                self.img.put(color, (int(x + self.width/2), int(y  + self.height/2)))

if __name__ == '__main__':
    MainApp()
