#!/usr/bin/python
'''
date    27.12.2018
ver     1.1
subs    Jupyter 4.4.0, ext. latex_envs
        Python 3.6.7
        LaTex 
        
history
1.0     vytvorenie dokumentu
1.1     doplnenie exportu <img ..>

Konverzia Jupyter notebookov na LaTex dokument
==============================================

Skript konvertuje notebooku umiestnene v spolocnom adresari na *.tex
dokumenty v samostatnych adresaroch. 


 
Postup konverzie
1. subor *.ipynb su skopirovane do samostatnych adresarov

2. v *.ipynb su expandovane vybrane HTML tagy a komentare
   <!---
   text napr. LaTex commands
   -->
3. subory *.ipynb su konvertovane na LaTex subory pomocou latex_nvs 

4. uprava *.tex suborov
   - odstranenie zahlavia
   - doplnenie inkludovania main.tex suboru s formatovanim textu
   - odstranenie zbytocnych komentarov
   - doplnenie explicitneho umiestnenia obrazkov
   
5. expanzia LaTex kodu generovaneho prikazom display(lx(..))
   umiestneneho v postupnosti prikazov
   \begin{verbatim}
   $ latex kod $
   \end{verbatim}
'''

import re
import os
from shutil import copyfile

from conv_config import *

def filter_jpn_img(s):
    '''
    Filter pre upravu formatovania obrazkov v subore *.ipynb
    
    Funkcia prehlada subor *.ipynb (v tvare retazca) a HTML tag pre
    vlozenie obrazku (atributy nie su oddelene ciarkou)
    
    <img src="obrazok.png" width=400px alt="Text pod obrazkom" scale="0.5">
    
    nahradi retazcom
    
    \begin{figure}
    \centerline{\includegraphics[scale=0.5]{obrazok.png}}
    \caption{Text pod obrazkom}
    \end{figure}
    
    param   s - vstupny subor v tvare retazca
    return  s - filtrovany retazec
    '''
    cmd = re.compile(r'<img src=\\"(?P<img>[\.\w/]*)\\"[,\s]*' + 
                     r'(?:width=(?P<width>[\d]*))?[px,\s]*'+ 
                     r'(?:alt=\\"(?P<alt>[\+\- \.\w]*)\\")?[,\s]*' +  
                     r'(?:scale=\\"(?P<scale>[\w\.]*))?' +  
                     r'(.)*>')

    offs = 0
    
    while True:
        data = cmd.search(s, offs)      # prehladanie s posunom
        if data is None:
            break

        (offs,k) = data.span() 
        print('[JPN Convert ] Image ', data['img'] )

        repl=r'\\begin{figure}' + \
             r'\\centerline{\\includegraphics[scale=' + \
             (data['scale'] if data['scale'] is not None else '1.0') + r']' + \
             r'{' + data['img'] +'}}' + \
             r'\\caption{' + \
             (data['alt'] if data['alt'] is not None else '----') +'}' + \
             r'\\end{figure}' 
        s = s.replace(data[0], repl)
    return s
    
def filter_jpn_comment(s):
    '''
    Filter neviditelnych komentarov v subore notebooku 
    
    Funkcia prehlada subor *.ipynb v tvare retazca a nahradi postupnost
    <!---  text -->  obsahom komentara
    
    param   s - vstupny subor v tvare retazca
    return  s - filtrovany subor
    '''
    return s
    

def filter_tex_verbatim(s):
    '''
    Filter vyrazov \begin{verbatim} $ latex kod $ \end{verbatim}
    
    Funcia sekvencne prehlada *.tex subor v tvare retazca a nahradi text 
    vyrazu textovou postupnostou
    \begin{equation} latex kod \end{equation}
    
    param   s - vstupny subor v tvare retazca
    return  s - filtrovany subor  
    '''
    cmd = re.compile(r"\\begin\{verbatim\}\s*'\$(.*)\$'\s*\\end\{verbatim\}") #, s)
    offs = 10 
    while True:
        equ = cmd.search(s, offs)      # prehladanie s posunom
        if equ is None:
            break

        (offs,k) = equ.span()        
        e = equ[1]
        e = e.replace(r'\\', "\\")     # uprava formatu
        repl=r'\begin{equation*}' +'\n' + \
             e + '\n' +\
             '\end{equation*}' + '\n'
        s = s.replace(equ[0], repl)
        #s = re.sub(equ[0], repl, s)
    return s
    
    
def filter_tex_label(s, s_type):
    '''
    Filter vyrazov \label v \section
    
    Funcia sekvencne prehlada *.tex subor v tvare retazca a odstrani
    \label za nazvom kapitoly
    
    param   s - vstupny subor v tvare retazca
    param   s_type - oznacenie filtrovaneho vyrazu (section, subsection ...)
    return  s - filtrovany subor  
    '''
    cmd = re.compile(r"(\\" + s_type + r"\{[\w\s]*\})\\label\{([-.\w\s]*)\}") #, s)
    offs = 10 
    while True:
        equ = cmd.search(s, offs)      # prehladanie s posunom
        if equ is None:
            break

        (offs,k) = equ.span()        
        s = s.replace(equ[0], equ[1])
    return s


#-----------------------------------------------------------------------
# 1. Vytvorenie adresarov pre kazdy notebook a ich skopirovanie
#-----------------------------------------------------------------------
for [f, cp, upd] in config:
    if not os.path.exists(dest + f):
        os.makedirs(dest + f)

    if cp is True:
        # kopia originalu
        print('[JPN Convert ] Copy notebook ' + f + '.ipynb')
        copyfile(source + f + '.ipynb', dest + f +'/' +  f + '.ipynb')
    
    if upd is True:
        # doplnenie cesty k lokalnej kopii kniznic pre konverziu
        # update notebooku s nastavenim lokalnych kniznic utilit (EXPORT ...)
        # zmazanie povodneho notebooku, premenovanie po update
        print('[JPN Convert ] Execute notebook ' + f + '.ipynb')
        os.environ["PYTHONPATH"] += os.pathsep + dest +'..'
        os.system('jupyter nbconvert --to notebook --execute '+ dest + f +'/' +  f + '.ipynb') 
        os.remove(dest + f +'/' +  f + '.ipynb') 
        os.rename(dest + f +'/' +  f + '.nbconvert' + '.ipynb', dest + f +'/' +  f + '.ipynb') 
        print()

#-----------------------------------------------------------------------
# 3.  Konverzia Jupyter -> LaTex
#-----------------------------------------------------------------------

for [f, cp, upd] in config:
    if cp is True:
        # uprava notebookov pred konverziou
        print('[JPN Convert ] Update notebook ' + f  + '.ipynb')
        name = dest + f +'/' + f  + '.ipynb'
        fp = open(name, 'r')
        s=fp.read()
        fp.close()
        
        s=filter_jpn_img(s)
        
        fp = open(name, 'w')
        fp.write(s)
        fp.close()
        
        print('[JPN Convert ] Convert notebook to LaTex ')
        s = 'jupyter nbconvert --to latex_with_lenvs ' 
        os.system(s + dest + f +'/' + f  + '.ipynb')
        print()
    
  
#-----------------------------------------------------------------------
# 4. Uprava *tex zdrojovych suborov
#    Doplnenie a uprava dokumentov pre ich zoradenie v LaTexu
#-----------------------------------------------------------------------
for [f, cp, upd] in config:
    if cp is True:
        # otvorenie suboru
        name = dest + f +'/' + f + '.tex'
        fp = open(name, 'r')
        print('[LTX Convert ] File', name )
        s=fp.read()
        fp.close()

        # vytrepanie somarin v zahlavi
        q = s.find(r'\begin{document}')
        s = (s[q:])

        # vytrepanie somarin a nepodporovanych prikazovzo zdrojoveho textu 
        s = s.replace(r'\maketitle', '')
        s = s.replace(r'\tableofcontents', '')
        s = s.replace('% Add a bibliography block to the postdoc', '')
        s = s.replace(r'%\bibliographystyle{ieetran}', '')
        s = s.replace(r'%\bibliography{Thesis}', '')
        s = s.replace('    \n', '')
        s = s.replace(r'\tightlist','')
        
        # explicitne umiestnenie obrazkov na poziciu [h!]
        s = s.replace(r'\begin{figure}', r'\begin{figure}[h!]')
    
        # 5. Filter na expanziu LaTex vyrazov
        s = filter_tex_verbatim(s)
        s = filter_tex_label(s, 'section')
        s = filter_tex_label(s, 'subsection')
        s = filter_tex_label(s, 'subsubsection')
        
        s = s.replace(r'\section', r'\chapter')
        s = s.replace(r'\subsection', r'\section')
        s = s.replace(r'\subsubsection', r'\subsection')

        # ulozenie konvertovaneho zdrojaku
        z=r'\documentclass[../main.tex]{subfiles}' + '\n'
        s = z + s
        fp = open(name, 'w')
        fp.write(s)
        fp.close()


