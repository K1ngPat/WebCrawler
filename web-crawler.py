import requests
from bs4 import BeautifulSoup
import urllib.parse as uparse
import time
import getopt, sys  


def get_links(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            links.append(href)

    for link in soup.find_all('link'):
        href = link.get('href')
        if href:
            links.append(href)

    for link in soup.find_all('script'):
        href = link.get('src')
        if href:
            links.append(href)
    
    for link in soup.find_all('img'):
        href = link.get('src')
        if href:
            links.append(href)

    return links

def typurl(url):
    o = uparse.urlparse(url).path
    
    for j in ["html", "css", "jpg", "jpeg", "png", "js", "pdf", "php"]:
        if o[-len(j):] == j:
            if o[-(len(j)+1)] == '.':
                return j
        
    return "misc"


def sort_urls(visited_urls):
    for i in range(len(visited_urls)):
        for j in range(len(visited_urls[i])):
            visited_urls[i][j] = (visited_urls[i][j], typurl(visited_urls[i][j]))

    sorts = { (lvl+1): {i:[visited_urls[lvl][j][0] for j in range(len(visited_urls[lvl])) if visited_urls[lvl][j][1]==i] for i in ["html", "css", "jpg", "jpeg", "png", "js", "pdf", "php", "misc"]} for lvl in range(len(visited_urls))}

    return sorts


def print_from_sorted(sorts):

    opp = ""
    
    for i in range(len(sorts)):
        opp += f"\n\nAt recursion level {i+1}\n"
        fls = 0
        for j in ["html", "css", "jpg", "jpeg", "png", "js", "pdf", "php", "misc"]:
            fls += len(sorts[i+1][j])
        
        opp += f"Total files found: {fls}\n"

        for j in ["html", "css", "jpg", "jpeg", "png", "js", "pdf", "php", "misc"]:
            if len(sorts[i+1][j]) == 0:
                continue
            opp = opp + j + ": " + str(len(sorts[i+1][j])) + '\n'

            for k in sorts[i+1][j]:
                opp = opp + k + "\n"

    return opp



    


def crawl(url, depth=2):
    visited = [[] for _ in range(depth)]
    queue = [[url, 0, None]]
    edges = []

    while queue:
        while True:
            current_url, current_depth, fath = queue.pop(0) 
            if current_url[4] != 's':
                break
            elif len(queue) == 0:
                break
        
        if current_depth > 0:
            visited[current_depth-1].append(current_url.strip(" "))

        if current_url[4] == 's':
            break

        if current_depth < depth:
            time.sleep(0.01)
            links = get_links(current_url)
            for link in links:
                absolute_url = uparse.urljoin(current_url, link).strip(" ")
                if absolute_url.strip(" ")[:10] == "javascript":
                    continue
                if current_url.strip(" ") != absolute_url.strip(" "):
                    edges.append((current_url.strip(" "), absolute_url.strip(" ")))

                new = True
                for k in range(depth):
                    if absolute_url.strip(" ") in visited[k]:
                        new = False
                        break
                
                for pq in queue:
                    if absolute_url.strip(" ") == pq[0]:
                        new = False

                if new:
                    if uparse.urlparse(absolute_url).hostname != uparse.urlparse(url).hostname:
                        # print("external detected") # This was used during debugging
                        visited[current_depth].append(absolute_url.strip(" "))
                    else:
                        queue.append([absolute_url.strip(" "), current_depth + 1, current_url.strip(" ")])

    return visited, edges


def plot_site_graph(edges):
    import networkx as nx
    import matplotlib.pyplot as plt

    labeled = []

    for i in range(len(edges)):
        labeled.append(edges[i][0])


    G = nx.DiGraph()

    G.add_edges_from(edges)

    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=False, node_color='lightblue', node_size=800, arrowsize=20)

    # Labelling only select nodes
    node_labels = {node: node if node in labeled else "" for node in G.nodes}
    nx.draw_networkx_labels(G, pos, labels=node_labels)

    # Display the graph
    plt.show()


# # trial usage
# start_url = 'http://mahitgadhiwala.com/'
# visited_urls = crawl(start_url, depth=2)
# # print(len(visited_urls))
# # for nov in range(len(visited_urls)):
# #     print(f"\n\nDepth {nov+1}\n\n")
# #     for urls in visited_urls[nov]:
# #         print(urls)

# sts = sort_urls(visited_urls)
# print(print_from_sorted(sts))

head_url = None     # Variables to store terminal args
dep = None
outfile = None
to_draw = False

argumentList = sys.argv[1:]

args, _ = getopt.getopt(argumentList, "u:t:o:g")

for i, j in args:

    if i == "-u":
        head_url = j

    elif i == "-t":
        dep = int(j)

    elif i == "-o":
        outfile = j

    elif i == "-g":
        to_draw = True


vtdurls, gredge = crawl(head_url, depth=dep)
stsurl = sort_urls(vtdurls)
outstring = print_from_sorted(stsurl)

if outfile == None:
    print(outstring)

else:
    with open(outfile, "w") as text_file:
        text_file.write(outstring)


if to_draw:
    plot_site_graph(gredge)