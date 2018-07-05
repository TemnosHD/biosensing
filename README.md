# Network Motifs
### Presentation by Laura Martens & Arthur Heimbrecht

This is our presentation of 'Network Motifs' for Prof. Schwarz's Seminar 'Biophysics of Sensing, Signaling and Cell Fate Decisions' on June 23rd 2018. <br>
Please read this README if you want to run the presentation on your local device.

## How to run the presentation
The presentation uses `reveal.js` by Hakim El Hattab ([link](https://github.com/hakimel/reveal.js/) to git repo). <br>
Also we used [Bokeh](https://bokeh.pydata.org/en/latest/) to visualize the plots for differential equations and made them interactive.
Depending on which system you use, you maybe need to install [MAMP](https://www.mamp.info/de/) or [XAMPP](https://www.apachefriends.org/de/index.html) since reveal.js is based on a javascript framework.
So basically this presentation works similar to a website. <br>
At least on macOS this is not required and clicking on `presentation.html` opens the presentation.
Still for the  full 'experience' additional software is required.

## Bokeh
Bokeh is an interactive visualization library for python, that we used to generate our plots.
To install Bokeh we recommend [pip](https://pypi.org/project/pip/) or [conda](https://conda.io/docs/). <br>
The plots are generated in separate python files which are located in bokeh/diagramXY/ together with required images and the necessary file containing a plotter class.
This is necessary due to the way Bokeh works.
To run a plot simply  type `bokeh serve /path/to/diagramXY` into your console. <br>
This command can be combined for all plots: `$ bokeh serve diagram1a diagram1b diagram1c diagram1d diagram1e diagram1f diagram2b diagram2c`
Now you are good to go and can view the plots in the presentation.
If they do not show up please check the port Bokeh uses.

## Generate PDF
To generate a PDF of the presentation please install [decktape](https://github.com/astefanutti/decktape) using [npm](https://www.npmjs.com) and run `$ decktape presentation.html presentation.pdf --slides 1-46`.
