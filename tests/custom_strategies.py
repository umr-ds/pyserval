"""Custom hypothesis strategies"""

from hypothesis.strategies import text, characters

unicode_printable = text(characters(blacklist_categories=('Cc', 'Cs')))

ascii_lower_case = characters(min_codepoint=97, max_codepoint=122)
ascii_upper_case = characters(min_codepoint=64, max_codepoint=90)
ascii_digits = characters(min_codepoint=48, max_codepoint=57)

ascii_alphanum = characters(
    max_codepoint=122,
    whitelist_categories=('Lu', 'Ll', 'Nd')
)
