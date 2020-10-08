import subprocess
from random import randint

from package_depends import get_pypi_dic


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
                clauses.append(depend(i, [idx[d]]) + " 0")
        if p["conflicts"]:
            for c in p["conflicts"]:
                clauses.append(conflict(i, idx[c]) + " 0")
    for n in installed:
        clauses.append("%d 0" % idx[n])
    return "\n".join(["p cnf %d %d" % (len(packages), len(clauses))] + clauses)


def check_conflicts(names):
    cnf = build_cnf(packages, names)
    with open("packages.cnf", "w") as f:
        f.write(cnf)

    subprocess.run(["minisat", "packages.cnf", "result.txt"])

    with open("result.txt") as f:
        result = f.read()

    result = result.split("\n")
    if result[0] == "SAT":
        pkg = dict((i + 1, v) for i, v in enumerate(packages))
        for n in result[1].split():
            i = int(n)
            if i > 0:
                print(pkg[i])
    else:
        print("error!")


def make_conflicts(deps):
    # print("////////////////Conflicts")
    depslist = list(deps.keys())  # достать ключи (пакеты)
    for i in range(0, len(depslist) - 1):  # пройтись по всем  пакетам
        has_conflicts = randint(0, 4)  # 25% шанс на конфликт
        if (has_conflicts == 2):
            parent = depslist[i]
            son = depslist[randint(0, len(deps.values()) - 1)]
            if son not in deps[parent]["depends"] and not (parent == son):  # добавление конфликта,
                deps[parent]["conflicts"].append(son)  # если элемент не является наследником или самим собой
                # print(parent + " and " + son)
    # print("////////////////Conflicts")


packages = get_pypi_dic("jupyter")  # достать словарь зависимостей
make_conflicts(packages)  # создать конфликты
names = ["qtconsole"]  # устанавливаемые пакеты
check_conflicts(names)  # проверка конфликтов
