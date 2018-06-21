from plotter_osc import *

def G(u, v, J, K):
    return 2*u*K/(v - u + v*J + u*K + np.sqrt((v - u + v*J + u*K)**2 - 4*(v - u)*u*K))

def RX(RX, t, S, k0, k1, k2, k2_, k3, k4, k5, k6, J3, J4):
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
    return np.array([   k5*RX[1] - k6*RX[0],
                        k0*G(k3*RX[1], k4, J3, J4) + k1*S - k2*RX[1] - k2_*RX[1]*RX[0]])

RX0 = [1., 1.]

k = np.array([('k0', 4.0), ('k1', 1.0), ('k2', 1.0), ('k2_', 1.0), ('k3', 1.0), ('k4', 1.0), ('k5', 0.1), ('k6', 0.075), ('J3', 0.3), ('J4', 0.3)],
             dtype=[('name', 'U10'), ('value', 'f4')])

b2 = plotter_osc(RX, RX0, _S_0=0.1,
                 _kvalues=k, _wire_url='diagram2b/static/wire2b.png', _formula_url='diagram2b/static/diff2b.png',
                _N=600, _Rmax=2.5, _Rmin=0, _Smax=0.5, _Smin=0, _title='Figure 2b', _quivleng=5)

b2.show_server()
