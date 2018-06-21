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
class plotter_bif:
    def __init__(self, _aggr, _depl, _dRdt, _S_0,
                 _kvalues=np.ones(7), _wire_url=0, _formula_url=0,
                _N=200, _Rmax=2, _Rmin=0, _Smax=3, _Smin=0, _title='test', _R0=0):
        self.aggregation = _aggr
        self.depletion = _depl
        self.dRdt = _dRdt
        self.kvalues = _kvalues
        self.N = _N #density of plot points
        self.Rmax = _Rmax
        self.Rmin = _Rmin
        self.Smax = _Smax
        self.Smin = _Smin
        self.S = _S_0
        S0 = [_S_0] #this is necessary since some struct need a list as input
        self.wire_url = _wire_url
        self.formula_url = _formula_url
        self.title = _title
        self.R = _R0
        
        # Set up data
        R_x = np.linspace(self.Rmin, self.Rmax, self.N)
        self.dRmin = np.max(self.depletion(R_x, self.kvalues))
        dR_dt_depl = self.depletion(R_x, self.kvalues)
        dR_dt_aggr = self.aggregation(R_x, self.S, self.kvalues)
        #R_ss = self.Rss(self.S, self.kvalues)
        #dR_dt_ss = self.depletion(R_ss, self.kvalues)
        self.dRmax = max(np.max(dR_dt_depl), np.max(dR_dt_aggr))
        self.dRmin = min(np.min(dR_dt_depl), np.min(dR_dt_aggr))
        
        self.data_dR_dt_R = ColumnDataSource(data=dict(R=R_x, dR_dt_depl=dR_dt_depl, dR_dt_aggr=dR_dt_aggr)) #graphs
        #self.data_dR_dt_R_lines = ColumnDataSource(data=dict(R_ss_y=[R_ss, R_ss], dR_dt_ss_y=[0, depletion(R_ss, self.kvalues)]))#y parallel
        #self.data_dR_dt_R_point_lab = ColumnDataSource(data=dict(R_ss=[R_ss], dR_dt_ss=[dR_dt_ss], lab=["R_ss = %.2f" % R_ss])) #label
        #self.data_dR_dt_R_point = ColumnDataSource(data=dict(R_ss=R_ss, dR_dt_ss=dR_dt_ss)) #label
        #we need to separate this, since bokeh has problem with drawing circles from data in the label structure
        
        #2nd graph, this differs from original graph
        R_y = np.linspace(self.Rmin, self.Rmax, self.N)
        S_x = np.linspace(self.Smin, self.Smax, self.N)
        
        R_, S_ = np.meshgrid(R_y, S_x)
        RS = self.dRdt(R_, S_, self.kvalues)
        R_split = self.split_R(RS, R_)
        S_split = np.split(S_x, self.get_index_Scrit(RS))
        #self.data_S_R = ColumnDataSource(data=dict(R_split=R_split, S_split=S_split))
        
        #implement a list of columnnames and use that list with add to append datasource
        self.data_R_S = []
        self.tags_R_S = []
        for i, r in enumerate(R_split):
            data_ = ColumnDataSource()
            s = S_split[i]
            tag = 's%i' % i
            data_.add(s, tag)
            self.tags_R_S.append([tag])
            for j, _r in  enumerate(r):
                #print(r, _r)
                tag = 'r%i' % j
                data_.add(_r, tag)
                self.tags_R_S[i].append(tag)
            self.data_R_S.append(data_)
        
        
        # Set up widgets
        self.S_var = Slider(title="S", value=self.S, start=self.Smin, end=self.Smax, step=(self.Smax - self.Smin)/100)
        self.k_var = list(np.empty(np.size(self.kvalues)))
        for i, k in enumerate(self.kvalues):
            self.k_var[i] = Slider(title=k['name'], value=k['value'], start=0.0, end=2.0, step=0.01)
            
            
    def signchange2D(self, a):
        #print(a[300])
        asign = np.sign(a)
        return ((np.roll(asign, 1, axis=1) - asign) != 0).astype(int)
    
    def signchange(self, a):
        asign = np.sign(a)
        return ((np.roll(asign, 1) - asign) != 0).astype(int)
    
    def corr_sign(self, a):
        signed = self.signchange2D(a)
        #print(signed[300])
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
        #if np.size(self.get_index_Scrit(RS))==0:
            #return R_
        Rs = R_[self.corr_sign(RS)==1]
        N = np.size(RS, 0)
        result = []
        old_n = 0
        first_ind = 0
        for n in np.append(self.get_index_Scrit(RS), N):
            R = np.empty(n-old_n)
            m = np.sum(self.corr_sign(RS), axis=1)[n-1]
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
        # Set up plot
        #plot_dR_dt = figure(plot_height=600, plot_width=600, title="Depletion/Aggregation Rate",
        #      #tools="crosshair,pan,reset,save,wheel_zoom",
        #      x_range=[self.Rmin, self.Rmax], y_range=[self.dRmin, self.dRmax], toolbar_location="above")

        plot_dR_dt = figure(plot_height=600, plot_width=600, title="Depletion/Aggregation Rate",
              x_range=[self.Rmin, self.Rmax], y_range=[self.dRmin, self.dRmax])
        
        
        plot_dR_dt.line('R', 'dR_dt_aggr', source=self.data_dR_dt_R, line_width=3, line_alpha=0.6)
        plot_dR_dt.line('R', 'dR_dt_depl', source=self.data_dR_dt_R, line_width=3, line_alpha=0.6, color='red')
        #plot_dR_dt.line('R_ss_y', 'dR_dt_ss_y', source=self.data_dR_dt_R_lines, line_width=3, line_alpha=0.6, color='red', line_dash='4 4')
        
        #labels = LabelSet(x='R_ss', y='dR_dt_ss', text='lab', level='glyph',
        #      x_offset=7, y_offset=-25, source=self.data_dR_dt_R_point_lab, render_mode='canvas')
        #plot_dR_dt.add_layout(labels)
        
        #plot_dR_dt.circle('R_ss', 'dR_dt_ss', source=self.data_dR_dt_R_point, fill_color="white", size=10)
        
        plot_dR_dt.yaxis.axis_label = "dR/dt"
        plot_dR_dt.xaxis.axis_label = "R"
        
        plot_dR_dt.toolbar.logo = None
        plot_dR_dt.toolbar_location = None
        
            
        #this part differs to original class 
        plot_R_S= figure(plot_height=600, plot_width=600, title="Steady State Solutions",
                  x_range=[self.Smin, self.Smax], y_range=[self.Rmin, self.Rmax], toolbar_location="above")
        
        for i, x in enumerate(self.tags_R_S):
            s = x[0]
            for j, y in enumerate(x[1:]):
                if j%2 == 1:
                    plot_R_S.line(x=s, y=y, source=self.data_R_S[i], line_width=3, line_alpha=0.6, line_dash='dotted')        
                else:
                    plot_R_S.line(x=s, y=y, source=self.data_R_S[i], line_width=3, line_alpha=0.6)        
        #plot_R_S.circle(x='S_ss', y='R_ss', source=self.data_S_R_point, fill_color="white", size=10)
        
        plot_R_S.yaxis.axis_label = "R_ss"
        plot_R_S.xaxis.axis_label = "S"
        
        plot_R_S.toolbar.logo = None
        plot_R_S.toolbar_location = None
        
        plot_wire = figure(plot_height=200, plot_width=200, x_range=(0,1), y_range=(0,1), title='Wire Diagramm')
        plot_wire.image_url(url=[self.wire_url], x=0, y=1, w=1, h=1)
        
        plot_wire.toolbar.logo = None
        plot_wire.toolbar_location = None
        plot_wire.axis.visible = False
        
        plot_formula = figure(plot_width=200, plot_height=120, x_range=(0,1), y_range=(0,1), title='Formulas')
        plot_formula.image_url(url=[self.formula_url], x=0, y=1, w=1, h=1)
        
        plot_formula.toolbar.logo = None
        plot_formula.toolbar_location = None
        plot_formula.axis.visible = False
        
        return plot_dR_dt, plot_R_S, plot_wire, plot_formula 
        
    def update_data(self, attrname, old, new):
    
        # Get the current slider values
        self.S = self.S_var.value
        S0 = [self.S]
        for i,k in enumerate(self.k_var):
             self.kvalues['value'][i] = k.value
    
        ## update curve
        R_x = np.linspace(self.Rmin, self.Rmax, self.N)
        dR_dt_depl = self.depletion(R_x, self.kvalues)
        dR_dt_aggr = self.aggregation(R_x, self.S, self.kvalues)
        #R_ss = Rss(self.S, self.kvalues)
        
        self.data_dR_dt_R.data = dict(R=R_x, dR_dt_depl=dR_dt_depl, dR_dt_aggr=dR_dt_aggr) #graphs
        #self.data_dR_dt_R_lines.data = dict(R_ss_y=[R_ss, R_ss], dR_dt_ss_y=[0, depletion(R_ss, self.kvalues)])#y parallel
        #self.data_dR_dt_R_point_lab.data = dict(R_ss=[R_ss], dR_dt_ss=[depletion(R_ss, self.kvalues)], lab=["R_ss = %.2f" % R_ss]) #label
        #self.data_dR_dt_R_point.data = dict(R_ss=R_ss, dR_dt_ss=depletion(R_ss, self.kvalues))
          
        #S = np.linspace(self.Smin, self.Smax, self.N)
        #R_y = Rss(S, self.kvalues)
        
        R_y = np.linspace(self.Rmin, self.Rmax, self.N)
        S_x = np.linspace(self.Smin, self.Smax, self.N)
        
        R_, S_ = np.meshgrid(R_y, S_x)
        RS = self.dRdt(R_, S_, self.kvalues)
        R_split = self.split_R(RS, R_)
        S_split = np.split(S_x, self.get_index_Scrit(RS))
        
        #implement a list of column_names and use that list with add to append datasource
        for i, r in enumerate(R_split):
            s = S_split[i]
            tag = 's%i' % i
            self.data_R_S[i].data[tag] = s
            self.tags_R_S[i][0] = tag
            for j, _r in  enumerate(r):
                tag = 'r%i' % j
                self.data_R_S[i].data[tag] = _r
                self.tags_R_S[i][j+1] = tag
        
        #implement a way to add or remove entries to the datastructure for changes in bifurcation number
        
        #self.data_R_S = []
        #self.tags_R_S = []
        #for i, r in enumerate(R_split):
        #    data_ = ColumnDataSource()
        #    s = S_split[i]
        #    tag = 's%i' % i
        #    data_.add(s, tag)
        #    self.tags_R_S.append([tag])
        #    for j, _r in  enumerate(r):
        #        tag = 'r%i' % j
        #        data_.add(_r, tag)
        #        self.tags_R_S[i].append(tag)
        #    self.data_R_S.append(data_)
        
        #self.data_S_R_lines.data=dict(R_ss_y=[0, R_ss], S_ss_y=[self.S, self.S], #y parallel
        #                              R_ss_x=[R_ss, R_ss], S_ss_x=[0, self.S]) #x parallel
        #self.data_S_R_point.data = dict(S_ss=S0, R_ss=R_ss)#dot
    
    def plot(self, doc):
        for w in self.k_var:
            w.on_change('value', self.update_data)
        self.S_var.on_change('value', self.update_data)
        
        # Set up layouts and add to document
        plot_dR_dt, plot_R_S, plot_wire, plot_formula = self.create_figure()
        l = row([column([plot_wire, plot_formula, widgetbox(self.S_var), widgetbox(self.k_var)]),
                 plot_dR_dt, plot_R_S], sizing_mode='fixed', width=1500, height=600)
        doc.add_root(l)
    
    def show_notebook(self):
        handler = FunctionHandler(self.plot)
        app = Application(handler)
        show(app, notebook_url="localhost:8888")
        
    def show_server(self):
        self.plot(curdoc())
        curdoc().title = self.title 
