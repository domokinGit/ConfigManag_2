import subprocess

packages = dict(
    a = dict(dependes=[["b"], ["c"], ["z"]], conflicts=[]),
    b = dict(dependes=[["d"]], conflicts=[]),
    c = dict(dependes=[["d", "e"], ["f", "g"]], conflicts=[]),
    d = dict(dependes=[], conflicts=["e", "g"]),
    e = dict(dependes=[], conflicts=[]),
    f = dict(dependes=[], conflicts=[]),
    g = dict(dependes=[], conflicts=[]),
    y = dict(dependes=[["z"]], conflicts=[]),
    z = dict(dependes=[], conflicts=[]),
)


def depend(x, ys):
    ys = " ".join(["%d" % y for y in ys])
    return "-%d %s" % (x, ys)


def conflict(x, y):
    return "-%d -%d" % (x, y)


def build_cnf(packages, installed):
    idx = dict((v, i + 1) for i, v in enumerate(packages))
    clauses = []
    for n in packages:
        i = idx[n]
        p = packages[n]
        if p["depends"]:
            for d in p["depends"]:
                clauses.append(depend(i, [idx[x] for x in d]) + " 0")
        if p["conflicts"]:
            for c in p["conflicts"]:
                clauses.append(conflict(i, idx[c] + " 0"))
    for n in installed:
        clauses.append("%d 0" % idx[n])
    return "\n".join(["p cnf %d %d" % (len(packages), len(clauses))] + clauses)


cnf = build_cnf(packages, ["a", "z"])
with open("packages.cnf", "w") as f:
    f.write(cnf)

subprocess.run(["minisat/minisat", "packages.cnf", "result.txt"])

with open("result.txt") as f:
    result = f.read();

result = result.split("\n")
if result[0] == "SAT":
    pkg = dict((i + 1, v) for i, v in enumerate(packages))
    for n in result[1].split():
        i = int(n)
        if i > 0:
            print(pkg[i])
        else:
            print("error!")
