import csv
import networkx as nx

def clean(value, precision=6):
    # Convert extremely small values (positive or negative) to exactly 0.0
    if abs(value) < 1e-12:
        return 0.0
    return round(float(value), precision)

print("Loading dataset...")

# Load CSV manually
edges = []
with open("social_network.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        if len(row) >= 2:
            edges.append((row[0].strip(), row[1].strip()))

print("Dataset loaded.")

# Create directed graph
G = nx.DiGraph()
G.add_edges_from(edges)

print("\nGraph Summary:")
print("Nodes:", list(G.nodes()))
print("Edges:", list(G.edges()))

# ---------------- PAGE RANK ---------------- #
try:
    pagerank = nx.pagerank_numpy(G, alpha=0.85)
except:
    pagerank = nx.pagerank(G, alpha=0.85)

print("\nPageRank Scores:")
for node, score in sorted(pagerank.items(), key=lambda x: x[1], reverse=True):
    print(f"{node}: {clean(score)}")

top_pr = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
print("\nTop 5 by PageRank:", [(n, clean(s)) for n, s in top_pr])

# ---------------- HITS ---------------- #
hubs, authorities = nx.hits(G, max_iter=500, normalized=True)

print("\nAuthority Scores:")
for node, score in sorted(authorities.items(), key=lambda x: x[1], reverse=True):
    print(f"{node}: {clean(score)}")

print("\nHub Scores:")
for node, score in sorted(hubs.items(), key=lambda x: x[1], reverse=True):
    print(f"{node}: {clean(score)}")

top_auth = sorted(authorities.items(), key=lambda x: x[1], reverse=True)[:5]
top_hubs = sorted(hubs.items(), key=lambda x: x[1], reverse=True)[:5]

print("\nTop Authorities:", [(n, clean(s)) for n, s in top_auth])
print("Top Hubs:", [(n, clean(s)) for n, s in top_hubs])

print("\nBackend Processing Complete.")
