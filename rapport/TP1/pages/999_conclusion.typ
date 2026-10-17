#heading(level: 1)[Conclusion]

Ce travail a permis de concevoir et d'évaluer l'agent AUSSI, démontrant la faisabilité et la puissance d'un moteur de recherche complètement découplé de la formulation des problèmes. À travers une interface abstraite unifiée.

L'analyse comparative menée sur l'ensemble des instances met en évidence trois points majeurs :

- *L'indispensable apport du Graph Search* : La mémorisation des états déjà visités s'avère cruciale. Dans les espaces d'états structurés avec des cycles ou des chemins redondants, le mode Tree Search conduit quasi systématiquement à une explosion combinatoire ou à des retours de limite de sécurité. Le mode Graph Search permet d'élaguer les branches dupliquées et de maintenir la taille de la frontière OPEN à un niveau minimal.
- *Le passage à l'échelle grâce aux heuristiques* : Les algorithmes non informés (BFS et UCS) montrent très vite leurs limites dès que la taille du problème augmente. L'introduction d'heuristiques informées permet à Greedy et $A^*$ de guider la recherche et de réduire le nombre de nœuds explorés de plusieurs ordres de grandeur, résolvant en quelques millisecondes des instances inaccessibles à la recherche aveugle.
- *La supériorité de $A^*$ comme compromis optimal* : Si l'algorithme Greedy offre une vitesse d'exécution élevée, il reste vulnérable aux coûts d'étapes non uniformes et aux pièges. Combiné à une heuristique admissible en mode Graph Search, l'algorithme $A^*$ s'impose comme la stratégie la plus performante : il garantit l'optimalité de la solution tout en explorant un nombre de nœuds bien inférieur à celui de UCS.

En conclusion, la combinaison de l'algorithme $A^*$ et du mode Graph Search constitue la stratégie de référence d'AUSSI. Ce travail illustre l'un des principes fondamentaux de l'intelligence artificielle agentique : la séparation nette entre un moteur de raisonnement généraliste et la modélisation spécifique du domaine via les états, les coûts et les heuristiques.
