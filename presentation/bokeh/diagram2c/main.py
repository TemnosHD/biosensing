from plotter_osc import *

def G(u, v, J, K):
    return 2*u*K/(v - u + v*J + u*K + np.sqrt((v - u + v*J + u*K)**2 - 4*(v - u)*u*K))

def RX(RX, t, S, k0, k0_, k1, k2, k3, k4, J3, J4):
    #k0 = k['value'][k['name']=='k0']
    #k1 = k['value'][k['name']=='k1']
    #k2 = k['value'][k['name']=='k2']
    #k2_ = k['value'][k['name']=='k2_']
    #k3 = k['value'][k['name']=='k3']
    #k4 = k['value'][k['name']=='k4']
    #k5 = k['value'][k['name']=='k5']
    #k6 = k['value'][k['name']=='k6']
    #J3 = k['value'][k['name']=='J3']
    #J4 = k['value'][k['name']=='J4']
    return np.array([   k1*S - (k0_+k0*G(k3*RX[1], k4, J3, J4))*RX[0],
                        (k0_ + k0*G(k3*RX[1], k4, J3, J4))*RX[0] - k2*RX[1] ])

RX0 = [1., 1.]

k = np.array([('k0', .4), ('k0_', .01), ('k1', 1.0), ('k2', 1.0), ('k3', 1.0), ('k4', .3), ('J3', 0.05), ('J4', 0.05)],
             dtype=[('name', 'U10'), ('value', 'f4')])

c2 = plotter_osc(RX, RX0, _S_0=0.2,
                 _kvalues=k, _wire_url='diagram2c/static/wire2c.png', _formula_url='diagram2c/static/diff2c.png',
                _N=600, _Rmax=1.6, _Rmin=0, _Smax=0.5, _Smin=0, _Xmax=7, _title='Figure 2c', _quivleng=10)


b2.show_server()
