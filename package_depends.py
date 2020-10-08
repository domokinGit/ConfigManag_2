import io
import webbrowser
import xml.etree.ElementTree as ElTree
import zipfile
import re
from urllib.request import urlopen


def load(url):
    try:
        with urlopen(url) as f:
            data = f.read()
    except:
        return 0
    return data


def get_package_url(name):
    data = load("https://pypi.org/simple/%s/" % name)
    root = ElTree.fromstring(data)
    package_url = None
    for elem in root[1]:
        if elem.tag == "a":
            url = elem.attrib["href"]
            if ".whl#" in url:
                package_url = url
    return package_url


def get_package_deps(url):
    deps = []
    data = load(url)
    if not data == 0:
        obj = io.BytesIO(data)
        zipf = zipfile.ZipFile(obj)
        meta_path = [s for s in zipf.namelist() if "METADATA" in s][0]
        with zipf.open(meta_path) as f:
            meta = f.read().decode("utf-8")
        for line in meta.split("\n"):
            line = line.replace(";", " ").split()
            if not line:
                break
            if line[0] == "Requires-Dist:" and not "extra" in line:
                if (len(re.findall('\[|]', line[1])) > 0):
                    line[1] = re.split('\[|]', line[1])[1]
                deps.append(line[1])
        return deps
    return 0


def gv(graph):
    lines = "digraph{"
    for v1 in graph:
        for v2 in graph[v1]:
            if not v1 == v2:
                v1 = v1.replace('-', '_').replace('.', ',')  # graphviz ругается на тире и точки
                v2 = v2.replace('-', '_').replace('.', ',')
                lines += '%s->%s;' % (v1, v2)
    lines += "}"
    return lines


def get_graph(graph):
    # print(gv_text(graph))
    digraph = gv(graph)
    if len(graph) > 1:
        url = "https://quickchart.io/graphviz?graph=" + digraph  # можно использовать
        # https://dreampuf.github.io/GraphvizOnline
        webbrowser.open(url, new=2)


def gv_text(graph):
    lines = ["digraph{"]
    for v1 in graph:
        for v2 in graph[v1]:
            if not v1 == v2:
                v1 = v1.replace('-', '_').replace('.', ',')  # graphviz ругается на тире и точки
                v2 = v2.replace('-', '_').replace('.', ',')
                lines.append('%s->%s;' % (v1, v2))
    lines.append("}")
    return ("\n").join(lines)


def get_pypi_dic(name):
    graph = dict()
    draw_graph = {}

    def rec(name):
        print(name)
        graph[name] = dict(depends=[], conflicts=[])
        draw_graph[name] = set()
        url = get_package_url(name)
        deps = get_package_deps(url)
        if not deps == 0:
            for d in deps:
                draw_graph[name].add(d)
                graph[name]["depends"].append(d)
                if d not in graph:
                    rec(d)

    rec(name)
    get_graph(draw_graph)
    return graph
