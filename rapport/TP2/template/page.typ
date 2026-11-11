// template\page.typ

// #import "header.typ": header
// #import "footer.typ": footer

#let setup-page(body) = {
  set page(
    paper: "a4",
    margin: (
      top: 2.2cm,
      bottom: 2.2cm,
      left: 2.5cm,
      right: 2.5cm,
    ),
    // header: header,
    // footer: footer
  )
  set heading(numbering: "1.")
  set text(
    font: "New Computer Modern", // "Times New Roman"
    size: 11pt,
    lang: "fr",
    hyphenate: false, // empêche la coupure automatique des mots
  )
  set par(
    justify: true,
    leading: 0.55em,
  )
  body
}

#let footer = context [
  #grid(
    columns: (1fr, auto, 1fr),
    align: horizon,
    align(left)[
      //#image("", height: 20pt)
    ],
    align(center)[
      -- #counter(page).display() --
    ],
    align(right)[
      //#image("", height: 20pt)
    ],
  )
]

