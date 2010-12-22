#!/usr/bin/env python
# -*- coding: latin-1 -*-

# GNU GENERAL PUBLIC LICENSE
# UI interfrace support for WinFile ( http://code.google.com/p/winfiles60/ ) - A powerful filemanager for the Symbian OS
# Copyright   2008-2011 memoryN70 ( memoryS60@gmail.com )
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

Here to come:

ui class
menu class
user popups class
progress diag class
listbox class


'''



class TouchDriver:
'''

vediamo di scrivere qualche idea...

Cosa deve fare la classe? 
- gestire il touch su una determinata area ben definita (rect) (non semplicemente un tocco ovviamente, per quello ui.bind_touch)
- e...qui dipende dall'uso che se ne vuole fare ovvero (casi...):

1) All'interno dell'area bisogna sapere se l'utente preme con un tocco semplice, oppure se effettua uno scroll (e quindi definire la sua direzione)
    Utilizzi-esempi: scrolling immagini (su-giu: zoom; destra-sinistra: cambio immagine), scrolling canzoni, volume...
2) All'interno dell'area ci sono elementi (icone, liste,...) e ogni elemento ha una ben definita grandezza. L'utente può selezionare un elemento e, se la lista è lunga, può effettuare
lo scrolling in varie direzioni ben definite.
    Utilizzi: menu, listbox e altro

3) 

Essa deve avere:

- magari può ricorrrere a ui.bind_touch per la gestione del touch (in particolare per il callback di una specifica area; la funzione di callback riceve la coordinata dello stilo)
- funzione di controllo input touch (e prime considerazioni come direzione e tipo)
- funzione di callback che deve dare dati ben ordinati in uscita
- deve poter essere usata anche con più istanze contemporanee (beh non è un problema :))
- deve comunque essere più leggera e ottimizzata possibile
- non deve essere legata ad immagini o canvas

'''
    def __init__(s):
    
    