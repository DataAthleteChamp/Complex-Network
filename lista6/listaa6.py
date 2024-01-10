# Short	Zachary karate club network
# The dataset contains social ties among the members of a university karate club collected by Wayne Zachary in 1977.

import networkx as nx
import scipy.io

file_path = r'C:\Users\Lenovo\Downloads\soc-karate\soc-karate.mtx'
matrix = scipy.io.mmread(file_path)
G = nx.Graph(matrix)

density = nx.density(G)

# współczynnik gronowania
C = nx.average_clustering(G)

# średnia długośc ścieżki
L = nx.average_shortest_path_length(G)

# losowa sieć z tą samą liczbą węzłów i krawędzi
N = len(G.nodes())
E = len(G.edges())
random_graph = nx.gnm_random_graph(N, E)

# Obliczenie parametrów dla losowej sieci
C_random = nx.average_clustering(random_graph)
L_random = nx.average_shortest_path_length(random_graph)

# współczynnik małego świata
sigma = (C / C_random) / (L / L_random)

print(f'Gęstość sieci: {density}')
print(f'Współczynnik gronowania (C): {C}')
print(f'Średnia długość ścieżki (L): {L}')

if sigma > 1:
    print("Sieć ma właściwości małego świata.")
else:
    print("Sieć nie ma właściwości małego świata.")