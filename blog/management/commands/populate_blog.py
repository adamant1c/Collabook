from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog.models import Post, Category
from django.utils.text import slugify
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the blog with initial content in EN and IT'

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
        categories = [
            {'en': 'Narrative', 'it': 'Narrativa'},
            {'en': 'Game Guide', 'it': 'Guida di Gioco'},
            {'en': 'Lore', 'it': 'Ambientazione'},
            {'en': 'Update', 'it': 'Aggiornamento'},
            {'en': 'Features', 'it': 'Funzionalità'}
        ]
        
        cat_objs = {}
        for cat_data in categories:
            cat, _ = Category.objects.get_or_create(name=cat_data['en'])
            cat.name_it = cat_data['it']
            cat.save()
            cat_objs[cat_data['en']] = cat

        # Define specific content
        guides = [
            {
                "title_en": "Complete Guide to Collabook's Three Worlds",
                "title_it": "Guida completa ai tre mondi di Collabook",
                "category": "Lore",
                "content_en": """
<h2>Explore the Collabook Universe</h2>
<p>Welcome, traveler. In Collabook, you are not limited to a single reality. The multiverse opens before you with three distinct worlds, each rich in history, danger, and unique opportunities. This guide will lead you through the intricacies of each setting, helping you choose where to begin your legend.</p>

<h3>1. The Realm of Eternal Magic (Fantasy)</h3>
<p>A world where mana flows like rivers and ancient dragons guard forgotten treasures. Here, brute strength clashes with the arcane. Main factions include the Order of Mages, the Dragon Knights, and the Shadow Thieves Guild.</p>
<h4>Key Locations:</h4>
<ul>
    <li><strong>The Crystal Citadel:</strong> Seat of the council of mages, a floating city accessible only to those who possess the gift.</li>
    <li><strong>The Whispering Forest:</strong> A living labyrinth where every tree has eyes and ears. The druids here are the only ones who know the safe paths.</li>
</ul>
<h4>Survival Tips:</h4>
<p>Never underestimate a spellcaster. Always carry elemental resistance potions and try to forge alliances with local magical creatures.</p>

<h3>2. The Galactic Federation (Sci-Fi)</h3>
<p>Humanity has reached the stars, but it is not alone. The Galactic Federation is a melting pot of alien cultures, interstellar diplomacy, and space conflicts. Take command of your ship and navigate through asteroids and nebulae.</p>
<h4>Factions:</h4>
<ul>
    <li><strong>The Starfleet:</strong> The guardians of peace and order.</li>
    <li><strong>The Trade Syndicate:</strong> Corporations that control trade routes and mineral resources.</li>
</ul>
<p>Technology here is the key. Upgrade your shields, install new warp engines, and learn to negotiate with species that think in ways completely different from yours.</p>

<h3>3. Neon City 2099 (Cyberpunk)</h3>
<p>In a dystopian future dominated by mega-corporations, the line between man and machine is blurred. Neon City is a concrete and hologram jungle, where information is worth more than gold.</p>
<p>Here, your body is modifiable. Cybernetic arms, enhanced eyes, neural interfaces. But beware of cyber-psychosis. The more you enhance yourself, the less human you become.</p>
<p>Choose your world wisely, adventurer. Each offers a different challenge, but glory awaits those who have the courage to seize it.</p>
""",
                "content_it": """
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
                "title_en": "Advanced Strategies for Survival in the Realm of Eternal Magic",
                "title_it": "Strategie avanzate per sopravvivere in Regno della Magia Eterna",
                "category": "Game Guide",
                "content_en": """
<h2>Survival in the Magic Realm</h2>
<p>The Realm of Eternal Magic is unforgiving. Whether you are a veteran warrior or a novice mage, these advanced strategies will help you stay alive one more day.</p>
<h3>Resource Management</h3>
<p>In the Realm, mana is as precious as life. Do not waste your most powerful spells on minor enemies (mobs). Save mana for bosses or emergency situations. Always carry a supply of healing herbs; they are cheaper than potions and easily found in the wilderness.</p>
<h3>Know Your Enemy</h3>
<p>Every creature has an elemental weakness. Undead fear fire and holy light. Water creatures are vulnerable to lightning. Use your 'Observation' skill before engaging in battle to discover the enemy's resistances.</p>
<h3>The Faction System</h3>
<p>You cannot be friends with everyone. Allying with the Mages will make you an enemy of the Church of the Inquisition. Choose your alliances carefully, as they will unlock exclusive equipment and unique missions.</p>
<p>Remember: a prepared adventurer is a living adventurer.</p>
""",
                "content_it": """
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
            }
        ]

        # Seed specific guides
        for guide in guides:
            slug = slugify(guide['title_en'])
            static_img = "images/blog/guide.png" if guide['category'] == 'Game Guide' else "images/blog/narrative.png"
            
            post, created = Post.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': guide['title_en'],
                    'title_it': guide['title_it'],
                    'author': user,
                    'category': cat_objs.get(guide['category'], cat_objs['Game Guide']),
                    'content': guide['content_en'],
                    'content_it': guide['content_it'],
                    'status': 1,
                    'static_image': static_img
                }
            )
            if not created:
                post.title = guide['title_en']
                post.title_it = guide['title_it']
                post.content = guide['content_en']
                post.content_it = guide['content_it']
                post.static_image = static_img
                post.save()
            self.stdout.write(f"Updated/Created guide: {guide['title_en']}")

        # Generate generic blogs
        blogs_it = [
            ("Come creare personaggi RPG memorabili", "Narrativa"),
            ("Guida completa ai giochi di ruolo per principianti", "Narrativa"),
            ("Storia dei giochi di ruolo: da D&D all'AI", "Ambientazione"),
            ("10 consigli per migliorare la tua narrazione interattiva", "Narrativa"),
            ("Come l'intelligenza artificiale sta cambiando i giochi di ruolo", "Funzionalità")
        ]
        
        blogs_en = [
            ("How to Create Memorable RPG Characters", "Narrative"),
            ("Complete Guide to Role-Playing Games for Beginners", "Narrative"),
            ("History of RPGs: From D&D to AI", "Lore"),
            ("10 Tips to Improve Your Interactive Storytelling", "Narrative"),
            ("How Artificial Intelligence is Changing RPGs", "Features")
        ]

        for i in range(len(blogs_en)):
            title_en, cat_en = blogs_en[i]
            title_it, cat_it = blogs_it[i]
            slug = slugify(title_en)
            
            content_en = f"""
<h2>{title_en}</h2>
<p>In the vast world of role-playing games, {title_en.lower()} is a fundamental topic. Whether you're a veteran or a novice, understanding these dynamics can radically transform your gaming experience.</p>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Experience the magic of AI storytelling.</p>
<h3>Key Points</h3>
<ul>
    <li>Deepening your character's history increases immersion.</li>
    <li>Don't be afraid to fail; the best stories are born from defeats.</li>
    <li>Make the most of Collabook's unique mechanics.</li>
</ul>
<p>Keep following our blog for more insights on {cat_en.lower()} and much more!</p>
"""
            content_it = f"""
<h2>{title_it}</h2>
<p>Nel vasto mondo dei giochi di ruolo, {title_it.lower()} è un argomento fondamentale. Che tu sia un veterano o un novizio, comprendere queste dinamiche può trasformare radicalmente la tua esperienza di gioco.</p>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivi la magia della narrazione AI.</p>
<h3>Punti Chiave</h3>
<ul>
    <li>Approfondire la storia del tuo personaggio aumenta l'immersione.</li>
    <li>Non aver paura di fallire; le storie migliori nascono dalle sconfitte.</li>
    <li>Sfrutta al massimo le meccaniche uniche di Collabook.</li>
</ul>
<p>Continua a seguire il nostro blog per altri approfondimenti su {cat_it.lower()} e molto altro!</p>
"""
            
            post, created = Post.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title_en,
                    'title_it': title_it,
                    'author': user,
                    'category': cat_objs.get(cat_en, cat_objs['Narrative']),
                    'content': content_en,
                    'content_it': content_it,
                    'status': 1,
                    'static_image': "images/blog/narrative.png"
                }
            )
            if not created:
                post.title = title_en
                post.title_it = title_it
                post.content = content_en
                post.content_it = content_it
                post.save()
            self.stdout.write(f"Updated/Created post: {title_en}")

        self.stdout.write(self.style.SUCCESS('Successfully populated multi-language blog content'))
