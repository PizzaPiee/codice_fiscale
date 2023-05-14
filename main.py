import PySimpleGUI as sg
import re 

COMUNI = {}
MESI = {}
CA_PARI = {}
CA_DISPARI = {}
CA_RESTO = {}
CONSONANTS = "bcdfghjklmnpqrstvwxyz".upper()
MESI_LAYOUT = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']

sg.theme('SandyBeach')  
layout = [  [sg.Text('Cognome'), sg.InputText(size=10, key="cognome")],
            [sg.Text('Nome'), sg.InputText(size=10, key="nome")],
            [sg.Text("Sesso"), sg.Radio("Maschio", "sesso", key="maschio", default=True), sg.Radio("Femmina", "sesso", key="femmina"),],
            [sg.Text("Data"), sg.InputText(size=2, key="giorno"), sg.Combo(MESI_LAYOUT, default_value="Gennaio", key="mese"), sg.InputText(size=4, key="anno")],
            [sg.Text("Comune"), sg.InputText(size=10, key="comune")],
            [sg.Button(button_text="Genera codice fiscale", key="submit")],
            [sg.Text(text="", key="result")]]

def generaCodiceFiscale(cognome: str, nome: str, giorno: int, anno: int, mese: str, sesso: str, comune: str):
    res = ""

    # COGNOME: 3 LETTERE
    # carica 3 consonanti nella lista 'temp'
    temp = []
    for c in cognome.upper():
        if c in CONSONANTS and len(temp) < 3:
            temp.append(c)
    # se le consonanti non bastano carica le vocali
    if len(temp) < 3:
        for c in cognome.upper():
            if c not in CONSONANTS and len(temp) < 3:
                temp.append(c)
    # se le consonanti e le vocali non bastano completa aggiungendo delle X
    while len(temp) < 3:
        temp.append("X")

    res += ''.join(temp) # add values to the end result
    temp = [] # clear list for next use

    # NOME: 3 LETTERE
    nomeConsonanti = list(filter(lambda c: c if c in CONSONANTS else None, [c for c in nome.upper()]))
    # se il nome ha 4 consonanti prendi e salva la prima, terza e quarta
    if len(nomeConsonanti) >= 4:
        temp.append(nomeConsonanti[0])
        temp.append(nomeConsonanti[2])
        temp.append(nomeConsonanti[3])
    # se non ha 4 consonanti carica le prime 3
    else:
        for c in nomeConsonanti:
            if len(temp) < 3:
                temp.append(c)
        # se le prime 3 non bastano prendi le vocali
        for c in list(filter(lambda c: c if c not in CONSONANTS else None, [c for c in nome.upper()])):
            if len(temp) < 3:
                temp.append(c)
        # se le consonanti e le vocali non bastano completa aggiungendo delle X
        while len(temp) < 3:
            temp.append("X")
            
    res += ''.join(temp) # add values to the end result
    temp = [] # clear list for next use

    # ANNO E MESE DI NASCITA: 3 CARATTERI ALFANUMERICI
    temp.append(str(anno)[2:]) # inserisci le ultime due cifre dell'anno
    temp.append(MESI[mese.upper()])

    res += ''.join(temp) # add values to the end result
    temp = [] # clear list for next use

    # GIORNO DI NASCITA E SESSO: DUE CIFRE
    giorno = str(giorno) if giorno > 9 else "0" + str(giorno)
    giorno = giorno if sesso.upper() == "Maschio".upper() else str(int(giorno)+40)

    res += giorno # add values to the end result

    # COMUNE O STATO DI NASCITA: QUATTRO CARATTERI ALFANUMERICI
    res += COMUNI[comune.upper()]

    # CARATTERE DI CONTROLLO
    pari = []
    dispari = []
    res = re.sub(r"[\n\t\s]*", "", res)

    # controlla e inserisci i valori dei caratteri nelle liste corrispondenti
    for i in range(0, len(res)):
        if (i+1)%2==0:
            pari.append(int(CA_PARI[res[i]]))
        else:
            dispari.append(int(CA_DISPARI[res[i]]))
    
    res += CA_RESTO[str((sum(pari) + sum(dispari)) % 26)] # add values to the end result
    return res

def caricaDati():
    with open("./dati/comuni.txt") as f:
        for riga in f:
            comune, codice = riga.split(" -- ")
            COMUNI[comune] = codice
    
    with open("./dati/mesi.txt") as f:
        for riga in f:
            mese, codice = riga.split(" -- ")
            MESI[mese] = codice 

    with open("./dati/caratteri_alfanumerici/pari.txt") as f:
        for riga in f:
            carattere, valore = riga.split(" -- ")
            CA_PARI[carattere] = valore

    with open("./dati/caratteri_alfanumerici/dispari.txt") as f:
        for riga in f:
            carattere, valore = riga.split(" -- ")
            CA_DISPARI[carattere] = valore
            
    with open("./dati/caratteri_alfanumerici/resto.txt") as f:
        for riga in f:
            valore, carattere = riga.split(" -- ")
            CA_RESTO[valore] = carattere

caricaDati()

# Create the Window
window = sg.Window('Codice fiscale', layout, size=(250, 300))
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    if event == "submit":
        text = ""
        isValid = True
        for k in list(values.keys()):
            if type(values[k]) == bool:
                continue
            if values[k] == '':
                text += k + " non può essere vuoto\n"
                isValid = False
            
        for k in ["giorno", "anno"]:
            try:
                values[k] = int(values[k])
            except:
                text += k + " non è un numero\n"
                isValid = False

        sesso = "maschio" if values["maschio"] else "femmina"

        if isValid:
            text = generaCodiceFiscale(values["cognome"], values["nome"], values["giorno"], values["anno"], values["mese"], sesso, values["comune"])
        window.Element("result").update(text)


window.close()