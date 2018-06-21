from plotter import *

def Rss (S, k):
    return (k['value'][k['name']=='R_T']*S)/(k['value'][k['name']=='k2'] / k['value'][k['name']=='k1'] + S)

def depletion(R, k):
    return k['value'][k['name']=='k2']*R

def aggregation(R, S, k):
    return k['value'][k['name']=='k1'] * S * (k['value'][k['name']=='R_T'] - R)

k = np.array([('R_T', 1.0), ('k1', 1.0), ('k2', 1.0)],
             dtype=[('name', 'U10'), ('value', 'f4')])

b1 = plotter(aggregation, depletion, Rss, _S_0=1,
                 _kvalues=k, _wire_url='diagram1b/static/wire1b.png', _formula_url='diagram1b/static/diff1b.png',
                _N=200, _Rmax=1, _Rmin=0, _Smax=3, _Smin=0, _title='Figure 1b')

b1.show_server()
