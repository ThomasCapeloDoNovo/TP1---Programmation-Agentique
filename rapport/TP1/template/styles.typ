// template/styles.typ

#let orange-edf = rgb("#f36f21")
#let blue-edf = rgb("#0066cc")

#let setup-styles(doc) = [

  // Style des légendes de figures
  #show figure.caption: it => context [
    #v(0.15cm)
    #align(center)[
      #text(size: 9.5pt)[
        #text(fill: orange-edf, weight: "bold")[
          #it.supplement~#it.counter.display(it.numbering)
        ]
        #text(style: "italic", weight: "bold")[ -- ]
        #it.body
      ]
    ]
  ]

  // numérotation des notes de bas de page
  #set footnote(
    numbering: n => text(fill: blue-edf, weight: "bold")[[#numbering("1", n)]]
  )

  #set footnote.entry(
    separator: [
      #line(length: 30%, stroke: 0.5pt)
      #v(0.1cm)
    ],
    gap: 0.55em,
    indent: 0em,
  )

  // Style du texte des notes en bas de page
  #show footnote.entry: set text(size: 9pt)

  #doc
]
