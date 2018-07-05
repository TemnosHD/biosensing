# Add all necessary imports here
import pandas as pd
import numpy as np

from bokeh.layouts import column, row, widgetbox, Spacer, layout
from bokeh.io import push_notebook, show, output_notebook, curdoc
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.models import ColumnDataSource, Select, LabelSet, Label
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure
output_notebook()


#implement class plotter that plots everything that is necessary
from scipy.integrate import odeint
np.set_printoptions(threshold=10)
from bokeh.palettes import viridis

class plotter_osc:
    def __init__(self, _RX, _RX0, _S_0=0,
                 _kvalues=np.ones(7), _wire_url=0, _formula_url=0,
                 _N=200, _Rmax=2, _Rmin=0, _Smax=3, _Smin=0, _Xmax=1.5, _Xmin=0,
                 _title='test', _R0=0, _quivleng=5, _imgheight=120, _kmax=0):
        self.RX = _RX
        self.RX0 = _RX0
        self.kvalues = _kvalues
        self.N = _N #density of plot points
        self.Rmax = _Rmax
        self.Rmin = _Rmin
        self.Smax = _Smax
        self.Smin = _Smin
        self.Xmax = _Xmax
        self.Xmin = _Xmin
        self.S = _S_0
        S0 = [_S_0] #this is necessary since some struct need a list as input
        self.wire_url = _wire_url
        self.formula_url = _formula_url
        self.title = _title
        self.quivleng = _quivleng
        self.imgheight=_imgheight
        
        if (np.size(_kmax)==1):
            self.kmax=np.array(_kvalues)
            self.kmax[:]['value'] = self.kmax[:]['value']*2
        else:
            self.kmax=_kmax
        
        
        # Set up data
        t = np.arange(0, 80, .1)
        xx = np.linspace(self.Xmin, self.Xmax, self.N)
        rr = np.linspace(self.Rmin, self.Rmax, self.N)
        pars = tuple(np.insert(self.kvalues['value'], 0, self.S))
        y = odeint(_RX, _RX0, t, pars)
        # defines a grid of points
        X, R = np.meshgrid(xx, rr)
        # calculates the value of the derivative at the point in the grid
        dy = self.RX(np.array([X, R]), 0, *pars)
        

        speed = np.sqrt(dy[0]**2 + dy[1]**2)
        theta = np.arctan(dy[1]/dy[0])

        d = 40 #density
        x0 = X[::d, ::d].flatten()
        y0 = R[::d, ::d].flatten()
        length = speed[::d, ::d].flatten()/_quivleng
        angle = theta[::d, ::d].flatten()
        x1 = x0 + length * np.cos(angle)
        y1 = y0 + length * np.sin(angle)
        
        #cm = np.array(["#C7E9B4", "#7FCDBB", "#41B6C4", "#1D91C0", "#225EA8", "#0C2C84"])
        cm = np.array(viridis(6))
        ix = ((length-length.min())/(length.max()-length.min())*5).astype('int')
        colors = cm[ix]
        
        self.data_X_R_traj = ColumnDataSource(data=dict(X=y[:,0], R=y[:,1]))
        self.data_X_R_quiv = ColumnDataSource(data=dict(x0=x0, y0=y0, x1=x1, y1=y1, colors=colors))
        
        #find nullclines like for plotter_bif
        R2, X2 = np.meshgrid(rr, xx)
        dy = self.RX(np.array([X2, R2]), 0, *pars)
        R_split1 = self.split_R(dy[0], R2)
        X_split1 = np.split(xx, self.get_index_Scrit(dy[0]))
        R_split2 = self.split_R(dy[1], R2)
        X_split2 = np.split(xx, self.get_index_Scrit(dy[1]))
        for ind, x in enumerate(np.insert(self.get_index_Scrit(dy[1]), 0, 0)):
            if np.sum(self.corr_sign(dy[1]), axis=1)[x] == 0:
                X_split2 = np.delete(X_split2, ind)
        for ind, x in enumerate(np.insert(self.get_index_Scrit(dy[0]), 0, 0)):
            if np.sum(self.corr_sign(dy[0]), axis=1)[x] == 0:
                X_split1 = np.delete(X_split1, ind)
                
        #self.data_S_R = ColumnDataSource(data=dict(R_split=R_split, S_split=S_split))
        R = np.array([])
        R_dotted = np.array([])
        X = np.array([])
        X_dotted = np.array([])
        self.data_R_S1 = ColumnDataSource()
        self.data_R_S1_dotted = ColumnDataSource()
        
        for i, r_ in enumerate(R_split1):
            for j, r in enumerate(r_):
                s = X_split1[i]
                _r = r
                _s = s
                if j%2 == 1:
                    _r = np.flip(r, 0)
                    _s = np.flip(s, 0)
                    R_dotted = np.append(R_dotted, _r)
                    X_dotted = np.append(X_dotted, _s)
                R = np.append(R, _r)
                X = np.append(X, _s)
        self.data_R_S1.add(R, "R")
        self.data_R_S1.add(X, "X")
        self.data_R_S1_dotted.add(R_dotted, "R")
        self.data_R_S1_dotted.add(X_dotted, "X")
        
        R = np.array([])
        R_dotted = np.array([])
        X = np.array([])
        X_dotted = np.array([])
        self.data_R_S2 = ColumnDataSource()
        self.data_R_S2_dotted = ColumnDataSource()
        
        for i, r_ in enumerate(R_split2):
            for j, r in enumerate(r_):
                s = X_split2[i]
                _r = r
                _s = s
                if j%2 == 1:
                    _r = np.flip(r, 0)
                    _s = np.flip(s, 0)
                    R_dotted = np.append(R_dotted, _r)
                    X_dotted = np.append(X_dotted, _s)
                R = np.append(R, _r)
                X = np.append(X, _s)
        self.data_R_S2.add(R, "R")
        self.data_R_S2.add(X, "X")
        self.data_R_S2_dotted.add(R_dotted, "R")
        self.data_R_S2_dotted.add(X_dotted, "X")
        
        #implement a list of columnnames and use that list with add to append datasource
        #self.data_X_R_null1 = []
        #self.tags_X_R_null1 = []
        #for i, r in enumerate(R_split1):
        #    data_ = ColumnDataSource()
        #    x = X_split1[i]
        #    tag = 'x%i' % i
        #    data_.add(x, tag)
        #    self.tags_X_R_null1.append([tag])
        #    for j, _r in  enumerate(r):
        #        #print(r, _r)
        #        tag = 'r%i' % j
        #        data_.add(_r, tag)
        #        self.tags_X_R_null1[i].append(tag)
        #    self.data_X_R_null1.append(data_)
        #self.data_X_R_null2 = []
        #self.tags_X_R_null2 = []
        #for i, r in enumerate(R_split2):
        #    data_ = ColumnDataSource()
        #    x = X_split2[i]
        #    tag = 'x%i' % i
        #    data_.add(x, tag)
        #    self.tags_X_R_null2.append([tag])
        #    for j, _r in  enumerate(r):
        #        #print(r, _r)
        #        tag = 'r%i' % j
        #        data_.add(_r, tag)
        #        self.tags_X_R_null2[i].append(tag)
        #    self.data_X_R_null2.append(data_)
        
        #use critical indeces to split both graphs even further, then compare all subarrays with one another by subtracting.
        # if the suctraction crosses 0 (signchange) mark that point and add it to coulmndata source
        
        #2nd graph, this differs from original graph
        R_y = np.linspace(self.Rmin, self.Rmax, self.N)
        S_x = np.linspace(self.Smin, self.Smax, self.N)
        
        ymin = []
        ymax = []
        yss = []
        alphapoint = []
        alphaline = []
        S = np.arange(self.Smin, self.Smax, .01)
        t = np.arange(0, 400, .4)
        # loop over the values of s (S)
        for s in S:
            # redefine the parameters using the new S
            pars = tuple(np.insert(self.kvalues['value'], 0, s))
            # integrate again the equation, with new parameters
            y = odeint(_RX, _RX0, t, pars)
            # calculate the minimum and maximum of the populations, but
            # only for the last 200 steps (the long-term solution),
            # appending the result to the list
            ymin.append(y[-500:,:].min(axis=0))
            ymax.append(y[-500:,:].max(axis=0))
            
            #find nullclines like for plotter_bif
            R2, X2 = np.meshgrid(rr, xx)
            dy = self.RX(np.array([X2, R2]), 0, *pars)
            #get length of all points and choose the one with the shortest length
            lengths = dy[0]**2 + dy[1]**2
            yss.append(R2[int(np.argmin(lengths)/np.size(lengths, axis=1)), np.argmin(lengths)%np.size(lengths, axis=1)])
            
            if ymax[-1][1] - ymin[-1][1] < 0.1:
                alphapoint.append(0.0)
                alphaline.append(0.9)
            else:
                alphapoint.append(0.9)
                alphaline.append(0.0)
            #add an alpha value to ymax and ymin depending on how close these values are!
            #do an inverse, that can be used for a line, which should give solid line in the end
            
            
            #R_split1 = self.split_R(dy[0], R2)
            #X_split1 = np.split(xx, self.get_index_Scrit(dy[0]))
            #R_split2 = self.split_R(dy[1], R2)
            #X_split2 = np.split(xx, self.get_index_Scrit(dy[1]))
            #for ind, x in enumerate(np.insert(self.get_index_Scrit(dy[1]), 0, 0)):
            #    if np.sum(self.corr_sign(dy[1]), axis=1)[x] == 0:
            #        X_split2 = np.delete(X_split2, ind)
            #for ind, x in enumerate(np.insert(self.get_index_Scrit(dy[0]), 0, 0)):
            #    if np.sum(self.corr_sign(dy[0]), axis=1)[x] == 0:
            #        X_split1 = np.delete(X_split1, ind)
                
                
        # convert the lists into arrays
        ymin = np.array(ymin)
        ymax = np.array(ymax)
        yss = np.array(yss)
        alphapoint = np.array(alphapoint)
        alphaline = np.array(alphaline)
        
        self.data_S_R = ColumnDataSource(data=dict(S=S, ymin=ymin[:,1], ymax=ymax[:,1], yss=yss[:], alphapoint=alphapoint, alphaline=alphaline))
        
        # Set up widgets
        self.S_var = Slider(title="S", value=self.S, start=self.Smin, end=self.Smax, step=(self.Smax - self.Smin)/100)
        self.k_var = list(np.empty(np.size(self.kvalues)))
        for i, k in enumerate(self.kvalues):
            self.k_var[i] = Slider(title=k['name'], value=k['value'], start=0.0, end=self.kmax[i]['value'], step=0.01)            
    
    def signchange2D(self, a):
        #print(a[300])
        asign = np.sign(a)
        return ((np.roll(asign, 1, axis=1) - asign) != 0).astype(int)
    
    def signchange(self, a):
        asign = np.sign(a)
        return ((np.roll(asign, 1) - asign) != 0).astype(int)
    
    def corr_sign(self, a):
        signed = self.signchange2D(a)
        #get rid of preceeeding 1 due to wrap around -> correct all 1s at [0] and then roll left
        signed[:, 0] = 0
        signed = np.roll(signed, -1, axis=1)
        return signed
    
    #get indices that have equal numbers of root / get subarrays
    def get_index_Scrit(self, a):
        roots = np.sum(self.corr_sign(a), axis=1)
        #print(roots)
        root_indeces = np.array([0])
        #the first index is always the beginning of a subarray
        
        #use np.roll to find 'signchanges' in mask
        for n in np.unique(roots):
            mask = np.isin(roots, n)
            mask = mask.astype(int)
            changes = self.signchange(mask)
            #changes[:, 0] = 1
            #mark first element, as the first element of each subarray is marked
            indeces = np.argwhere(changes==1)
            root_indeces = np.append(root_indeces, indeces)
            
        return np.unique(root_indeces)[1:]
        #return only unique indeces, since some indeces might appear more often
        #also 0 index is not needed
        
    def split_R(self, RS, R_):
        #print(RS)
        #print(R_)
        #if np.size(self.get_index_Scrit(RS))==0: #if there is no critical point, then R is not split
        #    print([R_])
        #    return np.array([R_])
        Rs = R_[self.corr_sign(RS)==1] #Rs contains the y-values at each critical point
        #print(Rs)
        #print('end')
        N = np.size(RS, 0)
        result = []
        old_n = 0
        first_ind = 0
        for n in np.append(self.get_index_Scrit(RS), N):
            R = np.empty(n-old_n)
            m = np.sum(self.corr_sign(RS), axis=1)[n-1]
            if m == 0:
                old_n = n
                continue
            #get #roots
            #print(first_ind, old_n, m, n)
            for i in range(m):
                #print(i, m, n, first_ind, old_n , np.shape(R), np.shape(Rs), np.shape(Rs[first_ind+i:first_ind+(n-old_n)*m+i:m]))
                #R = np.vstack((R, Rs[first_ind+i:first_ind+m*n+i:m]))
                R = np.vstack((R, Rs[first_ind+i:first_ind+(n-old_n)*m+i:m]))
                #start:stop:step, stop is not inclusive
            result.append(R[1:])
            #get rid of preceeding zeros
            #first_ind = first_ind+m*n
            first_ind = first_ind+(n-old_n)*m
            old_n = n
        return result
            
    def create_figure(self):

        plot_X_R = figure(plot_height=800, plot_width=600, title="X-R-Plane",
              x_range=[self.Xmin, self.Xmax], y_range=[self.Rmin, self.Rmax])
        
        plot_X_R.line('X', 'R', source=self.data_X_R_traj, line_width=3, line_alpha=0.6, color='black')
        plot_X_R.segment('x0', 'y0', 'x1', 'y1', color='colors', source=self.data_X_R_quiv, line_width=2)
        
        
        plot_X_R.line(x='X', y='R', source=self.data_R_S1, line_width=3, line_alpha=0.6, color='crimson')        
        plot_X_R.line(x='X', y='R', source=self.data_R_S1_dotted, line_width=3, line_alpha=1., line_dash='dotted', color='white')        
        plot_X_R.line(x='X', y='R', source=self.data_R_S2, line_width=3, line_alpha=0.6, color='steelblue')        
        plot_X_R.line(x='X', y='R', source=self.data_R_S2_dotted, line_width=3, line_alpha=1., line_dash='dotted', color='white')        
        #for i, s in enumerate(self.tags_X_R_null1):
        #    x = s[0]
        #    for j, y in enumerate(s[1:]):
        #        if j%2 == 1:
        #            plot_X_R.line(x=x, y=y, source=self.data_X_R_null1[i], line_width=3, line_alpha=0.6, line_dash='dotted', color='crimson')        
        #        else:
        #            plot_X_R.line(x=x, y=y, source=self.data_X_R_null1[i], line_width=3, line_alpha=0.6, color='crimson')  
        #
        #for i, s in enumerate(self.tags_X_R_null2):
        #    x = s[0]
        #    for j, y in enumerate(s[1:]):
        #        if j%2 == 1:
        #            plot_X_R.line(x=x, y=y, source=self.data_X_R_null2[i], line_width=3, line_alpha=0.6, line_dash='dotted', color='steelblue')        
        #        else:
        #            plot_X_R.line(x=x, y=y, source=self.data_X_R_null2[i], line_width=3, line_alpha=0.6, color='steelblue')  
        
        plot_X_R.yaxis.axis_label = "R"
        plot_X_R.xaxis.axis_label = "X"
        
        plot_X_R.toolbar.logo = None
        plot_X_R.toolbar_location = None
        
            
        #this part differs to original class 
        plot_R_S= figure(plot_height=800, plot_width=600, title="Steady State Solutions",
                  x_range=[self.Smin, self.Smax], y_range=[self.Rmin, self.Rmax], toolbar_location="above")
        
        plot_R_S.circle('S', 'ymin', alpha='alphapoint', source=self.data_S_R, color='black')
        plot_R_S.circle('S', 'ymax', alpha='alphapoint', source=self.data_S_R, color='black')
        plot_R_S.line('S', 'ymin', source=self.data_S_R, line_width=3, line_alpha=0.6, color='black')
        plot_R_S.line('S', 'ymax', source=self.data_S_R, line_width=3, line_alpha=0.6, color='black')
        plot_R_S.line('S', 'yss', source=self.data_S_R, line_width=3, line_alpha=0.6, line_dash='dashed', color='black')
        
        plot_R_S.yaxis.axis_label = "R"
        plot_R_S.xaxis.axis_label = "S"
        
        plot_R_S.toolbar.logo = None
        plot_R_S.toolbar_location = None
        
        plot_wire = figure(plot_height=300, plot_width=300, x_range=(0,1), y_range=(0,1), title='Wire Diagramm')
        plot_wire.image_url(url=[self.wire_url], x=0, y=1, w=1, h=1)
        
        plot_wire.toolbar.logo = None
        plot_wire.toolbar_location = None
        plot_wire.axis.visible = False
        
        plot_formula = figure(plot_width=300, plot_height=self.imgheight, x_range=(0,1), y_range=(0,1), title='Formulas')
        plot_formula.image_url(url=[self.formula_url], x=.01, y=.99, w=.98, h=.98)
        
        plot_formula.toolbar.logo = None
        plot_formula.toolbar_location = None
        plot_formula.axis.visible = False
        
        return plot_X_R, plot_R_S, plot_wire, plot_formula 
        
    def update_data(self, attrname, old, new):
    
        # Get the current slider values
        self.S = self.S_var.value
        S0 = [self.S]
        for i,k in enumerate(self.k_var):
             self.kvalues['value'][i] = k.value
    
        ## update curve
        # Set up data
        t = np.arange(0, 80, .1)
        xx = np.linspace(self.Xmin, self.Xmax, self.N)
        rr = np.linspace(self.Rmin, self.Rmax, self.N)
        pars = tuple(np.insert(self.kvalues['value'], 0, self.S))
        y = odeint(self.RX, self.RX0, t, pars)
        # defines a grid of points
        X, R = np.meshgrid(xx, rr)
        # calculates the value of the derivative at the point in the grid
        dy = self.RX(np.array([X, R]), 0, *pars)
        

        speed = np.sqrt(dy[0]**2 + dy[1]**2)
        theta = np.arctan(dy[1]/dy[0])

        d = 40 #density
        x0 = X[::d, ::d].flatten()
        y0 = R[::d, ::d].flatten()
        length = speed[::d, ::d].flatten()/self.quivleng
        angle = theta[::d, ::d].flatten()
        x1 = x0 + length * np.cos(angle)
        y1 = y0 + length * np.sin(angle)
        
        #cm = np.array(["#C7E9B4", "#7FCDBB", "#41B6C4", "#1D91C0", "#225EA8", "#0C2C84"])
        cm = np.array(viridis(6))
        ix = ((length-length.min())/(length.max()-length.min())*5).astype('int')
        colors = cm[ix]
        
        self.data_X_R_traj.data = dict(X=y[:,0], R=y[:,1])
        self.data_X_R_quiv.data = dict(x0=x0, y0=y0, x1=x1, y1=y1, colors=colors)
        
        #find nullclines like for plotter_bif
        R2, X2 = np.meshgrid(rr, xx)
        dy = self.RX(np.array([X2, R2]), 0, *pars)
        R_split1 = self.split_R(dy[0], R2)
        X_split1 = np.split(xx, self.get_index_Scrit(dy[0]))
        R_split2 = self.split_R(dy[1], R2)
        X_split2 = np.split(xx, self.get_index_Scrit(dy[1]))
        for ind, x in enumerate(np.insert(self.get_index_Scrit(dy[1]), 0, 0)):
            if np.sum(self.corr_sign(dy[1]), axis=1)[x] == 0:
                X_split2 = np.delete(X_split2, ind)
        for ind, x in enumerate(np.insert(self.get_index_Scrit(dy[0]), 0, 0)):
            if np.sum(self.corr_sign(dy[0]), axis=1)[x] == 0:
                X_split1 = np.delete(X_split1, ind)
                
        #self.data_S_R = ColumnDataSource(data=dict(R_split=R_split, S_split=S_split))
        
        #implement a list of columnnames and use that list with add to append datasource
        R = np.array([])
        R_dotted = np.array([])
        X = np.array([])
        X_dotted = np.array([])
        
        for i, r_ in enumerate(R_split1):
            for j, r in enumerate(np.flip(r_, 0)):
                s = X_split1[i]
                _r = r
                _s = s
                if j%2 == 1:
                    _r = np.flip(r, 0)
                    _s = np.flip(s, 0)
                    R_dotted = np.append(R_dotted, _r)
                    X_dotted = np.append(X_dotted, _s)
                R = np.append(R, _r)
                X = np.append(X, _s)
        self.data_R_S1.data["R"] = R
        self.data_R_S1.data["X"] = X
        self.data_R_S1_dotted.data["R"] = R_dotted
        self.data_R_S1_dotted.data["X"] = X_dotted
        
        R = np.array([])
        R_dotted = np.array([])
        X = np.array([])
        X_dotted = np.array([])
        
        for i, r_ in enumerate(R_split2):
            for j, r in enumerate(np.flip(r_, 0)):
                s = X_split2[i]
                _r = r
                _s = s
                if j%2 == 1:
                    _r = np.flip(r, 0)
                    _s = np.flip(s, 0)
                    R_dotted = np.append(R_dotted, _r)
                    X_dotted = np.append(X_dotted, _s)
                R = np.append(R, _r)
                X = np.append(X, _s)
        self.data_R_S2.data["R"] = R
        self.data_R_S2.data["X"] = X
        self.data_R_S2_dotted.data["R"] = R_dotted
        self.data_R_S2_dotted.data["X"] = X_dotted
                
    def plot(self, doc):
        for w in self.k_var:
            w.on_change('value', self.update_data)
        self.S_var.on_change('value', self.update_data)
        
        # Set up layouts and add to document
        plot_dR_dt, plot_R_S, plot_wire, plot_formula = self.create_figure()
        l = row([column([plot_wire, plot_formula, widgetbox(self.S_var), row([widgetbox(self.k_var[0::2], width=150), widgetbox(self.k_var[1::2], width=150)])]),
                 plot_dR_dt, plot_R_S], sizing_mode='fixed', width=1500, height=800)
        doc.add_root(l)
    
    def show_notebook(self):
        handler = FunctionHandler(self.plot)
        app = Application(handler)
        show(app, notebook_url="localhost:8888")
        
    def show_server(self):
        self.plot(curdoc())
        curdoc().title = self.title 
