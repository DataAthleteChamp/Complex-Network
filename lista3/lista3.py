import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import requests
from pyvis.network import Network
from scipy.sparse import csr_matrix
import json


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

macierz_sasiedztwa = nx.adjacency_matrix(G)
macierz_incydencji = nx.incidence_matrix(G, oriented=True)

# np.set_printoptions(threshold=np.inf)  # nie skraca printowania macierzy

print("Macierz sąsiedztwa:")
print(macierz_sasiedztwa.toarray())
print(macierz_sasiedztwa.shape)

print("Macierz incydencji:")
print(macierz_incydencji.toarray())
print(macierz_incydencji.shape)


def oblicz_wlasciwosci_grafu(G):
    wlasciwosci = {
        'rząd': dict(G.degree()),
        'liczba_wierzcholkow': G.number_of_nodes(),
        'rozmiar': G.number_of_edges(),
        'gestosc': nx.density(G),
        'sredni stopien': np.mean([v for k, v in G.degree()]),
        'srednica': nx.diameter(G) if nx.is_connected(G) else 'Graf nie jest spójny',
        'srednia_dlugosc_sciezki': nx.average_shortest_path_length(G) if nx.is_connected(G) else 'Graf nie jest spójny',
        'Centralność stopnia:': nx.degree_centrality(G),
        'centralnosc_bliskosci': nx.closeness_centrality(G),
        'centralnosc_posrednictwa': nx.betweenness_centrality(G),
        'centralnosc_wektora_wlasnego': nx.eigenvector_centrality_numpy(G),
        'pagerank': nx.pagerank(G)
    }
    return wlasciwosci


print("\nStatystyki sieci:")

wlasciwosci_grafu = oblicz_wlasciwosci_grafu(G)

filename = 'graph_properties.json'

with open(filename, 'w', encoding='utf-8') as file:
    json.dump(wlasciwosci_grafu, file, ensure_ascii=False, indent=4)

print(f"Statystyki sieci zostały zapisane do {filename}")


for nazwa, wartosc in wlasciwosci_grafu.items():
    print(f"{nazwa}: {wartosc}")



rzad = wlasciwosci_grafu['rząd']
wartosci = [v for k, v in rzad.items()]
etykiety = [k for k, v in rzad.items()]

plt.figure(figsize=(10, 6))
plt.pie(wartosci, labels=etykiety, autopct='%1.1f%%')
plt.title('Rząd wierzchołków')
plt.savefig('Rząd wierzchołków')
plt.show()



centralnosc_stopnia = wlasciwosci_grafu['Centralność stopnia:']

plt.figure(figsize=(10, 6))
plt.bar(centralnosc_stopnia.keys(), centralnosc_stopnia.values())
plt.title('Centralność Stopnia')
plt.xlabel('Wierzchołki')
plt.ylabel('Centralność')
plt.yscale('log')
plt.savefig('Centralność Stopnia')
plt.show()


centralnosc_bliskosci = wlasciwosci_grafu['centralnosc_bliskosci']

plt.figure(figsize=(10, 6))
plt.bar(centralnosc_bliskosci.keys(), centralnosc_bliskosci.values())
plt.title('Centralność Bliskości')
plt.xlabel('Wierzchołki')
plt.ylabel('Centralność')
plt.savefig('Centralność Bliskości')
plt.show()


centralnosc_posrednictwa = wlasciwosci_grafu['centralnosc_posrednictwa']
wierzcholki = list(centralnosc_posrednictwa.keys())
wartosci = list(centralnosc_posrednictwa.values())
plt.figure(figsize=(10, 6))
plt.scatter(wierzcholki, wartosci, color='blue')


for i, val in enumerate(wartosci):
    if val == 0.9999999999999999:
        plt.scatter(wierzcholki[i], wartosci[i], color='red')

plt.title('Wykres Rozrzutu Centralności Pośrednictwa')
plt.xlabel('Wierzchołki')
plt.ylabel('Wartość Centralności Pośrednictwa')
plt.xticks(rotation=90)
plt.savefig('Centralności Pośrednictwa')
plt.show()

# centralnosc_posrednictwa = wlasciwosci_grafu['centralnosc_posrednictwa']
#
# plt.figure(figsize=(10, 6))
# plt.bar(centralnosc_posrednictwa.keys(), centralnosc_posrednictwa.values())
# plt.title('Centralność Pośrednictwa')
# plt.xlabel('Wierzchołki')
# plt.ylabel('Centralność')
# plt.yscale('log')
# #plt.show()


centralnosc_wektora_wlasnego = wlasciwosci_grafu['centralnosc_wektora_wlasnego']

plt.figure(figsize=(10, 6))
plt.bar(centralnosc_wektora_wlasnego.keys(), centralnosc_wektora_wlasnego.values())
plt.title('Centralność Wektora Własnego')
plt.xlabel('Wierzchołki')
plt.ylabel('Centralność')
plt.savefig('Centralność Wektora Własnego')
plt.show()


pagerank = wlasciwosci_grafu['pagerank']

plt.figure(figsize=(10, 6))
plt.bar(pagerank.keys(), pagerank.values())
plt.title('PageRank')
plt.xlabel('Wierzchołki')
plt.ylabel('Wartość PageRank')
plt.yscale('log')
plt.savefig('PageRank')
plt.show()

G_sasiedztwa = nx.from_numpy_array(macierz_sasiedztwa)

if isinstance(macierz_incydencji, csr_matrix):
    macierz_incydencji = macierz_incydencji.toarray()

krawedzie = []
for i in range(macierz_incydencji.shape[1]):
    kolumna = macierz_incydencji[:, [i]].toarray().flatten()

plt.figure(figsize=(12, 12))
plt.subplot(121)
nx.draw(G_sasiedztwa, with_labels=True, font_weight='bold', node_color='skyblue')
plt.title('Graf z macierzy sąsiedztwa')
pos = nx.circular_layout(G)
nx.draw(G, pos, labels=mapowanie_etykiet, with_labels=True, node_color='blue', edge_color='black', node_size=500,
        alpha=0.6, font_weight='bold')

plt.subplot(122)
nx.draw(macierz_incydencji, with_labels=True, font_weight='bold', node_color='lightgreen')
plt.title('Graf z macierzy incydencji')
plt.show()

net_sasiedztwa = Network(notebook=True, cdn_resources='remote')
net_sasiedztwa.from_nx(G_sasiedztwa)
for node_id, label in mapowanie_etykiet.items():
    net_sasiedztwa.nodes[node_id]["label"] = label
net_sasiedztwa.show("graf_sasiedztwa.html")
net_sasiedztwa.save_graph("graf_sasiedztwa.html")
net_sasiedztwa.repulsion()
#
net_incydencji = Network(notebook=True, cdn_resources='remote')
net_incydencji.from_nx(macierz_incydencji)
net_incydencji.save_graph("graf_incydencji.html")
net_incydencji.show("graf_incydencji.html")

net = Network("500px", "500px", notebook=True, cdn_resources='remote')
net.from_nx(G)
net.show("network_visualization.html")
net.repulsion()
net.show_buttons("physics")



