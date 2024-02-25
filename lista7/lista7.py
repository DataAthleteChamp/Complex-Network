import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx
import os

# # Konfiguracja osmnx
# ox.config(use_cache=True, log_console=True)

ox.settings.use_cache = True
ox.settings.log_console = True

# Współrzędne centrum Rynek, Wrocław
center_point = (51.1079, 17.0385)


def analyze_network(graph, iteration, file_path="analiza_sieci.txt"):
    with open(file_path, 'a') as file:
        # wielokrotny na zwykły graf
        simple_graph = nx.Graph(graph)

        file.write(f"Iteracja {iteration}:\n")
        num_nodes = simple_graph.number_of_nodes()
        num_edges = simple_graph.number_of_edges()
        avg_length = sum(d['length'] for u, v, d in simple_graph.edges(data=True)) / num_edges
        clustering_coefficient = nx.average_clustering(simple_graph)
        density = nx.density(simple_graph)
        degree_centrality = nx.degree_centrality(simple_graph)
        max_degree_centrality = max(degree_centrality, key=degree_centrality.get)
        betweenness_centrality = nx.betweenness_centrality(simple_graph)
        max_betweenness_centrality = max(betweenness_centrality, key=betweenness_centrality.get)
        closeness_centrality = nx.closeness_centrality(simple_graph)
        max_closeness_centrality = max(closeness_centrality, key=closeness_centrality.get)

        file.write(f"Liczba wezlow: {num_nodes}\n")
        file.write(f"Liczba krawedzi: {num_edges}\n")
        file.write(f"Srednia dlugosc krawedzi: {avg_length:.2f} m\n")
        file.write(f"Wspolczynnik grupowania: {clustering_coefficient:.2f}\n")
        file.write(f"Gestosc sieci: {density:.6f}\n")
        file.write(f"Najwieksza centralnosc stopnia: {max_degree_centrality} ({degree_centrality[max_degree_centrality]:.2f})\n")
        file.write(f"Najwieksza centralnosc posrednictwa: {max_betweenness_centrality} ({betweenness_centrality[max_betweenness_centrality]:.2f})\n")
        file.write(f"Najwieksza centralnosc bliskosci: {max_closeness_centrality} ({closeness_centrality[max_closeness_centrality]:.2f})\n")
        file.write("\n")


def plot_graph(graph, iteration, save_path="wizualizacje"):
    os.makedirs(save_path, exist_ok=True)
    fig, ax = ox.plot_graph(graph, node_size=0, edge_linewidth=0.5, show=False, close=False)
    plt.title(f"Iteracja {iteration}: Sieć ulic w promieniu {iteration * 2} km od centrum Wrocławia")

    file_name = os.path.join(save_path, f"wroclaw_iteracja_{iteration}.png")
    fig.savefig(file_name, format='png', dpi=300)
    plt.close(fig)
    print(f"Wizualizacja zapisana jako: {file_name}")


for i in range(1, 8):
    distance = i * 2000  # Promień wzrasta o 2 km w każdej iteracji
    print(f"\nIteracja {i}:")
    graph = ox.graph_from_point(center_point, dist=distance, network_type='drive')
    analyze_network(graph, i)
    plot_graph(graph, i)
