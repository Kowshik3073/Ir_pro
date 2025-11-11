import csv
import networkx as nx
import numpy as np

print("Loading dataset...")
# Load CSV manually (edge list, no header expected)
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

# --- Manual PageRank Implementation --- #
def manual_pagerank(G, alpha=0.85, tol=1e-4, max_iter=100):
    nodes = list(G.nodes())
    N = len(nodes)
    pr = {node: 1.0 / N for node in nodes}
    out_degree = {node: G.out_degree(node) for node in nodes}
    for it in range(max_iter):
        pr_new = {}
        for node in nodes:
            s = 0.0
            for nbr in G.predecessors(node):
                if out_degree[nbr] > 0:
                    s += pr[nbr] / out_degree[nbr]
            pr_new[node] = (1 - alpha) / N + alpha * s
        # Convergence check
        diff = sum(abs(pr_new[n] - pr[n]) for n in nodes)
        pr = pr_new
        if diff < tol:
            print(f"PageRank converged after {it+1} iterations (diff={diff:.6f})")
            break
    return pr

pagerank = manual_pagerank(G, alpha=0.85, tol=1e-4)
print("\n=== PageRank Scores ===")
for node, score in sorted(pagerank.items(), key=lambda x: x[1], reverse=True):
    print(f"{node}: {round(score, 6)}")
top_pr = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
print("\nTop 5 by PageRank:", top_pr)

# --- Manual HITS Implementation --- #
def manual_hits(G, max_iter=100, tol=1e-4):
    nodes = list(G.nodes())
    N = len(nodes)
    auth = {node: 1.0 for node in nodes}
    hub = {node: 1.0 for node in nodes}
    for it in range(max_iter):
        auth_new = {node: 0.0 for node in nodes}
        hub_new = {node: 0.0 for node in nodes}
        # Update authority
        for node in nodes:
            for nbr in G.predecessors(node):
                auth_new[node] += hub[nbr]
        # Normalize authority
        norm = np.linalg.norm(list(auth_new.values()))
        if norm > 0:
            for node in nodes:
                auth_new[node] /= norm
        # Update hub
        for node in nodes:
            for nbr in G.successors(node):
                hub_new[node] += auth_new[nbr]
        # Normalize hub
        norm = np.linalg.norm(list(hub_new.values()))
        if norm > 0:
            for node in nodes:
                hub_new[node] /= norm
        # Convergence check
        diff = sum(abs(auth_new[n] - auth[n]) + abs(hub_new[n] - hub[n]) for n in nodes)
        auth, hub = auth_new, hub_new
        if diff < tol:
            print(f"HITS converged after {it+1} iterations (diff={diff:.6f})")
            break
    return hub, auth

hubs, authorities = manual_hits(G, max_iter=500, tol=1e-4)
print("\n=== Authority Scores ===")
for node, score in sorted(authorities.items(), key=lambda x: x[1], reverse=True):
    print(f"{node}: {round(score, 6)}")
print("\n=== Hub Scores ===")
for node, score in sorted(hubs.items(), key=lambda x: x[1], reverse=True):
    print(f"{node}: {round(score, 6)}")
top_auth = sorted(authorities.items(), key=lambda x: x[1], reverse=True)[:5]
top_hubs = sorted(hubs.items(), key=lambda x: x[1], reverse=True)[:5]
print("\nTop Authorities:", top_auth)
print("Top Hubs:", top_hubs)

# --- Comparison Section --- #
print("\n" + "="*80)
print("DETAILED COMPARISON OF PageRank vs HITS")
print("="*80)

# Get top nodes by each metric
top_pr_list = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]
top_auth_list = sorted(authorities.items(), key=lambda x: x[1], reverse=True)[:5]
top_hubs_list = sorted(hubs.items(), key=lambda x: x[1], reverse=True)[:5]

top_pr_nodes = set(n for n, _ in top_pr_list)
top_auth_nodes = set(n for n, _ in top_auth_list)
top_hub_nodes = set(n for n, _ in top_hubs_list)

print("\nTOP 5 BY PAGERANK (Influence):")
for i, (node, score) in enumerate(top_pr_list, 1):
    print(f"  {i}. {node}: {score:.6f}")

print("\nTOP 5 BY AUTHORITY (Trustworthiness - cited by hubs):")
for i, (node, score) in enumerate(top_auth_list, 1):
    print(f"  {i}. {node}: {score:.6f}")

print("\nTOP 5 BY HUB (Influence - links to authorities):")
for i, (node, score) in enumerate(top_hubs_list, 1):
    print(f"  {i}. {node}: {score:.6f}")

print("\n" + "-"*80)
print("INTERSECTION ANALYSIS:")
print("-"*80)

common_pr_auth = top_pr_nodes & top_auth_nodes
common_pr_hub = top_pr_nodes & top_hub_nodes
common_all = top_pr_nodes & top_auth_nodes & top_hub_nodes

print(f"\nNodes in TOP 5 PageRank AND TOP 5 Authority: {common_pr_auth if common_pr_auth else 'None'}")
print(f"Nodes in TOP 5 PageRank AND TOP 5 Hub: {common_pr_hub if common_pr_hub else 'None'}")
print(f"Nodes in ALL THREE top 5 lists: {common_all if common_all else 'None'}")

print("\n" + "-"*80)
print("INTERPRETATION:")
print("-"*80)
if common_all:
    print(f"\nNode(s) {common_all} are CRITICAL to the network:")
    print("  - Highly influential overall (PageRank)")
    print("  - Trusted/cited by many important sources (Authority)")
    print("  - Links to other important sources (Hub)")
elif common_pr_auth:
    print(f"\nNode(s) {common_pr_auth} combine influence with trustworthiness:")
    print("  - PageRank recognizes their overall importance")
    print("  - HITS recognizes them as authoritative sources")
elif common_pr_hub:
    print(f"\nNode(s) {common_pr_hub} are influential connectors:")
    print("  - PageRank recognizes their overall importance")
    print("  - HITS recognizes them as important hubs (good at linking)")
else:
    print("\nNo overlap between top PageRank and HITS rankings.")
    print("This suggests:")
    print("  - PageRank emphasizes broad network flow")
    print("  - HITS emphasizes hub-authority relationships")
    print("  - Different aspects of importance are captured by each algorithm")

print("\n" + "="*80)

# --- CREATE SINGLE PNG WITH 3 SUBGRAPHS USING PIL --- #
try:
    from PIL import Image, ImageDraw, ImageFont
    import math
    
    print("\nGenerating 3-graph visualization (PageRank, Authority, Hub)...")
    
    nodes = list(G.nodes())
    
    # Normalize all scores to 0-1 range
    pr_vals = np.array([pagerank[n] for n in nodes])
    auth_vals = np.array([authorities[n] for n in nodes])
    hub_vals = np.array([hubs[n] for n in nodes])
    
    pr_norm = (pr_vals - pr_vals.min()) / (pr_vals.max() - pr_vals.min()) if pr_vals.max() > pr_vals.min() else np.ones_like(pr_vals)
    auth_norm = (auth_vals - auth_vals.min()) / (auth_vals.max() - auth_vals.min()) if auth_vals.max() > auth_vals.min() else np.ones_like(auth_vals)
    hub_norm = (hub_vals - hub_vals.min()) / (hub_vals.max() - hub_vals.min()) if hub_vals.max() > hub_vals.min() else np.ones_like(hub_vals)
    
    # Image setup: 3 graphs side by side with MUCH larger spacing
    graph_width, graph_height = 900, 800
    total_width = graph_width * 3 + 120  # 3 graphs + margins
    total_height = graph_height + 280  # Title + margins
    
    img = Image.new('RGB', (total_width, total_height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Node positions (same for all 3 graphs) - spread out more to avoid collision
    pos = {}
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / len(nodes)
        r = 340  # Increased radius for more spacing between nodes
        pos[node] = (graph_width // 2 + r * math.cos(angle), graph_height // 2 + r * math.sin(angle))
    
    def draw_arrow(draw, x1, y1, x2, y2, fill_color='#000000', width=4):
        """Draw a line with an arrow in the middle pointing from (x1,y1) to (x2,y2)"""
        import math
        
        # Draw the line
        draw.line([(x1, y1), (x2, y2)], fill=fill_color, width=width)
        
        # Calculate midpoint
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # Calculate arrow direction
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_length = 30  # Length of arrow from tip to base
        arrow_width = 18   # Width of arrow
        
        # Arrow tip is at midpoint
        # Two points forming the arrowhead base
        arrow_p1 = (
            mid_x - arrow_length * math.cos(angle) - arrow_width * math.sin(angle),
            mid_y - arrow_length * math.sin(angle) + arrow_width * math.cos(angle)
        )
        arrow_p2 = (
            mid_x - arrow_length * math.cos(angle) + arrow_width * math.sin(angle),
            mid_y - arrow_length * math.sin(angle) - arrow_width * math.cos(angle)
        )
        
        # Draw filled arrowhead with dark border
        draw.polygon([(mid_x, mid_y), arrow_p1, arrow_p2], fill=fill_color)
        # Draw arrowhead outline for better visibility
        draw.line([(mid_x, mid_y), arrow_p1], fill='#000000', width=2)
        draw.line([(mid_x, mid_y), arrow_p2], fill='#000000', width=2)
        draw.line([arrow_p1, arrow_p2], fill='#000000', width=2)
    
    def draw_graph(draw, graph_pos, scores_norm, start_x, start_y, graph_w, graph_h, title, color):
        """Draw a single network graph with node sizes based on scores"""
        # Load larger font - try multiple options
        try:
            # Try to load a larger truetype font if available
            large_font = ImageFont.truetype("arial.ttf", 28)
            title_font = ImageFont.truetype("arial.ttf", 32)
        except:
            try:
                large_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 28)
                title_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 32)
            except:
                # Fallback to default large font
                large_font = ImageFont.load_default(size=20)
                title_font = ImageFont.load_default(size=24)
        
        # Draw edges first with arrows
        for u, v in G.edges():
            x1, y1 = graph_pos[u]
            x2, y2 = graph_pos[v]
            x1, y1 = start_x + x1, start_y + y1
            x2, y2 = start_x + x2, start_y + y2
            draw_arrow(draw, x1, y1, x2, y2, fill_color='#1a1a1a', width=4)
        
        # Draw nodes
        for i, node in enumerate(nodes):
            x, y = graph_pos[node]
            x, y = start_x + x, start_y + y
            importance = scores_norm[i]
            radius = 20 + importance * 30  # Smaller size range: 20-50 pixels
            
            # Draw circle with strong contrast
            draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], 
                        fill=color, outline='#000000', width=4)
            
            # Draw node label with LARGE BOLD font
            bbox = draw.textbbox((0, 0), node, font=large_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text((x - text_width//2, y - text_height//2), node, fill='#000000', font=large_font)
        
        # Draw title with larger font
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_height = bbox[3] - bbox[1]
        draw.text((start_x + 25, start_y - 60), title, fill='#000000', font=title_font)
    
    # Draw all three graphs
    draw_graph(draw, pos, pr_norm, 40, 200, graph_width, graph_height, 
               "PageRank (Influence)", '#ff9999')
    draw_graph(draw, pos, auth_norm, 40 + graph_width + 40, 200, graph_width, graph_height, 
               "Authority (Trusted)", '#99ff99')
    draw_graph(draw, pos, hub_norm, 40 + 2*(graph_width + 40), 200, graph_width, graph_height, 
               "Hub (Connector)", '#ffff99')
    
    # Draw main title with MUCH LARGER font
    try:
        main_title_font = ImageFont.truetype("arial.ttf", 48)
    except:
        try:
            main_title_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 48)
        except:
            main_title_font = ImageFont.load_default(size=28)
    
    try:
        subtitle_font = ImageFont.truetype("arial.ttf", 32)
    except:
        try:
            subtitle_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 32)
        except:
            subtitle_font = ImageFont.load_default(size=20)
    
    main_title = "Network Analysis: PageRank vs HITS Authority vs HITS Hub"
    bbox = draw.textbbox((0, 0), main_title, font=main_title_font)
    title_width = bbox[2] - bbox[0]
    draw.text(((total_width - title_width) // 2, 20), main_title, fill='#000000', font=main_title_font)
    
    # Add subtitle
    subtitle = "Node Size = Metric Score (Larger = More Important)"
    bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = bbox[2] - bbox[0]
    draw.text(((total_width - subtitle_width) // 2, 85), subtitle, fill='#333333', font=subtitle_font)
    
    img.save('network_combined_importance.png', quality=95)
    print("Visualization saved as 'network_combined_importance.png'")
    
    # Generate individual graphs for each metric
    print("\nGenerating individual metric graphs...")
    
    # PageRank graph
    img_pr = Image.new('RGB', (900, 800), color='white')
    draw_pr = ImageDraw.Draw(img_pr)
    
    try:
        font_pr = ImageFont.truetype("arial.ttf", 28)
        title_font_pr = ImageFont.truetype("arial.ttf", 36)
    except:
        try:
            font_pr = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 28)
            title_font_pr = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 36)
        except:
            font_pr = ImageFont.load_default(size=20)
            title_font_pr = ImageFont.load_default(size=24)
    
    # Draw PageRank edges with arrows
    for u, v in G.edges():
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        draw_arrow(draw_pr, x1, y1, x2, y2, fill_color='#1a1a1a', width=4)
    
    # Draw PageRank nodes
    for i, node in enumerate(nodes):
        x, y = pos[node]
        importance = pr_norm[i]
        radius = 18 + importance * 32
        draw_pr.ellipse([(x - radius, y - radius), (x + radius, y + radius)], 
                       fill='#ff6b6b', outline='#000000', width=3)
        bbox = draw_pr.textbbox((0, 0), node, font=font_pr)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw_pr.text((x - text_width//2, y - text_height//2), node, fill='#000000', font=font_pr)
    
    bbox = draw_pr.textbbox((0, 0), "PageRank - Global Network Influence", font=title_font_pr)
    title_width = bbox[2] - bbox[0]
    draw_pr.text(((900 - title_width) // 2, 20), "PageRank - Global Network Influence", fill='#000000', font=title_font_pr)
    
    img_pr.save('network_pagerank.png', quality=95)
    print("PageRank graph saved as 'network_pagerank.png'")
    
    # Authority graph
    img_auth = Image.new('RGB', (900, 800), color='white')
    draw_auth = ImageDraw.Draw(img_auth)
    
    for u, v in G.edges():
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        draw_arrow(draw_auth, x1, y1, x2, y2, fill_color='#1a1a1a', width=4)
    
    for i, node in enumerate(nodes):
        x, y = pos[node]
        importance = auth_norm[i]
        radius = 18 + importance * 32
        draw_auth.ellipse([(x - radius, y - radius), (x + radius, y + radius)], 
                         fill='#66bb6a', outline='#000000', width=3)
        bbox = draw_auth.textbbox((0, 0), node, font=font_pr)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw_auth.text((x - text_width//2, y - text_height//2), node, fill='#000000', font=font_pr)
    
    bbox = draw_auth.textbbox((0, 0), "Authority - Trusted Sources (HITS)", font=title_font_pr)
    title_width = bbox[2] - bbox[0]
    draw_auth.text(((900 - title_width) // 2, 20), "Authority - Trusted Sources (HITS)", fill='#000000', font=title_font_pr)
    
    img_auth.save('network_authority.png', quality=95)
    print("Authority graph saved as 'network_authority.png'")
    
    # Hub graph
    img_hub = Image.new('RGB', (900, 800), color='white')
    draw_hub = ImageDraw.Draw(img_hub)
    
    for u, v in G.edges():
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        draw_arrow(draw_hub, x1, y1, x2, y2, fill_color='#1a1a1a', width=4)
    
    for i, node in enumerate(nodes):
        x, y = pos[node]
        importance = hub_norm[i]
        radius = 18 + importance * 32
        draw_hub.ellipse([(x - radius, y - radius), (x + radius, y + radius)], 
                        fill='#ffc107', outline='#000000', width=3)
        bbox = draw_hub.textbbox((0, 0), node, font=font_pr)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw_hub.text((x - text_width//2, y - text_height//2), node, fill='#000000', font=font_pr)
    
    bbox = draw_hub.textbbox((0, 0), "Hub - Link Distributors (HITS)", font=title_font_pr)
    title_width = bbox[2] - bbox[0]
    draw_hub.text(((900 - title_width) // 2, 20), "Hub - Link Distributors (HITS)", fill='#000000', font=title_font_pr)
    
    img_hub.save('network_hub.png', quality=95)
    print("Hub graph saved as 'network_hub.png'")
    
except Exception as e:
    print(f"Error creating visualization: {e}")
    import traceback
    traceback.print_exc()

print("\nBackend Processing Complete.")

print("\nBackend Processing Complete.")
