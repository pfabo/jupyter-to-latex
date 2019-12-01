#coding:utf8

main_tex_template = r'''
% Verzia 20.09.2019
% Template pre export Jupyter notebookov do LaTex-u
% 
\documentclass[10pt,a4paper]{report}      % rozmery papiera
\usepackage[utf8]{inputenc}               % kodovanie dokumentu
\usepackage[slovak]{babel}                % delenie slov
\usepackage[IL2]{fontenc}                 % lepsi kerning (ako pri T1)
\usepackage{amsmath}                      % matematicke vyrazy
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage[unicode]{hyperref}
\usepackage{wrapfig}
\usepackage{hyperref}
\usepackage{xcolor,colortbl}
\usepackage{array}
\usepackage{subfiles}
\usepackage{adjustbox}
\usepackage{fancyvrb}
\usepackage{url}

\usepackage{indentfirst}
\setlength{\parindent}{0cm}                % zrusene odsadenie pre paragrafy 

\fontfamily{ptm}\selectfont
\renewcommand{\familydefault}{ptm}         % zmena fontu dokumentu

\usepackage{listings}
\include{listing}                          % formatovanie zdrojovych kodov

\usepackage{geometry}
 \geometry{
 a4paper,
 total={160mm,247mm},
 left=25mm,
 top=25mm,
 }
 
\DeclareMathOperator{\arccosh}{arccosh}

% cesty k obrazkom
\include{graphics_path}       

% struktura dokumentu
\begin{document}

% titulna stranka
\include{title_page}

% obsah
\newpage
\tableofcontents

% kapitoly dokumentuy
\include{chapters_path}

\end{document}
'''
