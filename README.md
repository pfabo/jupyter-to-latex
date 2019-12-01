# jupyter-to-latex
Simple python script for jupyter-notebook to latex conversion.

Convert Jupyter (with LaTeX_envs extension) notebook simple or multiple files to LaTex document. 
Adds some improvements to conversion process. Need Python >= 3.6.

1. Download and unpack source files, set path. 

2. In your export directory run *python jp2tex.py -c*

This create config files and tex files from templates (title page etc.) 

3. Edit *config.py*

Enter path to notebook files and list of chapters.

4. Run *python jp2tex.py*

This generate tex file for every chapter, compile *main.tex* with LaTex.
