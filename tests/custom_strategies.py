"""Custom hypothesis strategies"""

from hypothesis.strategies import text, characters, binary, dictionaries

unicode_printable = text(characters(blacklist_categories=("Cc", "Cs")))

ascii_alpha = characters(max_codepoint=122, whitelist_categories=("Lu", "Ll"))

ascii_alphanum = characters(max_codepoint=122, whitelist_categories=("Lu", "Ll", "Nd"))

payloads = binary()

payloads_nonempty = binary(min_size=1)

custom_fields = dictionaries(keys=ascii_alpha, values=ascii_alphanum)
