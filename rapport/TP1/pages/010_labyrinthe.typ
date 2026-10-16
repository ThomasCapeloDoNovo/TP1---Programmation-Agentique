#heading(level: 1)[Labyrinthe]

#heading(level: 2)[Modélisation]
Le problème du labyrinthe consiste à trouver un chemin entre un point de départ et un point d'arrivée dans un labyrinthe représenté par une grille. Chaque cellule de la grille peut être soit libre, soit occupée par un mur, soit un obstacle de poids compris entre 2 et 9. Le but est de se déplacer à travers les cellules pour atteindre l'objectif.

Un état est représenté par la position actuelle de l'agent dans le labyrinthe. À chaque étape, l'agent peut se déplacer vers une cellule adjacente (haut, bas, gauche, droite) si cette cellule est libre ou si elle contient un obstacle. 

Le coût du déplacement est de 1 pour une cellule libre et égal au poids de l'obstacle pour une cellule occupée par un obstacle.

#heading(level: 2)[Heuristique]
Pour l'heuristique, nous avons choisi d'utiliser la *distance de Manhattan*. Cette heuristique est admissible car elle ne surestime jamais le coût réel pour atteindre l'objectif.

$
h(s) =   |x_a - x_g| + |y_a - y_g|
$

Avec ($x_a$, $y_a$) représentant les coordonnées de l'agent AUSSI et ($x_g$, $y_g$) représentant les coordonnées de l'objectif.
Puisque le coût minimal d'une étape est de 1 (case libre) et que les obstacles ont des poids $>= 2$, la distance de Manhattan calculée avec un coût unitaire reste strictement inférieure ou égale au coût réel ($h(s) <= h^*(s)$).

#heading(level: 2)[Comparaison des algorithmes]

Instance 1 : Facile

#context {
  set text(size: 10pt)

  table(
    columns: 8,

    [Algorithme], [Mode], [Coût total], [Profondeur], [Nœuds générés], [Nœuds expansés], [Max OPEN], [Temps (ms)],

    [BFS], [Tree], [12], [12], [32 507], [14 901], [17 606], [37.0],
    [BFS], [Graph], [12], [12], [37], [34], [3], [0.1],

    [UCS], [Tree], [12], [12], [32 507], [14 901], [17 606], [35.1],
    [UCS], [Graph], [12], [12], [37], [34], [3], [0.1],

    [Greedy], [Tree], [12], [12], [26], [12], [14], [< 0.1],
    [Greedy], [Graph], [12], [12], [15], [12], [3], [< 0.1],

    [A\*], [Tree], [12], [12], [26], [12], [14], [< 0.1],
    [A\*], [Graph], [12], [12], [15], [12], [3], [< 0.1],
  )
}

Instance 2 : Avec un piège sur une des cases du chemin optimal

#context {
  set text(size: 10pt)

  table(
    columns: 8,

    [Algorithme], [Mode], [Coût total], [Profondeur], [Nœuds générés], [Nœuds expansés], [Max OPEN], [Temps (ms)],

    [BFS], [Tree], [20], [12], [32 507], [14 901], [17 606], [35.9],
    [BFS], [Graph], [20], [12], [37], [34], [3], [0.1],

    [UCS], [Tree], [#text(red)[N/A]], [#text(red)[N/A]], [209 424], [100 000], [109 424], [327.3],
    [UCS], [Graph], [16], [16], [41], [39], [4], [0.1],

    [Greedy], [Tree], [20], [12], [26], [12], [14], [0.1],
    [Greedy], [Graph], [20], [12], [15], [12], [3], [< 0.1],

    [A\*], [Tree], [16], [16], [154], [66], [88], [0.1],
    [A\*], [Graph], [16], [16], [22], [18], [4], [< 0.1],
  )
}

Ces résultats mettent en évidence l'efficacité de la distance de Manhattan pour guider la recherche dans le labyrinthe, tout en soulignant l'impact du choix du mode de recherche et de la prise en compte du coût des actions.

Le mode Tree Search montre très rapidement ses limites sur une grille pourtant simple. En raison de la présence de boucles et d'allers-retours possibles entre les cellules adjacentes, les algorithmes sans mémorisation des états visités subissent une explosion combinatoire. Sur l'instance avec piège, UCS et BFS en Tree Search atteignent la limite fixée à 100 000 nœuds expansés ou génèrent des dizaines de milliers de nœuds inutiles. À l'inverse, le passage en Graph Search élimine immédiatement toutes les redondances : le nombre de nœuds expansés chute drastiquement.

L'instance avec un piège illustre le comportement de chaque algorithme face à des coûts non uniformes. BFS et Greedy trouvent une solution avec un coût sous-optimal car ils franchissent l'obstacle pénalisant. En revanche, UCS et $A^*$ parviennent à contourner le piège pour garantir la solution optimale. $A^*$ s'impose comme le choix le plus performant, réussissant à trouver ce chemin optimal en expansant deux fois moins de nœuds que UCS.

