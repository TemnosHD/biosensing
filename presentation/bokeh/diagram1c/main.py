from plotter import *

def G(u, v, J, K):
    return 2*u*K/(v - u + v*J + u*K + np.sqrt((v - u + v*J + u*K)**2 - 4*(v - u)*u*K))

def Rss(S, k):
    k1 = k['value'][k['name']=='k1']
    k2 = k['value'][k['name']=='k2']
    km1 = k['value'][k['name']=='km1']
    km2 = k['value'][k['name']=='km2']
    R_T = k['value'][k['name']=='R_T']
    return R_T * G(k1*S, k2, km1/R_T, km2/R_T)

def depletion(R, k):
    k1 = k['value'][k['name']=='k1']
    k2 = k['value'][k['name']=='k2']
    km1 = k['value'][k['name']=='km1']
    km2 = k['value'][k['name']=='km2']
    R_T = k['value'][k['name']=='R_T']
    return k2*R / (km2 + R)

def aggregation(R, S, k):
    k1 = k['value'][k['name']=='k1']
    k2 = k['value'][k['name']=='k2']
    km1 = k['value'][k['name']=='km1']
    km2 = k['value'][k['name']=='km2']
    R_T = k['value'][k['name']=='R_T']
    return k1*S*(R_T - R) / (km1 + R_T - R)

k = np.array([('R_T', 1.0), ('k1', 1.0), ('k2', 1.0), ('km1', 0.05), ('km2', 0.05)],
             dtype=[('name', 'U10'), ('value', 'f4')])

c1 = plotter(aggregation, depletion, Rss, _S_0=1,
                 _kvalues=k, _wire_url='diagram1c/static/wire1c.png', _formula_url='diagram1c/static/diff1c.png',
                _N=200, _Rmax=1, _Rmin=0, _Smax=3, _Smin=0, _title='Figure 1c', _imgheight=130)

c1.show_server()
