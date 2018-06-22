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
class plotter:
    def __init__(self, _aggr, _depl, _Rss, _S_0,
                 _kvalues=np.ones(7), _kmax=np.array(7), _wire_url=0, _formula_url=0,
                _N=200, _Rmax=2, _Rmin=0, _Smax=3, _Smin=0, _title='test', _imgheight=200):
        self.aggregation = _aggr
        self.depletion = _depl
        self.Rss = _Rss
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
        if (_kmax.all==np.zeros(7)).all:
            self.kmax=np.array(_kvalues)
            self.kmax[:]['value'] = self.kmax[:]['value']*2
        else:
            self.kmax=_kmax
            
        self.imgheight=_imgheight
        
        # Set up data
        R_x = np.linspace(self.Rmin, self.Rmax, self.N)
        self.dRmin = np.max(self.depletion(R_x, self.kvalues))
        dR_dt_depl = self.depletion(R_x, self.kvalues)
        dR_dt_aggr = self.aggregation(R_x, self.S, self.kvalues)
        R_ss = self.Rss(self.S, self.kvalues)
        dR_dt_ss = self.depletion(R_ss, self.kvalues)
        self.dRmax = max(np.max(dR_dt_depl), np.max(dR_dt_aggr))
        self.dRmin = min(np.min(dR_dt_depl), np.min(dR_dt_aggr))
        
        self.data_dR_dt_R = ColumnDataSource(data=dict(R=R_x, dR_dt_depl=dR_dt_depl, dR_dt_aggr=dR_dt_aggr)) #graphs
        self.data_dR_dt_R_lines = ColumnDataSource(data=dict(R_ss_y=[R_ss[0], R_ss[0]], dR_dt_ss_y=[0, self.depletion(R_ss[0], self.kvalues)]))#y parallel
        self.data_dR_dt_R_point_lab = ColumnDataSource(data=dict(R_ss=[R_ss], dR_dt_ss=[dR_dt_ss], lab=["R_ss = %.2f" % R_ss])) #label
        self.data_dR_dt_R_point = ColumnDataSource(data=dict(R_ss=R_ss, dR_dt_ss=dR_dt_ss)) #label
        #we need to separate this, since bokeh has problem with drawing circles from data in the label structure
        
        S = np.linspace(self.Smin, self.Smax, self.N)
        R_y = self.Rss(S, self.kvalues)
        self.data_S_R = ColumnDataSource(data=dict(S=S, R=R_y))
        self.data_S_R_lines = ColumnDataSource(data=dict(R_ss_y=[0, R_ss[0]], S_ss_y=[self.S, self.S], #y and x parallel
                                                    R_ss_x=[R_ss[0], R_ss[0]], S_ss_x=[0, self.S]))
        self.data_S_R_point = ColumnDataSource(data=dict(S_ss=S0, R_ss=R_ss))#dot
        
        # Set up widgets
        self.S_var = Slider(title="S", value=self.S, start=self.Smin, end=self.Smax, step=(self.Smax - self.Smin)/100)
        self.k_var = list(np.empty(np.size(self.kvalues)))
        for i, k in enumerate(self.kvalues):
            self.k_var[i] = Slider(title=k['name'], value=k['value'], start=0.0, end=self.kmax[i]['value'], step=0.01)
    
    def create_figure(self):
        # Set up plot
        #plot_dR_dt = figure(plot_height=600, plot_width=600, title="Depletion/Aggregation Rate",
        #      #tools="crosshair,pan,reset,save,wheel_zoom",
        #      x_range=[self.Rmin, self.Rmax], y_range=[self.dRmin, self.dRmax], toolbar_location="above")

        plot_dR_dt = figure(plot_height=800, plot_width=600, title="Depletion/Aggregation Rate",
              x_range=[self.Rmin, self.Rmax], y_range=[self.dRmin, self.dRmax])
        
        
        plot_dR_dt.line('R', 'dR_dt_depl', source=self.data_dR_dt_R, line_width=3, line_alpha=0.6, color='crimson')
        plot_dR_dt.line('R', 'dR_dt_aggr', source=self.data_dR_dt_R, line_width=3, line_alpha=0.6, color='steelblue')
        plot_dR_dt.line('R_ss_y', 'dR_dt_ss_y', source=self.data_dR_dt_R_lines, line_width=3, line_alpha=0.6, color='red', line_dash='4 4')
        
        labels = LabelSet(x='R_ss', y='dR_dt_ss', text='lab', level='glyph',
              x_offset=7, y_offset=-25, source=self.data_dR_dt_R_point_lab, render_mode='canvas')
        plot_dR_dt.add_layout(labels)
        
        plot_dR_dt.circle('R_ss', 'dR_dt_ss', source=self.data_dR_dt_R_point, fill_color="white", size=10)
        
        plot_dR_dt.yaxis.axis_label = "dR/dt"
        plot_dR_dt.xaxis.axis_label = "R"
        
        plot_dR_dt.toolbar.logo = None
        plot_dR_dt.toolbar_location = None
        
            
            
        plot_R_S= figure(plot_height=800, plot_width=600, title="Steady State Solutions",
                  #tools="crosshair,pan,reset,save,wheel_zoom",
                  x_range=[self.Smin, self.Smax], y_range=[self.Rmin, self.Rmax], toolbar_location="above")
    
        plot_R_S.line('S', 'R', source=self.data_S_R, line_width=3, line_alpha=0.6, color='black')
        plot_R_S.line('S_ss_y', 'R_ss_y', source=self.data_S_R_lines, line_width=3, line_alpha=0.6, color='black', line_dash='4 4')
        plot_R_S.line('S_ss_x', 'R_ss_x', source=self.data_S_R_lines, line_width=3, line_alpha=0.6, color='red', line_dash='4 4')
        
        plot_R_S.circle(x='S_ss', y='R_ss', source=self.data_S_R_point, fill_color="white", size=10)
        
        plot_R_S.yaxis.axis_label = "R_ss"
        plot_R_S.xaxis.axis_label = "S"
        
        plot_R_S.toolbar.logo = None
        plot_R_S.toolbar_location = None
        
        plot_wire = figure(plot_height=300, plot_width=300, x_range=(0,1), y_range=(0,1), title='Wire Diagramm')
        plot_wire.image_url(url=[self.wire_url], x=0, y=1, w=1, h=1)
        
        plot_wire.toolbar.logo = None
        plot_wire.toolbar_location = None
        plot_wire.axis.visible = False
        
        plot_formula = figure(plot_width=300, plot_height=self.imgheight, x_range=(0,1), y_range=(0,1), title='Formulas')
        plot_formula.image_url(url=[self.formula_url], x=0.01, y=0.99, w=0.98, h=0.98)
        
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
        R_ss = self.Rss(self.S, self.kvalues)
        
        self.data_dR_dt_R.data = dict(R=R_x, dR_dt_depl=dR_dt_depl, dR_dt_aggr=dR_dt_aggr) #graphs
        self.data_dR_dt_R_lines.data = dict(R_ss_y=[R_ss[0], R_ss[0]], dR_dt_ss_y=[0, self.depletion(R_ss[0], self.kvalues)])#y parallel
        self.data_dR_dt_R_point_lab.data = dict(R_ss=[R_ss], dR_dt_ss=[self.depletion(R_ss, self.kvalues)], lab=["R_ss = %.2f" % R_ss]) #label
        self.data_dR_dt_R_point.data = dict(R_ss=R_ss, dR_dt_ss=self.depletion(R_ss, self.kvalues))
          
        S = np.linspace(self.Smin, self.Smax, self.N)
        R_y = self.Rss(S, self.kvalues)
        self.data_S_R.data = dict(S=S, R=R_y)
        self.data_S_R_lines.data=dict(R_ss_y=[0, R_ss[0]], S_ss_y=[self.S, self.S], #y parallel
                                      R_ss_x=[R_ss[0], R_ss[0]], S_ss_x=[0, self.S]) #x parallel
        self.data_S_R_point.data = dict(S_ss=S0, R_ss=R_ss)#dot
    
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
