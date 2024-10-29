# !/usr/bin/env python3
import math

class Odometry:
    def __init__(self, wheelbase:float, startX:float, startY:float, startDirection:float, listr:list, listl:list):
        self.wheelbase= wheelbase
        self.kx=0
        self.ky=0
        self.anew=startDirection
        self.distance_per_tick=3.7/70
        self.listr=listr
        self.listl=listl
        self.listdr=[]
        self.listdl=[]
        self.delta_a=0
        self.startX=startX
        self.startY=startY
        
    def maths(self, r, l):
        # If path straight
        if (r==l):
            s=r
            ab=0
        else:
            ab=(r-l)/self.wheelbase
            ds=(r+l)/2
            rs=ds/ab
            s=abs(2*rs*math.sin(ab/2))
            
        # Convert to degree
        ag=(180/math.pi)*ab
        
        # Convert into direction
        dx=abs((s*math.sin(ab-self.delta_a))/50)
        dy=abs((s*math.cos(ab-self.delta_a))/50)
        self.delta_a=(self.delta_a-ab) 
        # New angle of sight
        anew=(float(self.anew)-float(ag))%360

        if (0<=anew<90):
            x=dx
            y=dy
        elif (90<=anew<180):
            x=dx
            y=(-1)*dy
        elif (180<=anew<270):
            x=(-1)*dx
            y=(-1)*dy
        else:
            x=(-1)*dx
            y=dy  
        return x, y, ag     

    def calc_new_position(self):
        for i in range(len(self.listdr)):
            newX, newY, newD= self.maths(self.listdr[i], self.listdl[i])
            self.kx=self.kx+newX
            self.ky=self.ky+newY
            self.anew=(float(self.anew)-float(newD))%360   
        
        return self.kx, self.ky, self.anew
    
    def delta_rotation(self):   
        for i in range(len(self.listr)-1):
            self.listdr.append((self.listr[i+1]-self.listr[i])*self.distance_per_tick)
            self.listdl.append((self.listl[i+1]-self.listl[i])*self.distance_per_tick)

    def convert_new_postion(self):
        if (self.anew==90 or self.anew==270):
            self.anew=self.anew-90 
            changed_x, changed_y, changed_d=self.calc_new_position()
            new_d=(changed_d+90)%360
            new_x=self.startX+changed_y
            new_y=self.startY+changed_x*(-1)
            return new_x, new_y, new_d
        else: 
            changed_x, changed_y, changed_d=self.calc_new_position()
            return changed_x, changed_y, changed_d

    def round_cordinates(self, x, y , d):
        rounded_x=round(x)
        rounded_y=round(y)
        if (d>335 or d<25):
            rounded_d=0
        elif (65<d<115):
            rounded_d=90
        elif (155<d<205):
            rounded_d=180
        else:
            rounded_d=270
        return rounded_x, rounded_y, rounded_d 
        
