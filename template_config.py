config_template='''
#-----------------------------------------------------------------------
# Konfiguracia skriptu
#-----------------------------------------------------------------------
# Definicia ciest 
#  source - cesta k zdrojovym notebookom 
#  chapters - zoznam kapitol dokumentu
#
# zoznam notebookov pre konverziu
# format zaznamu
# [ notebook, convert, update ]
#    notenbook - meno notebooku bez pripony, 
#                bude pouzite ako adresar, do ktoreho sa skopiruje subor 
#                notebooku a do ktoreho sa budu zapisovat generovane subory
#
#    convert   - True/False preskocenie kopirovania a konverzie 
#                setrenie casu pri suboroch, ktore sa nemenili
#
#    update    - True/False spustenie update notebooku pred konverziou
#                update nema vyznam pre subory bez interaktivnej casti
#

source = 'path_to_notebooks'

chapters = [ 
            ['notebook_name',          True,  True],
          ]
          
'''
