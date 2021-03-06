#!/usr/bin/python
# -*- coding:utf-8 -*-
from sys import exit as sysexit
from time import time
import numpy as np
import matplotlib.pyplot as plt
from lib.objects import Body, System
from lib.LeapFrog import leapfrog
from lib.hermite import hermite
from lib.plots import display_parameters
from lib.units import *

def main():
    #initialisation
    m = np.array([1., 1., 0.1],
            dtype=np.longdouble)*Ms # Masses in Solar mass
    a = np.array([1.00, 1.00, 7.0],
            dtype=np.longdouble)*au # Semi-major axis in astronomical units
    e = np.array([0., 0., 0.10],
            dtype=np.longdouble)    # Eccentricity
    psi = np.array([0., 0., 80.],
            dtype=np.longdouble)*np.pi/180. # Inclination of the orbital plane in degrees

    x1 = a[0]*(1.+e[0])*np.array([0., -1., 0.],
            dtype=np.longdouble)
    x2 = a[1]*(1.+e[1])*np.array([0., 1., 0.],
            dtype=np.longdouble)
    x3 = a[2]*(1.+e[2])*np.array([np.cos(psi[2]), 0., np.sin(psi[2])],
            dtype=np.longdouble)
    q = np.array([x1, x2, x3],dtype=np.longdouble)

    v1 = np.array([np.sqrt(G*m[0]*m[1]/((m[0]+m[1])*np.sqrt(np.sum((q[0]-q[1])**2)))), 0., 0.],
            dtype=np.longdouble)
    v2 = np.array([-np.sqrt(G*m[0]*m[1]/((m[0]+m[1])*np.sqrt(np.sum((q[0]-q[1])**2)))), 0., 0.],
            dtype=np.longdouble)
    v3 = np.array([0., np.sqrt(G*(m[0]+m[1])*(2./np.sqrt(np.sum(q[2]**2))-1./a[2])), 0.],
            dtype=np.longdouble)
    v = np.array([v1, v2, v3],dtype=np.longdouble)

    #integration parameters
    duration = 500*yr    #integration time in seconds
    step = np.longdouble(100.0/1.*86400.) #integration step in seconds
    integrator = "hermite"
    n_bodies = 3
    display = True
    gif = False
    blackstyle = True
    savename = "{0:d}bodies_{1:s}".format(n_bodies, integrator)
    display_param = True

    #simulation start
    bodylist = []
    for j in range(n_bodies):
        bodylist.append(Body(m[j], q[j], v[j]))
    bin_syst = System(bodylist[0:2])
    dyn_syst = System(bodylist, main=True, blackstyle=blackstyle)
    print("Integration start...")
    t1 = time()

    if integrator.lower() in ['leapfrog', 'frogleap', 'frog']:
        E, L, sma, ecc, phi = leapfrog(dyn_syst, bin_syst, duration,
                step, recover_param=True, display=display, savename=savename, gif=gif)
    elif integrator.lower() in ['hermite','herm']:
        E, L, sma, ecc, phi = hermite(dyn_syst, bin_syst, duration,
                step, recover_param=True, display=display, savename=savename, gif=gif)
    
    t2=time()
    print("...Integration end.\n Elapsed time {0:.3f} sec".format(t2-t1))

    parameters = [duration, [step], dyn_syst, integrator, [a, e, psi]]
    display_parameters([E], [L], [sma], [ecc], [phi], parameters=parameters,
            savename=savename, display_param=display_param)
    return 0

if __name__ == '__main__':
    sysexit(main())
