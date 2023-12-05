import networkx as nx
import matplotlib.pyplot as plt
import requests
from pyvis.network import Network
import scipy as sp

# Funkcja do pobierania danych z API GitHuba
def pobierz_wszystkie_dane(url):
    wyniki = []
    page = 1
    while True:
        response = requests.get(f"{url}?page={page}&per_page=100")
        if response.status_code != 200:
            print(f"error {response.status_code}: nie można pobrać")
            break

        dane = response.json()
        if not dane:
            break

        wyniki.extend(dane)
        page += 1

    return wyniki

# Pobieranie danych
url = 'https://api.github.com/users/isocpp/followers'
wszystkie_dane = pobierz_wszystkie_dane(url)
print(f"Pobrano {len(wszystkie_dane)} wyników")

# Tworzenie grafu
G = nx.Graph()
for rekord in wszystkie_dane:
    follower = rekord['login']
    G.add_edge(follower, 'isocpp', capacity=1, flow=1)

# Etykiety krawędzi
edge_labels = {(u, v): f"{d['flow']}/{d['capacity']}" for u, v, d in G.edges(data=True)}

# Rysowanie grafu
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1000, edge_color='black')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
plt.show()

# Wyświetlanie podstawowych informacji o grafie
print("Wierzchołki grafu:")
print(G.nodes())


# Tworzenie macierzy sąsiedztwa
macierz_sasiedztwa = nx.adjacency_matrix(G)

# Tworzenie macierzy incydencji
macierz_incydencji = nx.incidence_matrix(G, oriented=True)  # 'oriented' dla grafów skierowanych



# Konwersja macierzy na format, który można łatwo obsłużyć
macierz_sasiedztwa_array = macierz_sasiedztwa.toarray()
macierz_incydencji_array = macierz_incydencji.toarray()



liczba_kolumn = macierz_incydencji_array.shape[1]  # zwróci liczbę kolumn w macierzy

for i in range(liczba_kolumn):  # teraz iterujesz od 0 do liczba_kolumn-1
    for j, incydencja in enumerate(macierz_incydencji_array[:, i]):
        # ... reszta Twojego kodu ...
# Wypisanie macierzy (opcjonalnie, dla weryfikacji)
print("Macierz sąsiedztwa:")
print(macierz_sasiedztwa_array)
print("\nMacierz incydencji:")
print(macierz_incydencji_array)

# Teraz, mając macierze, możemy stworzyć nowe grafy w NetworkX, używając tych macierzy

# Tworzenie nowego grafu z macierzy sąsiedztwa
graf_z_macierzy_sasiedztwa = nx.from_numpy_array(macierz_sasiedztwa_array)

# Tworzenie nowego grafu z macierzy sąsiedztwa
#graf_z_macierzy_sasiedztwa = nx.from_numpy_matrix(macierz_sasiedztwa_array)

# Tworzenie nowego grafu z macierzy incydencji jest bardziej złożone, ponieważ NetworkX nie ma bezpośredniej funkcji do tego.
# Jednak można to zrobić manualnie, iterując przez macierz i dodając krawędzie.

graf_z_macierzy_incydencji = nx.Graph()  # lub nx.DiGraph() dla grafu skierowanego
wierzcholki = list(G.nodes())
for i, w in enumerate(wierzcholki):
    for j, incydencja in enumerate(macierz_incydencji_array[:, i]):
        if incydencja != 0:
            # Dla grafów nieskierowanych, dodajemy krawędź, jeśli istnieje incydencja
            graf_z_macierzy_incydencji.add_edge(wierzcholki[i], wierzcholki[j])

# Teraz mamy dwa nowe grafy utworzone z macierzy. Możesz kontynuować pracę z tymi grafami w NetworkX.




# Analiza grafu
print(f"Liczba wierzchołków: {G.number_of_nodes()}")
print(f"Liczba krawędzi: {G.number_of_edges()}")
print(f"Graf jest spójny: {nx.is_connected(G)}")

if nx.is_connected(G):
    print(f"Średnica grafu: {nx.diameter(G)}")
    print(f"Promień grafu: {nx.radius(G)}")

# Wizualizacja za pomocą Pyvis
#net = Network(notebook=True)
net = Network("500px", "500px", notebook=True, cdn_resources='remote')  # lub 'remote'

net.from_nx(G)
net.show("network_visualization.html")
