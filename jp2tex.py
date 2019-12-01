#!/usr/bin/python
'''
date    27.12.2018
ver     1.1
subs    Jupyter 4.4.0, ext. latex_envs
        Python 3.6.7
        LaTex 
        NumPy
        Scipy
        SymPy
        Pandoc
        
history
1.0     vytvorenie dokumentu
1.1     doplnenie exportu <img ..>
        doplnenie specialneho formatovania vystupu sympy
1.2     implementacia <!-- REMOVE-->
        impleementacia vertikalneho formatovania <!-- SMALLSKIP --> ...
1.3     upravy ciest a formatovanie vystupu 

Konverzia Jupyter notebookov na LaTex dokument
==============================================

Skript konvertuje notebooku umiestnene v spolocnom adresari na *.tex
dokumenty v samostatnych adresaroch. 

Specialne znaky a doplnky v suboroch notebooku
1. Novy odstavec
   funguje dvojite lomitko na konci textu\\
   
2. Odstranenie riadku pred konverziou
<!-- REMOVE-->
toto je text riadku, ktory bude odstraneny po znak konca riadku

3. Vertikalne formatovanie
<!-- SMALLSKIP -->
<!-- MEDSKIP -->
<!-- BIGSKIP -->
<!-- NEWPAGE -->
<!-- BR -->

------------------------------------------------------------------------
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
   
==============================================
TODO
1. Kontrola existencie notebookov z konfiguracie

'''

import re
import os
import sys

from shutil import copyfile

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
                     r'(?:alt=\\"(?P<alt>[!\+\- \.\w]*)\\")?[,\s]*' +  
                     r'(?:scale=\\"(?P<scale>[\w\.]*))?' +  
                     r'(.)*>')

    offs = 0
    
    while True:
        data = cmd.search(s, offs)      # prehladanie s posunom
        if data is None:
            break

        (offs,k) = data.span() 
        #print(data['scale'])
        
        #exit()
        print('Konverzia obrazku ', data['img'] )

        repl=r'\\begin{figure}' + \
             r'\\centerline{\\includegraphics[scale=' + \
             (data['scale'] if data['scale'] is not None else '1.0') + r']' + \
             r'{' + data['img'] +'}}' + \
             r'\\caption{' + \
             (data['alt'] if data['alt'] is not None else '----') +'}' + \
             r'\\end{figure}' 
        s = s.replace(data[0], repl)
    return s
    
def filter_jpn_vertical(s):
    '''
    Filter neviditelnych komentarov v subore notebooku Jupyter-Notebookov
    
    Uprava vertikalneho formatovania textu.
    Funkcia prehlada subor *.ipynb v tvare retazca a nahradi postupnost
    <!---  format -->  makrom z LaTexu
    
    param   s - vstupny subor v tvare retazca
    return  s - filtrovany subor
    '''
    s = s.replace(r'<!-- SMALLSKIP -->', r'\\smallskip')
    s = s.replace(r'<!-- MEDSKIP -->', r'\\medskip')
    s = s.replace(r'<!-- BIGSKIP -->', r'\\bigskip')
    s = s.replace(r'<!-- NEWPAGE -->', r'\\newpage')
    #s = s.replace(r'<!-- BR06 -->',  r'\\\\[6pt]')  # nefunguje
    #s = s.replace(r'<!-- BR12 -->',  r'\\\\[12pt]') # nefunguje
    s = s.replace(r'<!-- BR -->',  r'\\\\')

    return s
    
def filter_jpn_remove(s):
    '''
    Filter neviditelnych komentarov v subore notebooku 
    
    Funkcia prehlada subor *.ipynb v tvare retazca 
    <!-- REMOVE -->  
    a vymaze zo suboru notebooku nasledujuci riadok (po \n)
    
    param   s - vstupny subor v tvare retazca
    return  s - filtrovany subor
    '''

    # vyhladanie riadku s REMOVE a nasledujuceho riadku
    cmd1 = re.compile(r"\"<![-\s]*REMOVE[-\s]*>\s*\\n\",\s*(.*)[\\n?\"]*")  
    
    cmd2 = re.compile(r'\"\\n\",')
    offs = 0 
    while True:
        #offs = 0
        equ = cmd1.search(s, offs)      # prehladanie s posunom
        
        if equ is None:
            break
            
        (offs, k) = equ.span()
        #print(equ[0], offs, k)
        #(offs, k) = equ.span()          # zacaitok a koniec hladania   
        #offs = k   
        s = s.replace(equ[0], ' ', 1)  
        #
        newl = cmd2.search(s, offs)
        if newl is not None:
            #print('found', equ.span())
            (offs, k) = equ.span()
            print(type(offs))
            s1 = s[:offs]
            s2 = s[offs:]
            s = s1 + s2.replace(newl[0], '', 1)
              
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
    Filter vyrazov \label v \sectionJupyter-Notebookov
    
    Funcia sekvencne prehlada *.tex subor v tvare retazca a odstrani
    \label za nazvom kapitoly
    
    param   s - vstupny subor v tvare retazca
    param   s_type - oznacenie filtrovaneho vyrazu (section, subsection ...)
    return  s - filtrovany subor  
    '''
    cmd = re.compile(r"(\\" + s_type + r"\{[-.\w\s,-:]*\})\\label\{([-.\w\s]*)\}") #, s)
    offs = 10 
    while True:
        equ = cmd.search(s, offs)      # prehladanie s posunom
        if equ is None:
            break

        (offs, _) = equ.span()         # zaciatok a koniec najdeneho retazca
        s = s.replace(equ[0], equ[1])
    return s


def create_config_convert(name='config.py'):
    '''
    Vytvorenie noveho konfiguracneho suboru z template_config_file 
    '''
    import template_config as tp
    
    s = tp.config_template
    
    if os.path.exists('./'+name):
        q = input('Subor ' + name + ' existuje, prepisat ? [y/n] ')
        if q!='Y' and q !='y':
            return
            
    fp = open(name,'w')
    fp.write(s)
    fp.close()
    return
    
    
def create_config():
    '''
    Vytvorenie noveho konfiguracneho suboru z template_config_file 
    '''
    def create_file(name, s):
        '''
        Vygenerovanie suboru z template
        '''
        if os.path.exists('./'+name):
            q = input('[Config       ] Subor ' + name + ' existuje, prepisat ? [y/n] ')
            if q=='Y' or q =='y':
                fp = open(name,'w')
                fp.write(s)
                fp.close()
        else:
            fp = open(name,'w')
            fp.write(s)
            fp.close()
        return
        
    import template_config as tc
    create_file('config.py', tc.config_template)
        
    # listing.tex template
    import template_listing as tp    
    create_file('listing.tex', tp.listing_template)
    
    import template_main as tm
    create_file('main.tex', tm.main_tex_template)
    
    import template_title_page as tt
    create_file('title_page.tex', tt.title_page_template)
    
    create_file('chapters_path.tex', '% chapters path \n')
    create_file('graphics_path.tex', '% chapters path \n')

#-----------------------------------------------------------------------

import argparse


if __name__== "__main__":
        
    # Kontrola argumentov
    parser = argparse.ArgumentParser(description='Konverzia Jupyter notebookov na suubory LaTex-u')
    parser.add_argument('--c', '-config',  action='store_true', help='Vygeneruje konfiguracne subory')

    args = parser.parse_args()
    
    local_path = os.getcwd() + '/' 
    # vytvorenie prazdneho konfiguracneho suboru
    if args.c == True:
        # podla template vytvori subory
        # config.py, main.tex, listing.tex, title_page.tex, chapters_pat.tex, graphics_path.text
        create_config()
        exit()
        
    
    if os.path.exists(local_path + 'config.py'):
        sys.path.insert(1, local_path)
        import config
        
        if config.source[-1] != '/':
            config.source += '/'
        
        config.source = os.getenv("HOME") + '/' + config.source
        config.dest   = './convert/'
    else:
        print('Konfiguracne subory nie su vytvorene, spusti:')
        print('jp2tex.py -c')    
        exit()
    
    
    #-----------------------------------------------------------------------
    # 1. Vytvorenie adresarov pre kazdy notebook a ich skopirovanie
    #-----------------------------------------------------------------------
    
    # skopirovanie adresaru s obrazkami
    print('Kopirujem obrazky do ./img')
    if os.path.exists(config.source + 'img/'):
        if not os.path.exists(local_path + 'img/'):
            os.makedirs(local_path + 'img/')
        
        # kopirovanie suborov     
        for item in os.listdir(config.source + 'img/'):
            if os.path.isfile(config.source + 'img/' + item):
                copyfile(config.source + 'img/' + item, local_path + 'img/' + item)

                
    # skopirovanie pomocnych programov
    print('Kopirujem zdrojove texty do ./src')
    if os.path.exists(config.source + 'src/'):
        if not os.path.exists(local_path + 'src/'):
            os.makedirs(local_path + 'src/')
        
        # kopirovanie suborov     
        for item in os.listdir(config.source + 'src/'):
            if os.path.isfile(item):
                copyfile(config.source + 'src/' + item, local_path + 'src/' + item)

    
    if not os.path.exists(local_path + config.dest):
        print('Vytvorenie adresara' + config.dest)
        os.makedirs(local_path + config.dest)
    
    ch_path = open('chapters_path.tex', 'w')   # vygenerovanie suboru s cestami k notebookom 
    ch_path.write(r'% generovany subor - needitovat' + '\n\n')
    
    img_path = open('graphics_path.tex', 'w')   # vygenerovanie suboru s cestami k notebookom 
    img_path.write(r'% generovany subor - needitovat' + '\n\n')
    img_path.write(r'\graphicspath { {./img/}, ' + '\n')
    
    for [ntb, cp, upd] in config.chapters:
        #print(local_path + config.dest + ntb)
        if not os.path.exists(local_path + config.dest + ntb):
            os.makedirs(local_path + config.dest + ntb)
            
        # kontrola existencie notebooku
        if not os.path.exists(config.source + ntb + '.ipynb'):
            print('Chyba: Zdrojovy notebook neexistuje\n             ', config.source + ntb + '.ipynb')
            exit()

        if cp is True:
            # kopia originalu notebooku do lokalneh Jupyter-Notebookovo adresaru s menom notebooku
            print('Kopirujem notebook ' + ntb + '.ipynb')
            copyfile(config.source + ntb + '.ipynb', local_path + config.dest + ntb +'/' +  ntb + '.ipynb')
            
            ch_path.write(r'\newpage' + ' \n')
            ch_path.write(r'\subfile{' + config.dest + ntb + '/' + ntb + '}\n\n')
            
            img_path.write('{' + config.dest + ntb + '/},\n')
    
    img_path.write('}\n')
    img_path.close()
    ch_path.close()
    
    os.environ["PYTHONPATH"] += os.pathsep + local_path 

    for [ntb, cp, upd] in config.chapters:
        if upd is True:
            # doplnenie cesty k lokalnej kopii kniznic pre konverziu
            # update notebooku s nastavenim lokalnych kniznic utilit (EXPORT ...)
            # vysledkom konverzie je notebook name.nbconvert.ipynb
            # zmazanie povodneho notebooku
            # premenovanie po update na povodne meno bez .nbconvert
            try:
                print('Spustenie notebooku ' + ntb + '.ipynb')
                
                # spustenie s chybovymi hlaseniami
                #os.system('jupyter nbconvert --to notebook --execute '+ local_path + config.dest + ntb +'/' +  ntb + '.ipynb' + 
                #          ' --TemplateExporter.exclude_markdown=False' ) 
                
                # spustenie bez hlaseni nbconvert
                os.system('jupyter nbconvert --to notebook --execute '+ local_path + config.dest + ntb +'/' +  ntb + '.ipynb' + 
                          " --Application.log_level='CRITICAL'"  + ' --TemplateExporter.exclude_markdown=False' ) 
                
                os.remove(local_path + config.dest + ntb +'/' +  ntb + '.ipynb') 
                os.rename(local_path + config.dest + ntb +'/' +  ntb+ '.nbconvert' + '.ipynb', local_path + config.dest + ntb +'/' +  ntb + '.ipynb') 
            except:
                print('Chyba pri vykonavani notebooku ', ntb)   
                print('Pravdepodobne chyba v pythonovskom skripte v notebooku, otestuj originalny notebook')  
                exit()

    #-----------------------------------------------------------------------
    # 2. Konverzia Jupyter -> LaTex
    #-----------------------------------------------------------------------

    for [ntb, cp, upd] in config.chapters:
        if cp is True:
            # 2.1 Uprava notebookov pred konverziou
            # nacitanie celeho notebooku do textoveho retazca
            print('Filtracia notebooku ' + ntb  + '.ipynb')
            name = local_path + config.dest + ntb +'/' + ntb  + '.ipynb'
            fp = open(name, 'r')
            s=fp.read()
            fp.close()
                                        # filtracia suboru notebooku
            s=filter_jpn_remove(s)      # spracovanie <!-- REMOVE -->
            s=filter_jpn_img(s)         # uprava formatovania obrazkov
            s=filter_jpn_vertical(s)    # uprava vertikalneho formatovania
           
            fp = open(name, 'w')        # zapis filtrovaneho notebooku
            fp.write(s)
            fp.close()
            
            # 2.2 Konverzia notebooku do LaTex-u s pomocou latex_lenvs
            #print()
            #print('Konverzia do LaTex-u ')
            cmd = 'jupyter nbconvert --to latex_with_lenvs ' 
            os.system(cmd + local_path + config.dest + ntb +'/' + ntb  + '.ipynb' + ' --Application.log_level=0')
            #print()
        

    #-----------------------------------------------------------------------
    # 4. Uprava *tex zdrojovych suborov
    #    Doplnenie a uprava dokumentov pre ich zoradenie v LaTexu
    #-----------------------------------------------------------------------
    for [ntb, cp, upd] in config.chapters:
        if cp is True:
            # otvorenie suboru
            name = local_path + config.dest + ntb +'/' + ntb + '.tex'
            fp = open(name, 'r')
            print('Konverzia ' +  ntb +'.tex')
            s=fp.read()
            fp.close()

            # vytrepanie somarin v zahlavi
            q = s.find(r'\begin{document}')  # vyhladanie zaciatku aktivneho dokumentu
            s = (s[q:])                      # odfaklenia zahlavia

            # vytrepanie somarin a nepodporovanych prikazov zo zdrojoveho textu 
            s = s.replace(r'\maketitle', '')
            s = s.replace(r'\tableofcontents', '')
            s = s.replace('% Add a bibliography block to the postdoc', '')
            s = s.replace(r'%\bibliographystyle{ieetran}', '')
            s = s.replace(r'%\bibliography{Thesis}', '')
            s = s.replace('    \Jupyter-Notebookovn', '')
            s = s.replace(r'\tightlist','')
            
            # explicitne umiestnenie obrazkov na poziciu [h!]
            s = s.replace(r'\begin{figure}', r'\begin{figure}[h!]')
            # uprava default rozmeru generovanych obrazkov z matplotlib-u
            s = s.replace(r'\adjustimage{max size={0.7\linewidth}{0.3\paperheight}}', 
                          r'\adjustimage{max size={0.5\linewidth}}')
        
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


