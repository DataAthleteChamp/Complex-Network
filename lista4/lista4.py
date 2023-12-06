import requests
from networkx.algorithms.community import girvan_newman, greedy_modularity_communities, modularity
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import networkx as nx
from scipy.spatial.distance import pdist, squareform


def pobierz_wszystkie_dane(url):
    wyniki = []
    page = 1
    while True:
        response = requests.get(f"{url}?page={page}&per_page=100")
        if response.status_code != 200:
            print(
                f"error {response.status_code}: nie można pobrać \nmessage:API rate limit exceeded for 37.30.16.8. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)",
                "documentation_url https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting")
            break

        dane = response.json()
        if not dane:
            break

        wyniki.extend(dane)
        page += 1

    return wyniki


url = 'https://api.github.com/users/isocpp/followers'
wszystkie_dane = pobierz_wszystkie_dane(url)
print(f"Pobrano {len(wszystkie_dane)} wyników")

G = nx.Graph()
for rekord in wszystkie_dane:
    follower = rekord['login']
    G.add_edge(follower, 'isocpp')

nazwy_uzytkownikow = [uzytkownik['login'] for uzytkownik in wszystkie_dane]
nazwy_uzytkownikow.append('isocpp')
mapowanie_etykiet = {idx: nazwa for idx, nazwa in enumerate(nazwy_uzytkownikow)}

# Podstawowa analiza grafu
liczba_wierzcholkow = G.number_of_nodes()
liczba_krawedzi = G.number_of_edges()
sredni_stopien = np.mean([degree for node, degree in G.degree()])

print("Liczba wierzchołków:", liczba_wierzcholkow)
print("Liczba krawędzi:", liczba_krawedzi)
print("Średni stopień węzłów:", sredni_stopien)

# plt.figure(figsize=(12, 8))
# nx.draw(G, with_labels=True)
# plt.show()


# Wydzielenie kliki
kliki = list(nx.find_cliques(G))
print("Liczba wydzielonych klik:", len(kliki))
print("Znalezione kliki (pierwsze 5):", kliki[:5])  # Wyświetlenie pierwszych 5 kliki

# Generowanie społeczności za pomocą algorytmu Girvan-Newman
communities_generator = girvan_newman(G)
top_level_communities = next(communities_generator)
next_level_communities = next(communities_generator)

moduly_girvan_newman = [list(community) for community in next_level_communities]

print("Liczba wydzielonych modułów metodą Girvan-Newman:", len(moduly_girvan_newman))
print("Znalezione moduły metodą Girvan-Newman (pierwsze 5):", moduly_girvan_newman[:5])


# Aglomeracyjna analiza skupień i dendrogram
def graf_do_macierzy_odleglosci(G):
    path_length = dict(nx.all_pairs_shortest_path_length(G))
    size = len(G)
    macierz_odleglosci = np.zeros((size, size))
    for i, node_i in enumerate(G.nodes()):
        for j, node_j in enumerate(G.nodes()):
            try:
                macierz_odleglosci[i, j] = path_length[node_i][node_j]
            except KeyError:
                macierz_odleglosci[i, j] = np.inf
    return macierz_odleglosci


macierz_odleglosci = graf_do_macierzy_odleglosci(G)

Z = linkage(squareform(macierz_odleglosci), method='average')  # 'single', 'complete'

# v1
#plt.figure(figsize=(15, 10))
# dendrogram(Z, truncate_mode='lastp', p=30, leaf_rotation=90., leaf_font_size=12., show_contracted=True)
# plt.title("Dendrogram aglomeracyjnej analizy skupień")
# plt.xlabel("Numer próbki")
# plt.ylabel("Odległość")
# plt.show()

# v2
plt.figure(figsize=(10, 7))
dendrogram(Z)
plt.title("Dendrogram aglomeracyjnej analizy skupień")
plt.xlabel("Numer próbki")
plt.ylabel("Odległość")
plt.savefig("Dendrogram.png")
plt.show()

# Porównanie metod aglomeracyjnych i podziałowych

# Metoda aglomeracyjna
Z = linkage(squareform(graf_do_macierzy_odleglosci(G)), method='ward')
max_d = 2  # próg odległości do definiowania klastrów
clusters = fcluster(Z, max_d, criterion='distance')
agglomerative_communities = {}
for node, cluster in zip(G.nodes(), clusters):
    if cluster not in agglomerative_communities:
        agglomerative_communities[cluster] = []
    agglomerative_communities[cluster].append(node)

# Metoda podziałowa - Fast Greedy
fast_greedy_communities = list(greedy_modularity_communities(G))
fast_greedy_communities = [list(community) for community in fast_greedy_communities]

# Obliczanie modularności dla obu metod
modularity_agglomerative = modularity(G, agglomerative_communities.values())
modularity_fast_greedy = modularity(G, fast_greedy_communities)

print("Modularność dla metody aglomeracyjnej:", modularity_agglomerative)
print("Modularność dla metody Fast Greedy:", modularity_fast_greedy)


# Metoda podziału spektralnego

# Tworzenie macierzy Laplace'a
L = nx.laplacian_matrix(G).astype(float)

# Obliczanie dwóch najmniejszych wartości własnych i odpowiadających im wektorów własnych
eigenvalues, eigenvectors = eigsh(L, k=2, which='SM')

# Wykorzystanie drugiego najmniejszego wektora własnego do podziału grafu
fiedler_vector = eigenvectors[:, 1]

# Podział węzłów na dwie społeczności
nodes = np.array(G.nodes())
community1 = nodes[fiedler_vector > 0]
community2 = nodes[fiedler_vector <= 0]

# Wyniki
print("Społeczność 1:", community1)
print("-----------------------------------")
print("Społeczność 2:", community2)

# Analiza charakteru hierarchicznego sieci

# 1. Analiza Rozkładu Stopni Węzłów
stopnie = [G.degree(n) for n in G.nodes()]
plt.figure(figsize=(10, 6))
plt.hist(stopnie, bins=20)
plt.title('Histogram Stopni Węzłów')
plt.xlabel('Stopień')
plt.ylabel('Liczba Węzłów')
plt.savefig('Histogram Stopni Węzłów.png')
plt.show()

# 2. Analiza Centralności Pośrednictwa
betweenness = nx.betweenness_centrality(G)
plt.figure(figsize=(10, 6))
plt.bar(range(len(betweenness)), list(betweenness.values()))
plt.title('Centralność Pośrednictwa Węzłów')
plt.xlabel('Węzeł')
plt.ylabel('Centralność Pośrednictwa')
plt.savefig('Centralność Pośrednictwa Węzłów')
plt.show()

# 3. Analiza Dendrogramu
plt.figure(figsize=(10, 7))
dendrogram(Z)
plt.title('Dendrogram Aglomeracyjnej Analizy Skupień')
#plt.show()
