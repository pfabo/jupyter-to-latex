#coding:utf8

title_page_template = r'''
% teplate pre titulnu stranu dokumentu
% komponenty strany sy usporiadane v tabulke s centrovanymi riadkami

\title{
\begin{tabular}{c}
Uvodny nadpis\\
\\
\hline
Hlavny nadpis \\
\hline
\\
Spodny nadpis 
\\
\\
% logo - ak je pouzite
% \raisebox{-.25\height}{\includegraphics[width=6.0cm]{vc_logo_en.png}}  \\
\end{tabular}
}

% zoznam autorov
\author{Janko Hrasko}

% vytvorenia strany 
\maketitle 
'''
