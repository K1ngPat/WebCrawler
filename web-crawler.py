import requests
from bs4 import BeautifulSoup
import urllib.parse as uparse
import time
import getopt, sys  


def get_links(url): 
# This function searches for certain tags and gets their href/src attributes as appropriate. Returns array of links.
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
# This function checks externsion of a url path to determine filetype.
    o = uparse.urlparse(url).path
    
    for j in ["html", "css", "jpg", "jpeg", "png", "js", "pdf", "php"]:
        if o[-len(j):] == j:
            if o[-(len(j)+1)] == '.':
                return j
        
    return "misc"


def sort_urls(visited_urls):
    """
    Sorts urls visited by both level of recursion and file type.
    Used dictionaries as it is easier (in other functions) to refer to the filetypes by their extensions than indices.
    """
    for i in range(len(visited_urls)):
        for j in range(len(visited_urls[i])):
            visited_urls[i][j] = (visited_urls[i][j], typurl(visited_urls[i][j]))

    sorts = { (lvl+1): {i:[visited_urls[lvl][j][0] for j in range(len(visited_urls[lvl])) if visited_urls[lvl][j][1]==i] for i in ["html", "css", "jpg", "jpeg", "png", "js", "pdf", "php", "misc"]} for lvl in range(len(visited_urls))}

    return sorts


def print_from_sorted(sorts):
    """
    Takes a sorted dict of urls, as outputted by previous function, and returns a string in the required output format.
    """

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
    """
    The core crawling logic. 
    Returns an array of URLs visited along with the recursion level at which we found them.
    Also returns an array of directional edges for the graph functionality.
    Note: Every .strip(" ") is to avoid whitespaces in output
    """
    visited = [[] for _ in range(depth)] # Stores links we have already visited
    queue = [[url, 0, None]]        # Stores links we have found but not visited yet
    edges = []      # Stores edges (links from webpage A to webpage B)

    while queue:  # Continues until completely recursed
        while True:
            current_url, current_depth, fath = queue.pop(0) 
            # Take out the oldest link not followed yet. (Breadth-first recursion)


            if current_url[4] != 's': # Used to avoid https webpages
                break
            elif len(queue) == 0:
                break
        
        if current_depth > 0:  # We are now visiting current_url
            visited[current_depth-1].append(current_url.strip(" "))

        if current_url[4] == 's': # Avoid https link being last link recursed, avoided above check.
            break

        if current_depth < depth:
            time.sleep(0.01)        # Necessary to ensure that requests do not get mixed, runs into many bugs when this line is skipped
            links = get_links(current_url)          # Get links from this page
            for link in links:
                absolute_url = uparse.urljoin(current_url, link).strip(" ")         # URL parsing
                if absolute_url.strip(" ")[:10] == "javascript":            # to avoid javascript:void(0) from showing up as links
                    continue
                if current_url.strip(" ") != absolute_url.strip(" "):       # Disregard self-linking
                    edges.append((current_url.strip(" "), absolute_url.strip(" ")))         # Add edge for graph

                new = True          
                # Holder variable to check if we've seen this URL before. Next 2 loops do that. 
                # Repeated links was an issue that took quit some time to fix.
                for k in range(depth):
                    if absolute_url.strip(" ") in visited[k]:
                        new = False
                        break
                
                for pq in queue:
                    if absolute_url.strip(" ") == pq[0]:
                        new = False

                if new:
                    if uparse.urlparse(absolute_url).hostname != uparse.urlparse(url).hostname:
                        # print("external detected") # This was used during debugging, this if is activated in case of external links.
                        visited[current_depth].append(absolute_url.strip(" "))
                    else:
                        queue.append([absolute_url.strip(" "), current_depth + 1, current_url.strip(" ")])

    return visited, edges


def plot_site_graph(edges):         # used to plot the site graph.
    import networkx as nx
    import matplotlib.pyplot as plt

    labeled = []            # Not all nodes will be labelled, as that will make graph VERY crowded

    for i in range(len(edges)):
        labeled.append(edges[i][0])             # Only nodes that have children will be labelled. 
                                                # This prevents numerous tiny files from being labelled, and mostly labels pages


    G = nx.DiGraph()

    G.add_edges_from(edges)     # Create graph. Check networkx documentation for details.

    pos = nx.spring_layout(G)      # Settled on spring layout because it gives prettiest results

    nx.draw(G, pos, with_labels=False, node_color='lightblue', node_size=800, arrowsize=20) # with_labels false because we dont want to label all

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

args, _ = getopt.getopt(argumentList, "u:t:o:g") # check getopt documentation for details

for i, j in args: # used to get command line arguments

    if i == "-u":
        head_url = j

    elif i == "-t":
        dep = int(j)

    elif i == "-o":
        outfile = j

    elif i == "-g":
        to_draw = True

# Next to if cases are error handling. Ends script in such cases.

if head_url == "":
    print("ERROR: No url given.")
    sys.exit()

if dep<=0:
    print("ERROR: Invalid threshold, must be positive integer.")
    sys.exit()


vtdurls, gredge = crawl(head_url, depth=dep)  # Actual using of the functions defined above.
stsurl = sort_urls(vtdurls)
outstring = print_from_sorted(stsurl)

if outfile == None:         # When no file is given
    print(outstring)

else:                       # Writing to file
    with open(outfile, "w") as text_file:
        text_file.write(outstring)


if to_draw:         # Drawing graph
    plot_site_graph(gredge)


# Thank you for reading this code!