#heading(level: 1)[Navigation]

#heading(level: 2)[Modélisation]
Ici nous cherchons à ce qu'AUSSI se rende d'une ville à une autre, dans un graphe où les sommets sont des villes et les routes des arrêtes avec un poids (la distance en km)

Un état est la ville où se trouve AUSSI et chaque déplacement coûte la distance d'une route entre deux villes.
#heading(level: 2)[Heuristique]

L'heuristique est la distance euclidienne entre le point de départ et l'arrivée.

$h(n) = sqrt((x_n-x_A)^2+(y_n-y_A)^2)$

Avec nœud départ, $n=(x_n;y_n)$ et nœud arrivée, $A=(x_A;y_A)$

C'est une heuristique admissible si elle ne surestime jamais la coût minimal réel jusqu'au but : $h(n)<= h^*(n)$. Dans notre cas, chaque route pèse au moins autant que la distance à vol d’oiseau entre ses deux villes. Un chemin vers le but est une succession de routes : d’après l’inégalité triangulaire, la somme de leurs longueurs en ligne droite ne peut pas être plus petite que la distance directe entre $n$ et $A$, c’est-à-dire $h(n)$. Le coût réel d’un chemin est donc toujours supérieur ou égal à $h(n)$, ce qui donne $h(n) <= h^*(n)$. L’heuristique est bien admissible.


#heading(level: 2)[Comparaison des algorithmes]

Navigation en France de Lille à Marseille
#context {
  set text(size: 10pt)

  table(
    columns: 8,

    [Algorithme], [Mode], [Coût total], [Profondeur], [Nœuds générés], [Nœuds expansés], [Max OPEN], [Temps (ms)],

    [BFS], [Tree], [1005km], [3], [211], [47], [164], [1],
    [BFS], [Graph], [1005km], [3], [15], [11], [8], [$<$1],

    [UCS], [Tree], [975km], [4], [1182], [253], [929], [2],
    [UCS], [Graph], [975km], [4], [14], [11], [7], [$<$1],

    [Greedy], [Tree], [1005km], [3], [17], [3], [14], [$<$1],
    [Greedy], [Graph], [1005km], [3], [11], [3], [8], [$<$1],

    [A\*], [Tree], [975km], [4], [29], [6], [23], [$<$1],
    [A\*], [Graph], [975km], [4], [12], [5], [7], [$<$1],
  )
}

Le passage de Tree Search à Graph Search réduit fortement l’exploration. En Tree Search, les routes à double sens produisent des allers-retours, et un même état est regénéré de nombreuses fois : UCS génère 1182 nœuds, contre 14 en Graph Search. Le gain est le plus net pour BFS et UCS, qui n’utilisent pas l’heuristique et explorent toute la carte autour du départ.

Concernant les coûts totaux, UCS et $A*$ trouvent le chemin optimal (975 km, Lille → Reims → Dijon → Lyon → Marseille). BFS minimise le nombre de routes et non leur longueur, et Greedy ne tient pas compte du coût déjà parcouru : tous deux renvoient un chemin de 1005 km.

Greedy est l’algorithme qui explore le moins de nœuds (3 expansions), mais au prix d’une solution non optimale. $A*$ offre le meilleur compromis, il garantit l’optimalité et n’expanse que 5 nœuds en Graph Search, et 6 en Tree Search.