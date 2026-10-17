#heading(level: 1)[Introduction]

Ce travail est réalisé dans le cadre du cours 8INF878 – Intelligence artificielle agentique. Son objectif est de concevoir AUSSI V2 (_Agent Universel de Support Super Intelligent_), un agent capable de résoudre des problèmes grâce à un moteur de résolution générique. Les algorithmes d'exploration ne changent jamais d'un problème à l'autre : seules la formulation du problème et, lorsque c'est nécessaire, son heuristique lui sont propres.

AUSSI résout quatre problèmes : le labyrinthe, la navigation entre villes, le N-Puzzle et le jeu arithmétique. Il dispose de quatre stratégies de recherche (BFS, UCS, Greedy et A\*), chacune utilisable en mode Tree Search ou Graph Search. Pour chaque résolution, il indique si une solution a été trouvée, la présente, et fournit son coût, sa profondeur ainsi que des statistiques d'exécution.

#heading(level: 1)[Architecture générale]

#heading(level: 2)[Organisation du code]

Le code est découpé en trois parties indépendantes. Ce découpage permet d'ajouter un problème ou une stratégie en modifiant peu de fichiers.

#context {
  set text(size: 10pt)

  table(
    columns: (auto, auto, 1fr),

    [Élément], [Rôle], [Contenu],

    [`src/`], [Moteur générique], [Interface `Problem`, stratégies de recherche, fonction `SEARCH`, boucle de l'agent `AGENT`. Cette partie ne connaît aucun problème en particulier.],

    [`problems/`], [Problèmes], [Une classe par problème (labyrinthe, N-Puzzle, jeu arithmétique, navigation), ses instances de test et un registre qui permet de les construire à partir de leur nom.],

    [`interface/`], [Interface utilisateur], [Interface graphique pygame : choix du problème, de l'instance, de la stratégie et du mode, puis affichage du résultat.],

    [`main.py`], [Point d'entrée], [Lance l'interface graphique, ou un affichage en console.],
  )
}

#heading(level: 2)[Formulation d'un problème]

Tous les problèmes héritent de la classe abstraite `Problem`, qui est la seule chose que connaît le moteur de recherche. Elle impose de définir :

- `actions(s)` : les actions légales depuis l'état $s$ ;
- `result(s, a)` : l'état obtenu en appliquant l'action $a$ ;
- `goal_test(s)` : vrai si $s$ est un état but ;
- `step_cost(s, a, s')` : le coût de l'action, égal à 1 par défaut ;
- `heuristic(s)` : l'estimation $h(s)$ du coût restant jusqu'au but.

L'état initial est donné à la construction du problème. Un état doit être hashable car le Graph Search l'utilise comme clé de dictionnaire.

#heading(level: 2)[Moteur de recherche]

La fonction `SEARCH(problem, strategy, mode)` implémente toutes les stratégies avec une seule boucle. Les nœuds, qui contiennent un état, leur parent, l'action qui y mène, le coût $g$ du chemin et la profondeur, sont stockés dans OPEN, une file de priorité. À chaque itération, AUSSI retire de OPEN le nœud de plus petite valeur $f(n)$, vérifie s'il s'agit du but, puis génère ses successeurs. Seule la fonction $f$ change d'une stratégie à l'autre :

#context {
  set text(size: 10pt)

  table(
    columns: (auto, auto),

    [Stratégie], [Priorité $f(n)$],

    [BFS], [profondeur du nœud],
    [UCS], [$g(n)$],
    [Greedy], [$h(n)$],
    [A\*], [$g(n) + h(n)$],
  )
}

En cas d'égalité, le nœud généré en premier est développé en premier. Le test du but est effectué lorsque le nœud est retiré de OPEN (et non lors de sa génération), ce qui garantit l'optimalité d'UCS et de A\* avec une heuristique admissible.

Le paramètre `mode` choisit entre les deux variantes d'une même boucle :

- *Tree Search* : aucun état n'est mémorisé. Un même état peut donc être généré plusieurs fois, et indéfiniment s'il existe des cycles.
- *Graph Search* : un dictionnaire retient, pour chaque état, le meilleur coût $g$ connu. Un état déjà connu avec un coût inférieur ou égal n'est pas ajouté à OPEN, et un chemin plus économique vers un état déjà rencontré remplace l'ancien.

Enfin, trois limites de sécurité (nombre de nœuds expansés, taille de OPEN et temps) permettent à AUSSI de s'arrêter lui-même lorsqu'une résolution risque de dépasser ses capacités. `SEARCH` retourne alors l'un des trois statuts suivants : _solution_ (un chemin a été trouvé), _aucune solution_ (tout l'espace d'états a été exploré) ou _limite atteinte_. Ce dernier cas ne prouve pas l'absence de solution : la recherche a simplement été interrompue.

