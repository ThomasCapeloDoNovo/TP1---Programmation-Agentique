#heading(level: 1)[Connect Four]

#heading(level: 2)[Modélisation]

Le Puissance 4 se joue sur une grille de 6 lignes et 7 colonnes. Les joueurs déposent à tour de rôle un jeton dans une colonne, le jeton tombe à la case libre la plus basse. Le premier qui aligne quatre jetons (horizontalement, verticalement ou en diagonale) gagne (si la grille est pleine, la partie est nulle). Le jeu est bien plus grand que le Tic Tac Toe : l'arbre de jeu compte plusieurs milliers de milliards de positions, et aucun moteur ne peut l'explorer en entier dans un temps raisonnable.

- *État* : un tuple de 6 tuples de 7 entiers (0 pour vide, 1 ou 2 pour les joueurs), la case $(0, 0)$ étant en haut à gauche.
- *Joueur courant* : déduit du nombre de jetons posés, le joueur 1 commence.
- *Actions* : l'indice des colonnes dont la case du haut est vide. Elles sont retournées dans l'ordre 3, 4, 2, 5, 1, 6, 0, c'est-à-dire du centre vers les bords. Les coups centraux sont en général meilleurs car ils participent à plus d'alignements possibles ; les examiner en premier augmente le nombre de coupes de l'élagage alpha-bêta.
- *Résultat* : la gravité est simulée en cherchant, depuis le bas, la première case vide de la colonne choisie.
- *Test de fin* : on cherche un alignement de quatre jetons dans les quatre directions ; la partie est nulle si la ligne du haut est entièrement remplie.

*Fonction d'évaluation.* Comme au Tic Tac Toe, elle est calculée du point de vue d'un joueur $J$, et les termes adverses sont multipliés par 1,01. Elle somme deux composantes :

+ *Fenêtres de quatre cases* (horizontales et diagonales) : toutes les fenêtres sont générées une seule fois. Une fenêtre contenant des jetons des deux joueurs est ignorée. Sinon elle rapporte un poids selon le nombre de jetons du même joueur : 0 pour un, 100 pour deux, 1 000 pour trois et 100 000 pour quatre (victoire). Le poids est ajouté si la fenêtre appartient à $J$ et retiré si elle appartient à l'adversaire.
+ *Colonnes (alignements verticaux)* : pour ch aque colonne, on regarde la pile de jetons de même couleur au sommet ($n$ jetons) et le nombre de cases libres au-dessus. Si $n$ plus les cases libres permet encore d'atteindre quatre, la colonne a un potentiel et rapporte le poids correspondant à $n$. Une pile d'un seul jeton rapporte un poids lié à sa colonne, `[2, 6, 9, 16, 9, 6, 2]`, qui favorise le centre.

#heading(level: 2)[Comparaison des algorithmes]

Le Puissance 4 est le jeu où les différences entre moteurs apparaissent. Voici les confrontations réalisées, en alternant le joueur qui commence. Les parties de Minimax sont limitées à 0,5 s par coup (profondeur maximale 7) et celles de MCTS à 0,3 s ou 0,5 s par coup.

#figure(
  table(
    columns: 5,
    align: (left, right, right, right, right),
    [*Confrontation*], [*Parties*], [*Victoires du 1er moteur*], [*Victoires du 2e moteur*], [*Nuls*],
    [Minimax (prof. 7, 0,5 s) contre aléatoire], [8], [8], [0], [0],
    [MCTS (0,3 s) contre aléatoire], [8], [8], [0], [0],
    [Minimax (prof. 7, 0,5 s) contre MCTS (0,5 s)], [8], [8], [0], [0],
    [Minimax (prof. 3, 0,5 s) contre MCTS (0,5 s)], [6], [5], [1], [0],
    [Minimax (prof. 5) contre Minimax (prof. 2)], [4], [2], [2], [0],
  ),
  caption: [Résultats des confrontations au Puissance 4],
)

Les statistiques d'exploration montrent la limite des moteurs :

- Avec 0,5 s par coup, Minimax termine en moyenne la profondeur 5,4 sur une profondeur maximale demandée de 7, en explorant environ 3 800 nœuds. L'approfondissement itératif garantit une réponse dans le temps imparti, mais la profondeur atteinte dépend de la vitesse de la machine.
- MCTS réalise environ 500 itérations en 0,3 s, ce qui est peu pour un arbre aussi large, et ses simulations sont faites avec des coups totalement aléatoires.

On en retient que :

- Les deux moteurs battent facilement un joueur aléatoire.
- Face à MCTS, Minimax avec une profondeur suffisante l'emporte à chaque partie. L'évaluation heuristique (centre, alignements) lui donne une connaissance du jeu que MCTS ne peut pas reconstituer avec si peu de simulations. Même limité à une profondeur 3, Minimax gagne 5 parties sur 6, ce qui montre que la qualité de la fonction d'évaluation compte autant que la profondeur.
- Le duel Minimax (profondeur 5) contre Minimax (profondeur 2) est partagé : les deux moteurs étant déterministes, chacun gagne lorsqu'il joue dans une certaine configuration. Une plus grande profondeur n'assure donc pas toujours la victoire, surtout lorsque l'heuristique n'est pas parfaite.

Comme pour le Tic Tac Toe, ces résultats reposent sur un nombre limité de parties et doivent être interprétés comme des tendances. Avec davantage de temps de calcul (ou une implémentation plus rapide), MCTS profiterait davantage du nombre de simulations, alors que Minimax gagnerait en profondeur.
