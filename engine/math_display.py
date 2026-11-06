"""Render arithmetic fractions as stacked LaTeX in learner-facing text.

Conservative by design: never reinterpret URLs, dates, plain prose or existing
LaTeX. Generated mathematics is also instructed to use explicit stacked notation.
"""
import re

# A single basic algebraic token or a parenthesised algebraic expression.
_ATOM = r'(?:\([^()\n]+\)|[+-]?(?:\d+(?:\.\d+)?(?:[a-zA-Z])?|[a-zA-Z](?:\^\d+)?))'
_FRACTION = re.compile(rf'(?<![\w/.:])(?P<num>{_ATOM})\s*/\s*(?P<den>{_ATOM})(?![\w/])')
_LATEX_FRACTION = re.compile(r'(?<!\\)\\(?:dfrac|tfrac|frac)\s*\{')

def _latex_atom(atom):
    atom=atom.strip()
    if atom.startswith('(') and atom.endswith(')'):
        return atom[1:-1].strip()
    return atom

def stacked_fractions(text):
    """Convert recognisable slash fractions, preserving nonmath and code/URLs.

    Returns Streamlit-compatible Markdown containing LaTeX display fractions.
    More complex algebra must be emitted as LaTeX by the generator itself.
    """
    if not isinstance(text,str) or '/' not in text:
        return text
    # Keep code, links and LaTeX delimiters intact. Rewrite slash fractions
    # within existing math as well, leaving already stacked fractions alone.
    protected = re.compile(r'(```[\s\S]*?```|`[^`\n]*`|\$\$[\s\S]*?\$\$|(?<!\$)\$(?!\$)[^$\n]*\$(?!\$)|https?://\S+|\[[^\]]+\]\([^)]*\))')
    chunks=[]; cursor=0
    for match in protected.finditer(text):
        chunks.append(_replace_segment(text[cursor:match.start()]))
        token=match.group()
        if token.startswith('$$') and token.endswith('$$'):
            chunks.append('$$'+_replace_segment(token[2:-2],wrap=False)+'$$')
        elif token.startswith('$') and token.endswith('$'):
            chunks.append('$'+_replace_segment(token[1:-1],wrap=False)+'$')
        else:
            chunks.append(token)
        cursor=match.end()
    chunks.append(_replace_segment(text[cursor:]))
    return ''.join(chunks)

def _replace_segment(segment, wrap=True):
    def convert(match):
        a,b=match.group('num'),match.group('den')
        # Slash-delimited numbers that look like dates should not be rewritten.
        if re.match(r'^\d{1,2}$',a) and re.match(r'^\d{1,2}$',b):
            tail=segment[match.end():]
            if tail.startswith('/') and re.match(r'^/\d{2,4}\b',tail):
                return match.group()
        # Avoid regular expressions such as 'and/or'.
        frac='\\dfrac{' + _latex_atom(a) + '}{' + _latex_atom(b) + '}'
        return ('$'+frac+'$') if wrap else frac
    return _FRACTION.sub(convert,segment)
