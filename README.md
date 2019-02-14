# jupyter-to-latex
Simple python script for jupyter-notebook to latex conversion.

Convert Jupyter (with LaTeX_envs extension) notebook simple or multiple files to LaTex document. 
Adds some improvements to conversion process.
Conversion process is controlled with conv_config.py file.

## Conversion consist from following steps:

#### Copying original notebook file *.ipynb to temporary destination
   - creating directory with notebook name

#### Conversion of html image include to latex commands 

At this time is not possible to define image  dimension in conversion from Jupyter to Latex. 
With script image import with html command (alt and scale parameters are ignored in Jupyter)

    <img src="image.png" width=400px alt="Image text" scale="0.5">
    
is replaced in *.ipynb file with latex commands
    
    \begin{figure}
    \centerline{\includegraphics[scale=0.5]{image.png}}
    \caption{Image text}
    \end{figure}
   
#### Running standard Jupyter to Latex conversion with command

  jupyter nbconvert --to latex_with_lenvs 
  
#### Remove and update some terms im LaTeX file - see source code
