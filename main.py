import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import json

# Config batards
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# géstion du filtre vinted fait a la rache car trop fatiguer pour faire un truc serieux
FILTERS_FILE = "filters.json"

def load_filters():
    try:
        with open(FILTERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_filters(filters):
    with open(FILTERS_FILE, "w") as f:
        json.dump(filters, f, indent=4)

user_filters = load_filters()

# Fonc récup anonce faite sur vinted 
def fetch_vinted_items(search_query):
    url = f"https://www.vinted.fr/catalog?search_text={search_query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    print(response.text[:1000])  # Afficher les 1000 premiers caractères de la réponse HTML

    items = []
    for item in soup.find_all("div", class_="feed-grid__item"):
        link = item.find("a", class_="web_ui__ItemBox__overlay")
        title = item.find("h2", class_="web_ui__ItemBox__title")
        price = item.find("div", class_="web_ui__ItemBox__price")
        
        if link and title and price:
            items.append({
                "title": title.text.strip(),
                "price": price.text.strip(),
                "url": "https://www.vinted.fr" + link["href"]
            })
    return items

# Commande conf filtre
@bot.command()
async def setfilter(ctx, *, search_query):
    user_id = str(ctx.author.id)
    user_filters[user_id] = search_query
    save_filters(user_filters)
    await ctx.send(f"Filtre enregistré `{search_query}` !")

# commande voir filtre connard si ta besoin de lire sa regarde les tuto python de la chaine de toragp se giga tchat
@bot.command()
async def myfilters(ctx):
    user_id = str(ctx.author.id)
    if user_id in user_filters:
        await ctx.send(f"Ton filtre petit batard : `{user_filters[user_id]}`")
    else:
        await ctx.send(" Tu n'as pas défini ton putin de filtre. Utilise `!setfilter <recherche>` connard.")

# commande pour supre la même que la remarque du haut
@bot.command()
async def removefilter(ctx):
    user_id = str(ctx.author.id)
    if user_id in user_filters:
        del user_filters[user_id]
        save_filters(user_filters)
        await ctx.send("Ton filtre supprimé j'ai fait !")
    else:
        await ctx.send("Aucun filtre trouvé pour toi t adopté misquine bououououououou.")

# Commande pour afficher des articles selon le filtre ouai je sais c safe celle la ba tu connai les temps son dure
@bot.command()
async def showitems(ctx):
    user_id = str(ctx.author.id)
    if user_id not in user_filters:
        await ctx.send(" Tu n'as pas encore défini de filtre. Utilise `!setfilter <recherche>` connard.")
        return
    
    search_query = user_filters[user_id]
    items = fetch_vinted_items(search_query)
    
    if not items:
        await ctx.send("Aucun article trouvé pour ton filtre actuel pedale vas bhouououou.")
        return
    
    msg = "**Voici quelques articles correspondant à ton filtre mdr :**\n"
    for item in items[:5]:  # Afficher les 5 premiers résultats
        msg += f" {item['title']} - {item['price']}\ {item['url']}\n\n"
    
    await ctx.send(msg)

# Tâche automatique envoyer les annonces filtrées ( ps la normale si tu comprend pas même moi je me dit la tora tu fait de la merde mais hasoule)
@tasks.loop(minutes=2)
async def check_vinted():
    for user_id, search_query in user_filters.items():
        user = await bot.fetch_user(int(user_id))
        if user:
            items = fetch_vinted_items(search_query)
            if items:
                msg = "**Nouvelles annonces Vinted trouvées :**\n"
                for item in items[:3]:  # Envoie seulement 3 résultats stop spam
                    msg += f" {item['title']} - {item['price']}\n {item['url']}\n\n"
                try:
                    await user.send(msg)
                except:
                    print(f"Impossible d'envoyer un message à {user_id} car kelio fait chier avec ses idée de merde je suis fatiguer moi putain")

# la chef toi même maméne tu sais
@bot.event
async def on_ready():
    print(f" Connecté {bot.user.name} ({bot.user.id})")
    check_vinted.start()

if __name__ == "__main__":
    TOKEN = "MTI1MTgzNDgxNzgwNTI4NzQ3NA.G6fvLi.Jo_cFIvsAxX3UAIQJDK4MC5Xb1cnaRc4z9B0uM"  # vilain si tu sais pas sa pas grave c le token de ton bote discorde mon chouchou
    bot.run(TOKEN)
