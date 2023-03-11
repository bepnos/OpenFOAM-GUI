from flask import Flask, request, render_template, make_response
from datetime import datetime
import random
import requests

app = Flask(__name__)
internal_port = "3333"

BEPERKWACHTRIJ = False
PRINT_LOGS = False


class Parameter:
    """deze klasse stelt een parameter voor die kan aangepast worden in een openFOAM case.
    deze wordt gebruikt om de webinterface op te bouwen"""
    def __init__(self, naam, min_waarde, max_waarde, waarde=0.0, eenheid="m",stap=0.01, type="standaard", default=None, keuzes=("geen resultaten", "....")):
        self.naam = naam  # hoe heet deze parameter
        self.min_waarde = min_waarde  # wat kan deze parameter minimaal zijn
        self.max_waarde = max_waarde  # wat kan deze parameter maximaal zijn
        self.laatste_waarde = waarde  # wat is de laatste bekende waarde voor deze parammeter (of de startwaaarde)
        self.eenheid = eenheid # eenheid van de parameter
        self.stap = stap  # stapgrote waarme de parameter kan worden ingegeven
        if default is None: # startwaarde van de parameter
            default = waarde
        self.default = default
        self.keuzes = keuzes # indien dit een dropdown is wat zijn de keuzes
        self.type = type # welke type invoer is dit hiermee wordt bij het opbouwen van de webpagina rekening gehouden

    def __str__(self):
        return f"parameter {self.naam} die varieert tussen {self.min_waarde} en {self.max_waarde}"

    def __repr__(self):
        return f"Parameter({self.naam},{self.min_waarde},{self.max_waarde},begin={self.laatste_waarde})"

    def laatste_waarde_float(self):
        return float(self.laatste_waarde)

    def naam_geen_spatie(self):
        return self.naam.replace(" ", "_")

    def bereik(self):
        if self.type not in ['plaats', 'standaard']:
            return None
        goede_types = [int, float]
        if (type(self.min_waarde) in goede_types) and (type(self.max_waarde) in goede_types):
            return self.max_waarde - self.min_waarde
        else:
            return None

    def bereik_string(self):
        """wordt gebruikt om aan de eindgebruiker te tonen waartussen een parrameter mag varieren"""
        bereik = self.bereik()
        if bereik is not None:
            if bereik >= 0:
                if self.type == "plaats":
                    return f"(van {(-1)*self.min_waarde}{self.eenheid} naar links tot {self.max_waarde}{self.eenheid} naar rechts)"
                else:
                    return f"({self.min_waarde}{self.eenheid} tot {self.max_waarde}{self.eenheid})"
        return ""

    def get_default(self):
        return self.default


class Gebruiker:
    """deze classe stelt een gebruiker voor, en houdt hiervan de nodige data bij tussen reqests"""
    gebruikerslijst = []
    id_teller = 11000

    def __init__(self):
        self.id = str(Gebruiker.id_teller) + "-" + str(random.random())[2:]
        Gebruiker.id_teller += 1
        Gebruiker.gebruikerslijst.append(self)
        self.vraag_geschiedenis = []  # lijst tupels met case en wanneer deze werd opgevraagd

    def get_id(self):
        return self.id

    @staticmethod
    def get_gebruikerslijst():
        return Gebruiker.gebruikerslijst

    def is_gebruikers_id(self,id):
        return self.get_id() == id

    def __repr__(self):
        return f"gebruiker met id {self.get_id()} en geschiedenis {self.vraag_geschiedenis}"

    def __eq__(self, other):
        if type(other) == Gebruiker:
            if self.get_id() == other.get_id():
                return True
        return False

    def is_overactief(self):
        return True

    def wacht_tijd(self):
        """berekend hoe lang een gebruiker eventueel moet wachten voor deze opnieuw een berekening kan uitvoeren"""
        wact_tijd_teller = 0
        if not self.vraag_geschiedenis:
            return 0
        for i in range(1, len(self.vraag_geschiedenis)):
            case,tijdstip = self.vraag_geschiedenis[i]
            vorig_tijdstip = self.vraag_geschiedenis[i-1][1]
            verlopen_tijd = tijdstip - vorig_tijdstip
            verlopen_tijd_s = verlopen_tijd.total_seconds()
            wact_tijd_teller = max(wact_tijd_teller-verlopen_tijd_s, 0) # wachtijd loopt af
            if case == '/dambreuk':  # elke uitgevoerde case verhoogt de wachtijd
                if verlopen_tijd_s < 4:
                    wact_tijd_teller += 10 # vermijden dat 1 gebruiker snel na elkaar veel aanvragen doet
                elif verlopen_tijd_s < 10:
                    wact_tijd_teller += 5
                wact_tijd_teller += 10
            elif case == "/vuur":
                if verlopen_tijd_s < 4:
                    wact_tijd_teller += 20  # vermijden dat 1 gebruiker snel na elkaar veel aanvragen doet
                elif verlopen_tijd_s < 7:
                    wact_tijd_teller += 10
                wact_tijd_teller += 20
            else:
                wact_tijd_teller += 20
        wact_tijd_teller -= (datetime.now() - self.vraag_geschiedenis[-1][1]).total_seconds()
        wact_tijd_teller -= 32
        return max(round(wact_tijd_teller), 0)

    @staticmethod
    def gebruiker_uit_id(id):
        for bestaande_gebruiker in Gebruiker.gebruikerslijst:
            if bestaande_gebruiker.is_gebruikers_id(id):
                return bestaande_gebruiker
        return None


class Resultaat:
    """deze klasse geeft de informatie in verband met het resultaat van een op de server uitgevoerde berekening weer"""

    def __init__(self, video_locatie,wacht_tijd=None):
        self.video_locatie = video_locatie
        self.wacht_tijd = wacht_tijd

    def get_video_locatie(self):
        return self.video_locatie

    def __repr__(self):
        return f"resultaat met video locaie {self.video_locatie}"

    def moet_wachten(self):
        return self.video_locatie == "wacht"


class Info:
    """ Deze classe houdt de infourmatie bij die nodig is om de webpagina over een bepaalde
    openFOAM case weer te geven
    """
    def __init__(self, case_locatie, inleiding,titel=None, instructies=None, cases=None,witruimte_onderaan=15):
        if titel is None:
            self.titel = "EEN SIMULATIE IN DE CLOUD"
        if instructies is None:
            self.instructies = """ U kunt in deze simulatie parameters aanpassen door de glijdende invoerknoppen te verslepen. De huidige keuze wordt naast de invoer weergegeven. Druk op het kruisje om uw invoer ongedaan te maken.
                Druk onderaan op de knop "bereken" om de simulatie te starten. De berekeningen worden op een externe server uitgevoerd.
                Het kan even duren voor u de resultaten krijgt. Deze worden dan onderaan getoond."""
        if cases is None:
            self.cases = {"dambreuk": "/dambreuk", "vuur": "/vuur"}
        self.inleiding = inleiding
        self.huidige_case_locatie = case_locatie
        self.witruimte_onderaan = witruimte_onderaan

    def get_inleiding(self):
        return self.inleiding

    def is_caselijst(self):
        return len(self.cases) > 1


def case(parameters, configuratie, request, case_locatie):
    """" Maakt een webpagine die een openFOAM case/simulatie behandelt
    parametes: een lijst van Parameter objecten die de door de gebruiker in te stellen parameters voorstellen
    configuratie: een Info object met informatie over hoe de webinterface te configureren
    request: de requests die flask teruggeeft
    case-locatie: dit laat aan de API weten over welke case het betreft
    """
    # initialiseer case met parameters
    if (not request.cookies.get('gebruiker')) or Gebruiker.gebruiker_uit_id(request.cookies.get('gebruiker')) is None:
        nieuwe_gebruiker = Gebruiker()
        huidige_gebruiker = nieuwe_gebruiker
        nieuwe_coockie = True
        if PRINT_LOGS:
            print(f"nieuwe gebruiker geregistreerd: {huidige_gebruiker}")
    else:
        nieuwe_gebruiker = None
        huidige_gebruiker = Gebruiker.gebruiker_uit_id(request.cookies.get('gebruiker'))
        nieuwe_coockie = False

    if request.method == 'POST':
        result_from_post = []
        for param in parameters:
            invoer = request.form[param.naam]
            result_from_post.append(invoer)
            param.laatste_waarde = invoer
        if PRINT_LOGS:
            print(f"berekingen worden gevraagd door {huidige_gebruiker}; met waardes {result_from_post}")
        te_vragen_case = case_locatie

        wacht_tijd = huidige_gebruiker.wacht_tijd()
        if wacht_tijd > 0 and BEPERKWACHTRIJ:
            resultaat = Resultaat("wacht", wacht_tijd=wacht_tijd)
            if PRINT_LOGS:
                print(f'vraag van {huidige_gebruiker} geweigerd op basis van {huidige_gebruiker.vraag_geschiedenis}')
                print(f'de wachtijd bedraagt {wacht_tijd}')
        else:
            if BEPERKWACHTRIJ:
                huidige_gebruiker.vraag_geschiedenis.append((configuratie.huidige_case_locatie, datetime.now()))
            if PRINT_LOGS:
                print(f"berekeningen opvragen op de server ...... voor {huidige_gebruiker}")
            cmd = "\n".join([te_vragen_case, *result_from_post ])
            r = requests.request("POST", "https://pno3cwb1.student.cs.kuleuven.be", data=cmd, stream=True)
            if PRINT_LOGS:
                print(f"antwoord gekregen van de server voor {huidige_gebruiker}")
            output = r.content
            gebruiker_id = huidige_gebruiker.get_id()
            with open(f'static/images/output{gebruiker_id}.gif', "wb") as f:
                f.write(output)
            resultaat = Resultaat(f'images/output{gebruiker_id}.gif')
            print(Resultaat)
            if PRINT_LOGS:
                print(f"het resultaat van de berekeningen wordt opgelsagen in images/output{gebruiker_id}.gif")
        if PRINT_LOGS:
            print(f'resultaat {resultaat} wordt terugegeven')
        response = make_response(render_template('case.html', params=parameters, resultaat=resultaat, cookies=nieuwe_coockie, info=configuratie))
        if nieuwe_gebruiker is not None:
            response.set_cookie('gebruiker', value=nieuwe_gebruiker.get_id(), max_age=None)
        return response

    elif request.method == 'GET':
        response = make_response(render_template('case.html', params=parameters, resultaat=None, cookies=nieuwe_coockie, info=configuratie))
        if nieuwe_gebruiker is not None:
            response.set_cookie('gebruiker', value=nieuwe_gebruiker.get_id(), max_age=None)
        if PRINT_LOGS:
            print(f'gebruiker {huidige_gebruiker} heeft de website bezocht')
        return response

@app.route("/dambreuk", methods=['POST', 'GET'])
@app.route("/", methods=['POST', 'GET'])
def index():
    parameters = [Parameter("Hoogte water", 0.1, 4.0, waarde=2.0),
                  Parameter("Breedte water", 0.1, 4.0, waarde=0.5),
                  Parameter("Breedte dijk", 0.1, 1.9, waarde=0.32),
                  Parameter("Hoogte dijk", 0.1, 3.5, waarde=0.64),
                  Parameter("Verschuiving dijk", -1.0, 1.0, waarde=0.0, type="plaats"),
                  Parameter("Duur simulatie", 1, 5, waarde=5, eenheid="s", stap=1)]
    inleiding = """Welkom op onze website ! Hier kunt u simulaties laten uitvoeren met het programma openFOAM. 
    De simulatie die u hieronder kunt laten uitvoeren gaat over een dam die breekt. 
    Nadat de dam is gebroken komt een groote watermassa af op een dijk. Houdt deze stand ?  """
    configuratie = Info("/dambreuk", inleiding)
    case_locatie = "/opt/openfoam8/tutorials/multiphase/interFoam/laminar/damBreak/damBreak"
    return case(parameters, configuratie, request, case_locatie)


@app.route("/vuur", methods=['POST', 'GET'])
def pool_fire():
    parameters = [Parameter("Duur simulatie", 1, 5, waarde=5, eenheid="s", stap=1),
                  Parameter("Weer te geven informatie", 0, 0, type="keuze", keuzes=("T", "CH4", "N2", "O2", "H2O","CO2"), default=0, eenheid="")
                  ]
    inleiding = """ Hier kunt u een brand simuleren. U kunt zelf kiezen welke resultaten van de simulatie u te zien krijgt.
     Kies T om de temperatuur te bekijken. U kunt ook de concentratie van de aanwezige stoffen raadplegen.
     Kies CH4 voor methaan, N2 voor stikstof, O2 voor zuurstof, H2O voor waterdamp en CO2 voor koolstofdioxide."""
    configuratie = Info("/vuur", inleiding)
    case_locatie = "/opt/openfoam8/tutorials/combustion/fireFoam/LES/smallPoolFire2D"
    return case(parameters, configuratie, request, case_locatie)


@app.route("/over-dit-project")
def over_dit_project():
    configuratie = Info(None,None)
    response = make_response(render_template('about.html', info=configuratie))

    return response


if __name__ == '__main__':
    app.run('0.0.0.0', int(internal_port))

