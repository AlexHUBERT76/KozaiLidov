#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Class definition for physical attribute
"""
from os import system
import numpy as np
from lib.plots import DynamicUpdate
from lib.units import *

class Body:

    def __init__(self, mass, position, velocity):
        self.m = np.longdouble(mass)
        self.q = np.longdouble(position)
        self.v = np.longdouble(velocity)
        self.a = np.zeros(3,dtype=np.longdouble)
        self.ap = np.zeros(3,dtype=np.longdouble)
        self.j = np.zeros(3,dtype=np.longdouble)
        self.jp = np.zeros(3,dtype=np.longdouble)
        self.qp = np.zeros(3,dtype=np.longdouble)
        self.vp = np.zeros(3,dtype=np.longdouble)

    def __repr__(self): # Called upon "print(body)"
        return r"Body of mass: {0:.1e} $M_\odot$, position: {1},\
             velocity: {2}".format(self.m/Ms, self.q, self.v)

    def __str__(self): # Called upon "str(body)"
        return r"Body of mass: {0:.1e} $M_\odot$".format(self.m/Ms)

    @property
    def p(self):
        return self.v*self.m

    @property
    def pb(self):
        return self.vb*self.m

class System(Body):

    def __init__(self, bodylist, main = False, blackstyle=True):
        self.blackstyle = blackstyle #for dark mode in plot
        self.bodylist = np.array(bodylist)
        if main == True :
            self.COMShift()
        self.time = 0 #lifetime of system
        self.m = self.M
        self.q = self.COM
        self.v = self.COMV

    def __repr__(self):  # Called upon "print(system)"
        return str([print(body) for body in self.bodylist])

    def __str__(self):  # Called upon "str(system)"
        return str([str(body) for body in self.bodylist])


    def get_masses(self): #return the masses of each object
        return np.array([body.m for body in self.bodylist],
                        dtype=np.longdouble)


    def get_positions(self): #return the positions of the bodies
        xdata = np.array([body.q[0] for body in self.bodylist],
                        dtype=np.longdouble)
        ydata = np.array([body.q[1] for body in self.bodylist],
                        dtype=np.longdouble)
        zdata = np.array([body.q[2] for body in self.bodylist],
                        dtype=np.longdouble)
        return xdata, ydata, zdata

    def get_positionsCOM(self): #return the positions of the bodies
        COM = self.COM          # in the center of mass frame
        xdata = np.array([body.q[0]-COM[0] for body in self.bodylist],
                        dtype=np.longdouble)
        ydata = np.array([body.q[1]-COM[1] for body in self.bodylist],
                        dtype=np.longdouble)
        zdata = np.array([body.q[2]-COM[2] for body in self.bodylist],
                        dtype=np.longdouble)
        return xdata, ydata, zdata

    @property
    def M(self): #return total system mass
        mass = np.longdouble(0.)
        for body in self.bodylist:
            mass = mass + body.m
        return mass

    @property
    def mu(self):
        prod = np.longdouble(1.)
        for body in self.bodylist:
            prod = prod * body.m
        mu = prod/self.M
        return mu

    @property
    def COM(self): #return center of mass in cartesian np_array
        coord = np.zeros(3,dtype=np.longdouble)
        for body in self.bodylist:
            coord = coord + body.m*body.q
        coord = coord/self.M
        return coord

    @property
    def COMV(self): #return center of mass velocity in cartesian np_array
        coord = np.zeros(3,dtype=np.longdouble)
        for body in self.bodylist:
            coord = coord + body.m*body.v
        coord = coord/self.M
        return coord

    def COMShift(self): #Shift coordinates of bodies in system to
        COM = self.COM  # COM frame and set COM at rest
        COMV = self.COMV
        for body in self.bodylist:
            body.q = body.q - COM
            body.v = body.v - COMV

    @property
    def ECOM(self):  #return total energy in COM frame
        T = np.longdouble(0.)
        W = np.longdouble(0.)
        COM, COMV = self.COM, self.COMV
        for body in self.bodylist:
            T = T + 1./2.*body.m*np.linalg.norm(body.v-COMV)**2
            for otherbody in self.bodylist:
                if body != otherbody:
                    rij = np.linalg.norm(body.q-otherbody.q)
                    W = W - G*otherbody.m*body.m/(2.*rij)
        E = T + W
        return E

    @property
    def LCOM(self): #return angular momentum of bodies in system in COM frame
        L = np.zeros(3,dtype=np.longdouble)
        COM, COMV = self.COM, self.COMV
        for body in self.bodylist:
            L = L + np.cross(body.q-COM,body.p-body.m*COMV)
        return L

    @property
    def eccCOM(self): #exentricity of two body sub system
        if len(self.bodylist) == 2 :
            ecc = np.sqrt((2.*self.ECOM*(np.linalg.norm(self.LCOM)**2))
                    /(G**2*self.M**2*self.mu**3) + 1.)

        else :
            ecc = np.nan
        return ecc

    @property
    def smaCOM(self): #semi major axis of two body sub system
        if len(self.bodylist) == 2 :
            sma = -G*self.mu*self.bodylist[0].m/(2.*self.ECOM)
        else :
            sma = np.nan
        return sma

    @property
    def phi(self): #return angle formed by perturbator plan and reference plan
        if len(self.bodylist) == 3 :
            body1 = self.bodylist[0]
            body2 = self.bodylist[2]
            n1 = np.cross(body1.q-self.COM, body1.v-self.COMV)
            n2 = np.cross(body2.q-self.COM, body2.v-self.COMV)
            n1 = np.array([0., 0., 1.], dtype=np.longdouble)
            phi = np.arccos(np.dot(n1, n2) / (np.linalg.norm(n1) 
                    * np.linalg.norm(n2)))*180./np.pi
        else :
            phi = np.nan
        return phi

