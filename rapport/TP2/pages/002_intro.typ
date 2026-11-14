#heading(level: 1)[Introduction]

Ce travail est réalisé dans le cadre du cours 8INF878 – Intelligence artificielle agentique. Son objectif est de concevoir AUSSI V3 (_Agent Universel de Support Super Intelligent_), qui fait suite à AUSSI V2, fruit du Travail No. 1. 

Désormais, AUSSI doit être capable de jouer à des jeux à deux joueurs et à tours alternés. AUSSI aura ici le choix entre le Tic Tac Toe et le Puissance 4 (Connect 4), chacun jouable en utilisant un moteur basé sur le Minimax ou sur la méthode MCTS (Monte Carlo Tree Search).

Ce rapport se basera plus sur ces différents jeux et les moteurs utilisés plutôt que sur l'architecture générale et l'organisation du code de notre projet. Pour retrouver ces informations, vous pouvez vous referrer au rapport du Travail No. 1.

#heading(level: 1)[Architecture des moteurs]

Les deux moteurs sont écrits de façon générique : ils ne connaissent aucun jeu en particulier et communiquent uniquement avec l'interface abstraite `Game`. Chaque moteur est un agent dont la méthode `get_move(game, state)` retourne l'action choisie. Pour ajouter un jeu, il suffit d'écrire une sous-classe de `Game`, sans modifier les algorithmes de décision.

Tous les jeux héritent de la classe abstraite `Game`, qui définit le contrat commun utilisé par les moteurs. Elle impose de définir :

- `initial_state()` : l'état initial du jeu ;
- `player_to_move(s)` : le joueur qui doit jouer dans l'état `s` ;
- `actions(s)` : la liste des actions légales depuis l'état `s` ;
- `result(s, a)` : l'état obtenu en appliquant l'action `a` ;
- `is_terminal(s)` : indique si l'état `s` correspond à une fin de partie ;
- `winner(s)` : retourne le joueur gagnant, ou `None` en l'absence de gagnant ;
- `utility(s, player)` : retourne l'utilité exacte d'un état terminal du point de vue du joueur donné : `+1` pour une victoire, `-1` pour une défaite et `0` pour une partie nulle.

La classe fournit également `is_legal(s, a)` pour vérifier la légalité d'une action, `evaluate(s, player)` pour estimer la qualité d'un état non terminal et `display(s)` pour afficher un état dans la console.

Un état représente la configuration complète du jeu à un instant donné. Il doit être hashable afin de pouvoir être utilisé dans des structures de données adaptées à la recherche. De plus, `result(s, a)` doit produire un nouvel état sans modifier celui reçu en paramètre. Ainsi, les moteurs peuvent explorer différentes suites de coups sans altérer l'état réel de la partie.

Il est important de distinguer l'utilité exacte d'un état terminal de l'évaluation heuristique d'un état non terminal. L'utilité permet de reconnaître une victoire, une défaite ou une partie nulle. L'évaluation heuristique estime plutôt la qualité d'une position lorsque la recherche ne peut pas aller jusqu'à la fin de la partie. Cette séparation permet notamment à Minimax de prendre en compte les résultats réels lorsqu'ils sont connus, tout en utilisant une estimation lorsque la profondeur maximale est atteinte.

#heading(level: 2)[Minimax]

Le moteur Minimax (`MinimaxAgent`) explore l'arbre de jeu en supposant que les deux joueurs jouent de manière optimale : le joueur courant cherche à maximiser l'évaluation de l'état, son adversaire à la minimiser. Trois mécanismes le rendent utilisable sur des jeux dont l'arbre est trop grand pour être exploré entièrement.

*Élagage alpha-bêta.* On propage deux bornes : $alpha$, la meilleure valeur déjà garantie pour MAX, et $beta$, la meilleure valeur déjà garantie pour MIN. Dès qu'un nœud MAX obtient une valeur $v >= beta$, ou qu'un nœud MIN obtient $v <= alpha$, les actions restantes sont ignorées, car, en théorie, l'adversaire n'autoriserait jamais d'atteindre ce nœud. Le résultat est identique à celui du Minimax classique, mais plus efficace.

*Fonction d'évaluation.* L'exploration s'arrête quand l'état est terminal ou quand la profondeur restante atteint 0. L'état est alors évalué par `eval_fn(état, joueur)`, par défaut la méthode `evaluate` du jeu. Cette heuristique est toujours calculée du point de vue du joueur à la racine, que l'on maximise aux nœuds MAX et que l'on minimise aux nœuds MIN. Chaque jeu fournit la sienne (voir les sections suivantes).

*Approfondissement itératif (IDS) et limite de temps.* Le moteur lance successivement des recherches de profondeur 1, 2, …, `max_depth`. Une limite de temps (`time_limit`, 2 s par défaut) est vérifiée à chaque nœud : si elle est dépassée, une exception interrompt la recherche en cours et on conserve le meilleur coup de la dernière profondeur terminée. L'agent répond donc toujours dans le temps imparti. Le meilleur coup de la profondeur $d-1$ est de plus essayé en premier à la profondeur $d$, ce qui améliore l'élagage, puisque alpha-bêta est d'autant plus efficace que les bons coups sont examinés tôt. Les jeux peuvent aussi fournir leurs actions dans un ordre favorable : le Puissance 4 renvoie les colonnes du centre vers les bords.

L'agent expose sur l'interface la dernière profondeur complétée, le nombre de nœuds explorés et le temps de recherche.

#heading(level: 2)[Monte Carlo Tree Search]

Le moteur MCTS n'utilise aucune heuristique : il estime la valeur d'un coup à partir de parties jouées au hasard jusqu'à leur terme. Il construit progressivement un arbre dont chaque nœud mémorise son nombre de visites $n$ et la somme $W$ des récompenses obtenues. Tant que le temps imparti (`time_limit`) n'est pas écoulé, il répète quatre phases :

+ *Sélection* : depuis la racine, on descend dans l'arbre tant que le nœud courant est entièrement développé et non terminal, en choisissant l'enfant qui maximise la borne UCT : $ "UCT" = W / n + C sqrt(ln N / n) $ où $N$ est le nombre de visites du parent et $C$ la constante d'exploration (1 par défaut). Le premier terme favorise les coups qui ont bien réussi (exploitation), le second ceux qui ont été peu essayés (exploration). Aux nœuds où c'est l'adversaire qui joue, la moyenne est inversée, car il choisit le pire coup pour l'agent.
+ *Expansion* : on tire au hasard une action non encore essayée du nœud sélectionné et on crée l'enfant correspondant.
+ *Simulation* : à partir du nouvel état, les deux joueurs jouent des coups aléatoires jusqu'à une position terminale. La récompense vaut $+1$ si le joueur à la racine gagne, $-1$ s'il perd et $0$ pour un match nul.
+ *Rétropropagation* : la récompense remonte jusqu'à la racine, en incrémentant les visites et en cumulant la valeur de chaque nœud traversé.

À la fin du temps imparti, le coup joué est celui de l'enfant de la racine le plus visité (la valeur moyenne départage les égalités), ce qui est plus robuste que de prendre la meilleure moyenne. L'agent expose le nombre d'itérations réalisées et le temps de recherche.

Contrairement au Minimax, MCTS dépend du nombre de simulations réalisables dans le temps imparti.

