#!/usr/bin/python
# -*- coding:utf-8 -*-
from sys import exit as sysexit
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from lib.objects import Body, System
from lib.LeapFrog import leapfrog
from lib.hermite import hermite
from lib.plots import display_parameters
from lib.units import *

def main():
    #initialisation
    m = np.array([1., 1., 1e-1],dtype=np.longdouble)*Ms/Ms  # Masses in Solar mass
    a = np.array([1., 1., 5.],dtype=np.longdouble)/2.*au/au   # Semi-major axis in astronomical units
    e = np.array([0., 0., 1./4.],dtype=np.longdouble)   # Eccentricity
    psi = np.array([0., 0., 45.],dtype=np.longdouble)*np.pi/180.    # Inclination of the orbital plane in degrees

    x1 = np.array([0., -1., 0.],dtype=np.longdouble)*a[0]*(1.+e[0])
    x2 = np.array([0., 1., 0.],dtype=np.longdouble)*a[1]*(1.+e[1])
    x3 = np.array([np.cos(psi[2]), 0., np.sin(psi[2])],dtype=np.longdouble)*a[2]*(1.+e[2])
    q = np.array([x1, x2, x3],dtype=np.longdouble)

    v1 = np.array([np.sqrt(Ga*m[0]*m[1]/((m[0]+m[1])*np.sqrt(np.sum((q[0]-q[1])**2)))), 0., 0.],dtype=np.longdouble)
    v2 = np.array([-np.sqrt(Ga*m[0]*m[1]/((m[0]+m[1])*np.sqrt(np.sum((q[0]-q[1])**2)))), 0., 0.],dtype=np.longdouble)
    v3 = np.array([0., np.sqrt(Ga*(m[0]+m[1])*(2./np.sqrt(np.sum(q[2]**2))-1./a[2])), 0.],dtype=np.longdouble)
    v = np.array([v1, v2, v3],dtype=np.longdouble)

    #integration parameters
    duration, step = 100.*yr, np.array([1./(365.25)],dtype=np.longdouble)*yr #integration time and step in seconds
    step = np.sort(step)[::-1]
    integrator = "leapfrog"
    n_bodies = 3
    display = True
    gif = False
    savename = "{0:d}bodies_psi45_{1:s}".format(n_bodies, integrator)
    display_param = True

    bodies, bodysyst = [],[]
    for j in range(n_bodies):
        bodies.append(Body(m[j], q[j], v[j]))
    bin_syst = System(bodies[0:2])
    dyn_syst = System(bodies, main=True)
    bodysyst = [[deepcopy(bin_syst), deepcopy(dyn_syst)] for _ in range(len(step))]

    #simulation start
    exe = ProcessPoolExecutor()
    future_ELae = []
    for i,step0 in enumerate(step):
        if i != 0:
            display = False
        if integrator.lower() in ['leapfrog', 'frogleap', 'frog']:
            future_ELae.append(exe.submit(leapfrog, bodysyst[i][1], bodysyst[i][0], duration, step0, recover_param=True, display=display, savename=savename, gif=gif))
        elif integrator.lower() in ['hermite','herm']:
            future_ELae.append(exe.submit(hermite, bodysyst[i][1], bodysyst[i][0], duration, step0, recover_param=True, display=display, savename=savename, gif=gif))
    
    E, L, sma, ecc, phi = [], [], [], [], []
    for future in future_ELae:
        E0, L0, sma0, ecc0, phi0 = future.result()
        E.append(E0)
        L.append(L0)
        sma.append(sma0)
        ecc.append(ecc0)
        phi.append(phi0)
    parameters = [duration, step, dyn_syst, integrator]
    display_parameters(E, L, sma, ecc, phi, parameters=parameters, savename=savename, display_param=display_param)
    return 0

if __name__ == '__main__':
    sysexit(main())
