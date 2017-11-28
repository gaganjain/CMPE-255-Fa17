import requests, re, sys
import networkx as nx
from bs4 import BeautifulSoup, SoupStrainer

def surfer(root, n):
    """
        links, G = surfer(root, n)
    Build a graph of web pages by recursively visiting sites,
    starting with the provided root url. Stop when the number of
    nodes in the graph reaches n.

    Links are filtered by the valid_href function to exclude
    specified strings.
    """
    nodes = [root]
    bad_links = []

    G = nx.DiGraph()
    G.add_node(root)
    for i in range(n):
        link = nodes[i]

        sys.stdout.write('\r')
        sys.stdout.write("[%-20s] %d%%" % ('='*int(i*20/n), i*100/n))
        sys.stdout.flush()

        try:
            page_links = get_valid_links(link)
        except:
            bad_links.append(link)
            print('bad link: ', link)
            nodes.remove(link)
            continue

        new_nodes = list(set(page_links) - set(nodes))
        nodes.extend(list(set(new_nodes))) # add unique new links
        G.add_nodes_from(new_nodes)

        new_edges = [(link,l) for l in page_links]
        G.add_edges_from(new_edges)

    G.remove_nodes_from(nodes[n:])
    return nodes[:n], G

def get_valid_links(url):
    """
    Return list of links contained in given url. Uses valid_href()
    to exclude links that contain certain strings.
    """
    try:
        r = requests.get(url)
    except:
        raise

    soup = BeautifulSoup(r.text, "lxml", parse_only=SoupStrainer('a'))
    atags = soup.find_all(a_with_href)
    hrefs = [a.get('href') for a in atags]
    hrefs = list(filter(None, hrefs)) # remove empty links
    hrefs = [url + s if s[0] == '/' else s for s in hrefs] # replace / with root url
    hrefs = [s.rstrip("/") for s in hrefs] # remove trailing /
    return list(filter(lambda h : valid_href(h), hrefs))

def a_with_href(tag):
    return tag.name == 'a' and tag.has_attr('href')

def valid_href(href):
    """
    Returns False if href is not an absolute link (beginning with http://),
     or if href contains any of the strings in skip_list.
     Returns True otherwise.
    """
    link_regexp = re.compile(r"http://[^\"|<|>|;|'|)| ]+")
    skip_list = [".gif",".jpg",".jpeg",".pdf",".css",".js",".asp",".mwc",".ram",
        "lmscadsi","cybernet","w3.org","google","yahoo",
        "scripts","netscape","shockwave","webex","fansonly","!","?",
        ".png",".svg","myfonts.com"]
    skip = any([s in href for s in skip_list])
    return bool(link_regexp.search(href)) and not skip
