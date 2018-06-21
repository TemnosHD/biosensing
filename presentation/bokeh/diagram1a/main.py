from plotter import *

def Rss (S, k):
    return (k['value'][k['name']=='k0'] + k['value'][k['name']=='k1']*S)/k['value'][k['name']=='k2'] + S*0

def depletion(R, k):
    return k['value'][k['name']=='k2']*R

def aggregation(R, S, k):
    return k['value'][k['name']=='k0'] + k['value'][k['name']=='k1']*S +0*R

k = np.array([('k0', 0.01), ('k1', 1.0), ('k2', 5.0)],
             dtype=[('name', 'U10'), ('value', 'f4')])

a1 = plotter(aggregation, depletion, Rss, _S_0=1,
                 _kvalues=k, _wire_url='diagram1a/static/wire1a.png', _formula_url='diagram1a/static/diff1a.png',
                _N=200, _Rmax=2, _Rmin=0, _Smax=3, _Smin=0, _title='Figure 1a')

a1.show_server()

