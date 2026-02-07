from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog.models import Post, Category
from django.utils.text import slugify
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the blog with initial content'

    def handle(self, *args, **options):
        # Create a system user if needed
        self.stdout.write('Creating system user...')
        user, created = User.objects.get_or_create(username='Admin', email='admin@collabook.click')
        if created:
            user.set_password('admin123')
            user.is_staff = True
            user.is_superuser = True
            user.save()

        # Create Categories
        categories = ['Narrative', 'Game Guide', 'Lore', 'Update', 'Features']
        cat_objs = {}
        for cat_name in categories:
            cat, _ = Category.objects.get_or_create(name=cat_name)
            cat_objs[cat_name] = cat

        # Define specific content
        guides = [
            {
                "title": "Guida completa ai tre mondi di Collabook",
                "category": "Lore",
                "content": """
<h2>Esplora l'Universo di Collabook</h2>
<p>Benvenuto, viaggiatore. In Collabook, non sei limitato a una singola realtà. Il multiverso si apre davanti a te con tre distinti mondi, ognuno ricco di storia, pericoli e opportunità uniche. Questa guida ti condurrà attraverso le complessità di ogni ambientazione, aiutandoti a scegliere dove iniziare la tua leggenda.</p>

<h3>1. Il Regno della Magia Eterna (Fantasy)</h3>
<p>Un mondo dove il mana scorre come fiumi e antichi draghi sorvegliano tesori dimenticati. Qui, la forza bruta si scontra con l'arcano. Le fazioni principali includono l'Ordine dei Maghi, i Cavalieri del Drago e la Gilda dei Ladri dell'Ombra.</p>
<h4>Luoghi Chiave:</h4>
<ul>
    <li><strong>La Cittadella di Cristallo:</strong> Sede del consiglio dei maghi, una città fluttuante accessibile solo a chi possiede il dono.</li>
    <li><strong>La Foresta dei Sussurri:</strong> Un labirinto vivente dove ogni albero ha occhi e orecchie. I druidi qui sono gli unici a conoscere i sentieri sicuri.</li>
</ul>
<h4>Consigli di Sopravvivenza:</h4>
<p>Non sottovalutare mai un incantatore. Porta sempre con te pozioni di resistenza elementale e cerca di stringere alleanze con le creature magiche locali.</p>

<h3>2. La Federazione Galattica (Sci-Fi)</h3>
<p>L'umanità ha raggiunto le stelle, ma non è sola. La Federazione Galattica è un crogiolo di culture aliene, diplomazia interstellare e conflitti spaziali. Prendi il comando della tua nave e naviga tra asteroidi e nebulose.</p>
<h4>Fazioni:</h4>
<ul>
    <li><strong>La Flotta Stellare:</strong> I guardiani della pace e dell'ordine.</li>
    <li><strong>Il Sindacato Commerciale:</strong> Corporazioni che controllano le rotte commerciali e le risorse minerarie.</li>
</ul>
<p>La tecnologia qui è la chiave. Potenzia i tuoi scudi, installa nuovi motori a curvatura e impara a negoziare con specie che pensano in modi completamente diversi dal tuo.</p>

<h3>3. Neon City 2099 (Cyberpunk)</h3>
<p>In un futuro distopico dominato dalle mega-corporazioni, la linea tra uomo e macchina è sfocata. Neon City è una giungla di cemento e ologrammi, dove l'informazione vale più dell'oro.</p>
<p>Qui, il tuo corpo è modificabile. Braccia cibernetiche, occhi potenziati, interfacce neurali. Ma attento alla cyber-psicosi. Più ti potenzi, meno umano diventi.</p>
<p>Scegli il tuo mondo con saggezza, avventuriero. Ognuno offre una sfida diversa, ma la gloria attende chi ha il coraggio di coglierla.</p>
"""
            },
            {
                "title": "Strategie avanzate per sopravvivere in Regno della Magia Eterna",
                "category": "Game Guide",
                "content": """
<h2>Sopravvivenza nel Regno della Magia</h2>
<p>Il Regno della Magia Eterna non perdona. Che tu sia un guerriero veterano o un novizio mago, queste strategie avanzate ti aiuteranno a restare in vita un giorno in più.</p>
<h3>Gestione delle Risorse</h3>
<p>Nel Regno, il mana è prezioso quanto la vita. Non sprecare i tuoi incantesimi più potenti sui nemici minori (mob). Conserva il mana per i boss o per le situazioni di emergenza. Porta sempre con te una scorta di erbe curative; sono più economiche delle pozioni e si trovano facilmente nelle zone selvagge.</p>
<h3>Conoscere il Nemico</h3>
<p>Ogni creatura ha una debolezza elementale. I non-morti temono il fuoco e la luce sacra. Le creature d'acqua sono vulnerabili al fulmine. Usa la tua abilità di 'Osservazione' prima di ingaggiare battaglia per scoprire le resistenze del nemico.</p>
<h3>Il Sistema di Fazioni</h3>
<p>Non puoi essere amico di tutti. Allearsi con i Maghi ti renderà nemico della Chiesa dell'Inquisizione. Scegli con cura le tue alleanze, poiché sbloccheranno equipaggiamento esclusivo e missioni uniche.</p>
<p>Ricorda: un avventuriero preparato è un avventuriero vivo.</p>
"""
            },
            {
                "title": "Tutorial passo-passo per iniziare con Collabook",
                "category": "Features",
                "content": """
<h2>Iniziare la Tua Avventura</h2>
<p>Sei nuovo su Collabook? Nessun problema. Segui questi semplici passi per tuffarti nell'azione.</p>
<h3>Passo 1: Creazione dell'Account</h3>
<p>Clicca su 'Login' o 'Registrati' in alto. Puoi usare il tuo account Google per un accesso immediato o creare un account con email e password.</p>
<h3>Passo 2: Il Tuo Personaggio</h3>
<p>Vai alla sezione 'Character'. Qui definirai chi sei. Scegli un nome evocativo. Distribuisci i tuoi punti statistica. Vuoi essere forte? Agile? Intelligente? Non c'è una scelta sbagliata, solo stili di gioco diversi.</p>
<h3>Passo 3: Scegli il Mondo</h3>
<p>Nella pagina 'Worlds', seleziona l'ambientazione che più ti ispira. Leggi le descrizioni e clicca su 'Entra'.</p>
<h3>Passo 4: La Tua Prima Azione</h3>
<p>Verrai accolto da una descrizione introduttiva. Sotto, vedrai delle opzioni predefinite, ma il vero potere di Collabook sta nella casella di testo libera. Scrivi cosa vuoi fare! "Cerco tracce di magia", "Interrogo l'oste", "Rubo la chiave alla guardia". L'AI interpreterà la tua azione e ti risponderà.</p>
<p>Buona fortuna!</p>
"""
            },
            {
                "title": "Le meccaniche di gioco spiegate nel dettaglio",
                "category": "Game Guide",
                "content": """
<h2>Sotto il Cofano di Collabook</h2>
<p>Collabook combina la libertà della narrazione AI con la struttura solida di un RPG classico. Ecco come funziona.</p>
<h3>Il Motore D20</h3>
<p>Quando tenti un'azione incerta (come attaccare o scalare un muro), il sistema lancia un dado virtuale a 20 facce (D20). Al risultato si somma il tuo modificatore di statistica pertinente.</p>
<p>Esempio: Stai cercando di colpire un goblin. Hai Forza 15 (+2 bonus). Il sistema lancia il dado ed esce un 12. Totale: 14. Se la Classe Armatura (CA) del goblin è 13 o meno, colpisci!</p>
<h3>Combattimento a Turni</h3>
<p>In combattimento, l'ordine di azione è determinato dall'iniziativa (basata sull'Agilità). Hai diverse opzioni: Attacco Base, Abilità Speciale, Oggetto, Fuga. Ogni scelta ha conseguenze tattiche.</p>
<h3>L'AI Dungeon Master</h3>
<p>L'Intelligenza Artificiale agisce come il tuo Dungeon Master. Non decide solo se hai successo o fallisci, ma *come*. Descrive la scena, interpreta i PNG (Personaggi Non Giocanti) e reagisce in modo creativo alle tue idee più folli.</p>
"""
            }
        ]

        # Generate blog posts
        blogs = [
            ("Come creare personaggi RPG memorabili", "Narrative"),
            ("Guida completa ai giochi di ruolo per principianti", "Narrative"),
            ("Storia dei giochi di ruolo: da D&D all'AI", "Lore"),
            ("10 consigli per migliorare la tua narrazione interattiva", "Narrative"),
            ("Come l'intelligenza artificiale sta cambiando i giochi di ruolo", "Features"),
            ("L'arte del World Building: Creare mondi credibili", "Narrative"),
            ("Intervistare i PNG: Come ottenere informazioni cruciali", "Game Guide"),
            ("Gestire l'inventario: Cosa tenere e cosa vendere", "Game Guide"),
            ("Le migliori build per la classe Mago in Collabook", "Game Guide"),
            ("Cyberpunk vs Fantasy: Quale stile fa per te?", "Lore"),
            ("I segreti dei Draghi Antichi", "Lore"),
            ("Navigare nello spazio profondo: Guida alla sopravvivenza", "Game Guide"),
            ("La psicologia del villain: Creare antagonisti complessi", "Narrative"),
            ("Aggiornamento Patch 1.2: Nuove armi e bilanciamenti", "Update"),
            ("Community Spotlight: Le migliori storie dei giocatori", "Narrative"),
            ("Il futuro della narrativa generativa", "Features"),
            ("Come scrivere prompt efficaci per l'AI", "Features"),
            ("Guida al roleplay: Interpretare il tuo personaggio", "Narrative"),
            ("Le fazioni di Neon City spiegate", "Lore"),
            ("Dalla carta allo schermo: L'evoluzione dei Gdr", "Lore")
        ]

        # Add predefined guides
        for guide in guides:
            slug = slugify(guide['title'])
            if not Post.objects.filter(slug=slug).exists():
                Post.objects.create(
                    title=guide['title'],
                    slug=slug,
                    author=user,
                    category=cat_objs.get(guide['category'], cat_objs['Game Guide']),
                    content=guide['content'],
                    status=1,
                    meta_description=guide['content'][:150] + "..."
                )
                self.stdout.write(f"Created guide: {guide['title']}")

        # Add generated blogs
        for title, cat_name in blogs:
            slug = slugify(title)
            if not Post.objects.filter(slug=slug).exists():
                content = f"""
<h2>{title}</h2>
<p>Nel vasto mondo dei giochi di ruolo, {title.lower()} è un argomento fondamentale. Che tu sia un veterano o un novizio, comprendere queste dinamiche può trasformare radicalmente la tua esperienza di gioco.</p>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
<h3>Punti Chiave</h3>
<ul>
    <li>Approfondire la storia del tuo personaggio aumenta l'immersione.</li>
    <li>Non aver paura di fallire; le storie migliori nascono dalle sconfitte.</li>
    <li>Sfrutta al massimo le meccaniche uniche di Collabook.</li>
</ul>
<p>Continua a seguire il nostro blog per altri approfondimenti su {cat_name.lower()} e molto altro!</p>
"""
                Post.objects.create(
                    title=title,
                    slug=slug,
                    author=user,
                    category=cat_objs.get(cat_name, cat_objs['Narrative']),
                    content=content,
                    status=1,
                    meta_description=f"Un articolo approfondito su {title}."
                )
                self.stdout.write(f"Created post: {title}")

        self.stdout.write(self.style.SUCCESS('Successfully populated blog content'))
