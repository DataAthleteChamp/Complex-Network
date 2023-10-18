import networkx as nx
import matplotlib.pyplot as plt
import requests


def pobierz_wszystkie_dane(url):
    wyniki = []
    page = 1
    while True:
        response = requests.get(f"{url}?page={page}&per_page=100")
        if response.status_code != 200:
            print(f"Błąd {response.status_code}: Nie można pobrać danych.")
            break

        dane = response.json()
        if not dane:
            break

        wyniki.extend(dane)
        page += 1

    return wyniki


url = 'https://api.github.com/users/isocpp/followers'
wszystkie_dane = pobierz_wszystkie_dane(url)
print(f"Pobrano {len(wszystkie_dane)} rekordów.")


G = nx.Graph()


for rekord in wszystkie_dane:
    follower = rekord['login']
    G.add_edge(follower, 'isocpp', capacity=1, flow=1)

edge_labels = {(u, v): f"{d['flow']}/{d['capacity']}" for u, v, d in G.edges(data=True)}


plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1000, edge_color='black')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
plt.show()


print("Wierzchołki w grafie:")
print(G.nodes())


def znajdz_najkrotsza_sciezke(graf, start, koniec):
    try:
        sciezka = nx.shortest_path(graf, source=start, target=koniec)
        return sciezka
    except nx.NetworkXNoPath:
        return None


def sciezka_eulera(graf):
    if nx.is_eulerian(graf):
        return list(nx.eulerian_circuit(graf))
    else:
        return None


def maksymalny_przeplyw(graf, zrodlo, cel):
    przeplyw_wartosc, _ = nx.maximum_flow(graf, zrodlo, cel, capacity='capacity')
    return przeplyw_wartosc


start, koniec = 'smokku', 'jevinskie'
sciezka = znajdz_najkrotsza_sciezke(G, start, koniec)
if sciezka:
    print(f"Najkrótsza ścieżka od {start} do {koniec} to: {sciezka}")
else:
    print(f"Nie istnieje ścieżka między {start} a {koniec}.")

euler = sciezka_eulera(G)
if euler:
    print("Graf jest eulerowski. Oto ścieżka Eulera:")
    print(euler)
else:
    print("Graf nie jest eulerowski.")

zrodlo, cel = 'yuchen', 'YuncyYe'
przeplyw = maksymalny_przeplyw(G, zrodlo, cel)
print(f"Maksymalny przepływ między {zrodlo} a {cel} wynosi {przeplyw}")
