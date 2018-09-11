"""Custom hypothesis strategies"""

from hypothesis.strategies import text, characters

unicode_printable = text(characters(blacklist_categories=('Cc', 'Cs')))

ascii_alphanum = characters(
    max_codepoint=122,
    whitelist_categories=('Lu', 'Ll', 'Nd')
)
