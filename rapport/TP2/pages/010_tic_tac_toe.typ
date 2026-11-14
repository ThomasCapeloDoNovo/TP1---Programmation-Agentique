#heading(level: 1)[Tic Tac Toe]

#heading(level: 2)[Modélisation]

Le Tic Tac Toe se joue sur une grille de 3×3 cases où deux joueurs posent chacun leur tour un jeton dans une case vide, e premier qui aligne trois jetons gagne. Voici la modélisation que nous avons mis en place :

- *État* : un tuple de 3 tuples d'entiers (0 pour une case vide, 1 ou 2 pour les jetons des joueurs).
- *Joueur courant* : il est déduit de l'état en comptant les jetons : si les deux joueurs en ont posé autant, c'est le joueur 1 qui joue, sinon c'est le joueur 2.
- *Actions* : le couple `(ligne, colonne)` de chaque case vide.
- *Résultat* : une copie de la grille dans laquelle on rajoute le jeton joué par le joueur.
- *Test de fin* : on vérifie les 8 lignes possible et on retourne le gagnant s'il existe, un match nul si la grille est pleine, sinon la partie continue.

*Fonction d'évaluation.* Elle est calculée du point de vue d'un joueur $J$ et somme deux composantes. Les jetons de l'adversaire comptent négativement avec un facteur 1,01 : l'évaluation est ainsi légèrement pessimiste, ce qui évite d'attribuer la même valeur à des positions que l'on souhaite départager.

+ *Composante positionnelle* : chaque jeton rapporte le poids de sa case, 4 pour le centre, 3 pour les coins et 2 pour les côtés, ce qui reflète le nombre de lignes gagnantes passant par chaque case.
+ *Composante par ligne* : pour chacune des 8 lignes, si elle ne contient que des jetons de $J$ (ou que des jetons adverses), on ajoute (ou retire) un poids selon le nombre de jetons : 10 pour un, 100 pour deux et 100 000 pour trois, c'est-à-dire une victoire. Une ligne contenant des jetons des deux joueurs ne peut plus être gagnée et est ignorée.

Le grand poids d'un alignement complet garantit que, lorsque la recherche atteint une position gagnante, celle-ci domine.

#heading(level: 2)[Comparaison des algorithmes]

Il y a au plus $9! = 362 880$ séquences de coups au Tic Tac Toe, l'arbre de jeu est donc assez petit. Minimax avec une profondeur de 9 le parcourt entièrement (en moyenne 14 000 nœuds par coup face à un joueur aléatoire) et ne perd jamais. Pour comparer les moteurs, nous avons fait jouer 10 parties par confrontation, en alternant le joueur qui commence. Les paramètres sont : Minimax avec une profondeur maximale de 9 (ou de 2 pour la recherche courte) et 2 s par coup, et MCTS avec 1 s par coup, soit environ 20 000 itérations par coup.

#figure(
  table(
    columns: 5,
    align: (left, right, right, right, right),
    [*Confrontation*], [*Parties*], [*Victoires du 1er algorithme*], [*Victoires du 2e algorithme*], [*Nuls*],
    [Minimax (prof. 9) contre aléatoire], [10], [10], [0], [0],
    [MCTS (1 s) contre aléatoire], [10], [10], [0], [0],
    [Minimax (prof. 9) contre Minimax (prof. 9)], [10], [0], [0], [10],
    [Minimax (prof. 9) contre MCTS (1 s)], [10], [0], [0], [10],
    [Minimax (prof. 2) contre MCTS (1 s)], [10], [0], [0], [10],
    [MCTS (1 s) contre MCTS (1 s)], [10], [0], [0], [10],
  ),
  caption: [Résultats des confrontations au Tic Tac Toe],
)

On observe que :

- Les deux moteurs battent largement un joueur aléatoire.
- Les confrontations Minimax/Minimax, Minimax/MCTS et MCTS/MCTS donnent toujours des égalités, néanmoins dans le cas Minimax/MCTS, Minimax pourrait gagner si MCTS avait un temps de reflexion plus petit. Car les évaluations de MCTS sont basées sur le hasard.
- Même une recherche Minimax très courte (profondeur 2) suffit à égaliser face à MCTS, grâce à l'évaluation qui valorise le centre et les alignements.

Les résultats sont issus d'un petit nombre de parties et sont donc indicatifs. Le Tic Tac Toe est trop simple pour départager les moteurs.
