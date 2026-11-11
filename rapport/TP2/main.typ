// main.typ

#import "template/page.typ": footer, setup-page
#import "template/styles.typ": setup-styles
#show: setup-page
#show: setup-styles
#include "template/styles.typ"

#include "pages/000_cover.typ"

#set page(
  footer: footer,
)

#counter(page).update(1)

#include "pages/001_outline.typ"
#include "pages/002_intro.typ"

#include "pages/010_tic_tac_toe.typ"
#include "pages/011_connect4.typ"

#include "pages/999_conclusion.typ"
