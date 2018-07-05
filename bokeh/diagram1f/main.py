from plotter_bif import *

def G(u, v, J, K):
    return 2*u*K/(v - u + v*J + u*K + np.sqrt((v - u + v*J + u*K)**2 - 4*(v - u)*u*K))

def depletion(R, k):
    k0 = k['value'][k['name']=='k0']
    k1 = k['value'][k['name']=='k1']
    k2 = k['value'][k['name']=='k2']
    k2_ = k['value'][k['name']=='k2_']
    k3 = k['value'][k['name']=='k3']
    k4 = k['value'][k['name']=='k4']
    J3 = k['value'][k['name']=='J3']
    J4 = k['value'][k['name']=='J4']
    return k2*R + k2_*R*G(k3, k4*R, J3, J4) + 0*R

def aggregation(R, S, k):
    k0 = k['value'][k['name']=='k0']
    k1 = k['value'][k['name']=='k1']
    k2 = k['value'][k['name']=='k2']
    k2_ = k['value'][k['name']=='k2_']
    k3 = k['value'][k['name']=='k3']
    k4 = k['value'][k['name']=='k4']
    J3 = k['value'][k['name']=='J3']
    J4 = k['value'][k['name']=='J4']
    return k1*S + k0 + 0*R

def dRdt(R, S, k):
    return aggregation(R, S, k) - depletion(R, k)

k = np.array([('k0', 0.0), ('k1', 0.05), ('k2', 0.1), ('k2_', 0.5), ('k3', 0.10), ('k4', 0.5), ('J3', 0.05), ('J4', 0.05)],
             dtype=[('name', 'U10'), ('value', 'f4')])
kmax = np.array([('k0', 0.05), ('k1', 1.0), ('k2', 1.), ('k2_', 1.), ('k3', 1.0), ('k4', 1.), ('J3', 0.15), ('J4', 0.15)],
             dtype=[('name', 'U10'), ('value', 'f4')])

f1 = plotter_bif(aggregation, depletion, dRdt, _S_0=1,
                 _kvalues=k, _wire_url='diagram1f/static/wire1f.png', _formula_url='diagram1f/static/diff1f.png',
                _N=600, _Rmax=1, _Rmin=0, _Smax=2, _Smin=0, _title='Figure 1f', _kmax=kmax, _imgheight=100)

f1.show_server()
