from plotter_bif import *

def G(u, v, J, K):
    return 2*u*K/(v - u + v*J + u*K + np.sqrt((v - u + v*J + u*K)**2 - 4*(v - u)*u*K))

def depletion(R, k):
    k0 = k['value'][k['name']=='k0']
    k1 = k['value'][k['name']=='k1']
    k2 = k['value'][k['name']=='k2']
    k3 = k['value'][k['name']=='k3']
    k4 = k['value'][k['name']=='k4']
    J3 = k['value'][k['name']=='J3']
    J4 = k['value'][k['name']=='J4']
    return k2*R

def aggregation(R, S, k):
    k0 = k['value'][k['name']=='k0']
    k1 = k['value'][k['name']=='k1']
    k2 = k['value'][k['name']=='k2']
    k3 = k['value'][k['name']=='k3']
    k4 = k['value'][k['name']=='k4']
    J3 = k['value'][k['name']=='J3']
    J4 = k['value'][k['name']=='J4']
    return k1*S + k0*G(k3*R, k4, J3, J4)

def dRdt(R, S, k):
    return aggregation(R, S, k) - depletion(R, k)

k = np.array([('k0', 0.5), ('k1', 0.01), ('k2', 1.0), ('k3', 1.00), ('k4', 0.2), ('J3', 0.05), ('J4', 0.05)],
             dtype=[('name', 'U10'), ('value', 'f4')])

e1 = plotter_bif(aggregation, depletion, dRdt, _S_0=1,
                 _kvalues=k, _wire_url='diagram1e/static/wire1e.png', _formula_url='diagram1e/static/diff1e.png',
                _N=600, _Rmax=1, _Rmin=0, _Smax=15, _Smin=0, _title='Figure 1e')

e1.show_server()
