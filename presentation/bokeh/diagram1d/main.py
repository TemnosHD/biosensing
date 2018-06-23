from plotter import *

def Rss(S, k):
    k1 = k['value'][k['name']=='k1']
    k2 = k['value'][k['name']=='k2']
    k3 = k['value'][k['name']=='k3']
    k4 = k['value'][k['name']=='k4']
    return k1*k4/k2/k3 + 0*S

def Xss(S, k):
    k1 = k['value'][k['name']=='k1']
    k2 = k['value'][k['name']=='k2']
    k3 = k['value'][k['name']=='k3']
    k4 = k['value'][k['name']=='k4']
    return k3*S/k4 

def depletion(R, S, k):
    k1 = k['value'][k['name']=='k1']
    k2 = k['value'][k['name']=='k2']
    k3 = k['value'][k['name']=='k3']
    k4 = k['value'][k['name']=='k4']
    return k2*Xss(S, k)*R

def aggregation(R, S, k):
    k1 = k['value'][k['name']=='k1']
    k2 = k['value'][k['name']=='k2']
    k3 = k['value'][k['name']=='k3']
    k4 = k['value'][k['name']=='k4']
    return k1*S + 0*R

k = np.array([('k1', 2.0), ('k2', 2.0), ('k3', 1.0), ('k4', 1.0)],
             dtype=[('name', 'U10'), ('value', 'f4')])

d1 = plotter(aggregation, depletion, Rss, _S_0=1,
                 _kvalues=k, _wire_url='diagram1c/static/wire1d.png', _formula_url='diagram1c/static/diff1d.png',
                _N=200, _Rmax=1, _Rmin=0, _Smax=3, _Smin=0, _title='Figure 1d', _imgheight=300)

d1.show_server()
