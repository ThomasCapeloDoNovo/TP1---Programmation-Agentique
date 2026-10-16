#heading(level: 1)[N-Puzzle]

#heading(level: 2)[Modélisation]
Le N-Puzzle (aussi connu sous le nom de "Taquin") est un petit jeu où le but est de recréer une image fractionnée et mélangée en plusieurs cases. La plupart des taquins vendus sont de taille 3x3 mais il est possible d'augmenter la taille comme bon vous semble. Ici, nous testerons AUSSI sur 3 instances : 3x3, 4x4 et 5x5. 

Un état est un plateau de tuiles représenté par un tuple de tuples de nombres, représentant chacun la position de leur tuile. Cette représentation très visuelle permet de comparer avec le plateau goal assez facilement.

A chaque étape, AUSSI a le choix de déplacer la case vide vers le haut, le bas, à gauche ou à droite (si possible), et de déplacer la tuile concernée. Le but étant de retrouver le plateau goal.

Chaque déplacement a un coût de 1.

#heading(level: 2)[Heuristique]
Pour l'heuristique, nous avons décidé d'utiliser la *distance de Manhattan*. 
L'heuristique estime le nombre de déplacement qu'il reste avant d'atteindre l'état goal, en calculant pour chaque tuile la distance de Manhattan entre sa position actuelle et sa position dans l'état goal.

$
h(s) = sum_(t in T) (
  |r_s(t) - r_g(t)| + |c_s(t) - c_g(t)|
)
$
où T représente l'ensemble des tuiles, $r_s$ et $c_s$ la position actuelle de la tuile et, $r_g$ et $c_g$ la position goal de la tuile


#heading(level: 2)[Comparaison des algorithmes]

Instance 3x3
#context {
  set text(size: 10pt)

  table(
    columns: 8,

    [Algorithme], [Mode], [Coût total], [Profondeur], [Nœuds générés], [Nœuds expansés], [Max OPEN], [Temps (ms)],

    [BFS], [Tree], [#text(red)[N/A]], [#text(red)[N/A]], [849935], [300000\*], [549935], [5036],
    [BFS], [Graph], [20], [20], [74203], [55408], [18858], [1273],

    [UCS], [Tree], [#text(red)[N/A]], [#text(red)[N/A]], [849935], [300000\*], [549935], [5061],
    [UCS], [Graph], [20], [20], [74203], [55408], [18858], [652],

    [Greedy], [Tree], [#text(red)[N/A]], [#text(red)[N/A]], [879586], [300000\*], [579586], [7170],
    [Greedy], [Graph], [62], [62], [1047], [622], [413], [12],

    [A\*], [Tree], [20], [20], [12096], [4737], [7359], [75],
    [A\*], [Graph], [20], [20], [452], [282], [170], [3],
  )
}
\* Limite de noeuds expansés (300 000) atteinte, stop par sécurité.

Instance 4x4
#context {
  set text(size: 10pt)

  table(
    columns: 8,

    [Algorithme], [Mode], [Coût total], [Profondeur], [Nœuds générés], [Nœuds expansés], [Max OPEN], [Temps (ms)],

    [BFS], [Tree], [#text(red)[N/A]], [#text(red)[N/A]], [4344050], [1342381], [3001669], [30000\*],
    [BFS], [Graph], [#text(red)[N/A]], [#text(red)[N/A]], [2891601], [1505175], [1386426], [30000\*],

    [UCS], [Tree], [#text(red)[N/A]], [#text(red)[N/A]], [4811051], [1486692], [3324359], [30000\*],
    [UCS], [Graph], [#text(red)[N/A]], [#text(red)[N/A]], [2739545], [1425505], [1314040], [30000\*],

    [Greedy], [Tree], [#text(red)[N/A]], [#text(red)[N/A]], [2612550], [940285], [1672265], [30000\*],
    [Greedy], [Graph], [109], [109], [6712], [3240], [3431], [71],

    [A\*], [Tree], [#text(red)[N/A]], [#text(red)[N/A]], [2642549], [838717], [1803832], [30000\*],
    [A\*], [Graph], [39], [39], [67117], [33965], [33069], [830],
  )
}
\* Limite de temps (30s) atteinte, stop par sécurité.

Instance 5x5
#context {
  set text(size: 10pt)

  table(
    columns: 8,

    [Algorithme], [Mode], [Coût total], [Profondeur], [Nœuds générés], [Nœuds expansés], [Max OPEN], [Temps (ms)],

    [BFS], [Tree], [#text(red)[N/A]], [#text(red)[N/A]], [3815403], [1097785], [2717618], [30000\*],
    [BFS], [Graph], [#text(red)[N/A]], [#text(red)[N/A]], [2599705], [1177149], [1422556], [30000\*],

    [UCS], [Tree], [#text(red)[N/A]], [#text(red)[N/A]], [4404995], [1269705], [3135290], [30000\*],
    [UCS], [Graph], [#text(red)[N/A]], [#text(red)[N/A]], [2826946], [1282621], [1544325], [30000\*],

    [Greedy], [Tree], [#text(red)[N/A]], [#text(red)[N/A]], [2073682], [829472], [1244210], [30000\*],
    [Greedy], [Graph], [56], [56], [5733], [2472], [3199], [75],

    [A\*], [Tree], [#text(red)[N/A]], [#text(red)[N/A]], [2178969], [647533], [1531436], [30000\*],
    [A\*], [Graph], [22], [22], [26808], [11990], [14792], [364],
  )
}
\* Limite de temps (30s) atteinte, stop par sécurité.

Ces résultats nous montrent que l'heuristique joue un rôle clé dans la résolution du taquin. BFS et UCS ne trouvent souvent pas la solution en un temps résonnable, et lors de l'arrêt de la recherche, le nombre de noeuds explorés est énorme. Nous avons essayé de repousser au maximum les limites de temps et de mémoire pour les algorithmes BFS et UCS, mais aucune solution n'était trouvée, alors nous avons laissé les résultats sous 30s par soucis de lisibilité. Plus généralement, sur des instances au-delà de 3x3, il est vite compliqué d'obtenir une solution rapidement avec ces deux algorithmes.

Au contraire, Greedy et A\* s'en sortent très bien sur toutes les instances, en tout cas pour leur version Graph Search. On voit que dans ce problème, la version Tree Search a beaucoup plus de difficultés à trouver une solution. 

Enfin, on remarque assez bien que BFS et UCS donnent sensiblement les mêmes résultats, ce qui est tout à fait normal car les actions sont ici à coup unitaire. 