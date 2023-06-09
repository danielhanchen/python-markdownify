from bs4 import BeautifulSoup, NavigableString, Comment, Doctype
import re
WHITESPACE_RE    = re.compile(r'[\t ]+')
REMOVE_HTML_TAGS = re.compile("</?[a-z]{3,}[^>]{0,}>")
CHECK_CODY_CODE  = re.compile(r"^>?([^\s]{0,})(?:copy[\s]{0,}code)+", flags = re.IGNORECASE)

NEWLINE     = "\n"
TAB         = "\t"
PRE_TAG     = "<pre"
PRE_END_TAG = "</pre>"
IS_NESTED_NODE_SET = frozenset(('ol', 'ul', 'li', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'td', 'th',))

def convert_h1(el, text, convert_as_inline):
    text = text.strip() # [Fix newline start in header tags] (https://github.com/matthewwithanm/python-markdownify/pull/89)
    return f'{text}\n{"=" * len(text)}\n' if text else ""
pass

def convert_h2(el, text, convert_as_inline):
    text = text.strip() # [Fix newline start in header tags] (https://github.com/matthewwithanm/python-markdownify/pull/89)
    return f'{text}\n{"-" * len(text)}\n' if text else ""
pass

def convert_a(el, text, convert_as_inline):
    if not text: return ""
    prefix = " " if text[0]  == " " else ""
    suffix = " " if text[-1] == " " else ""
    if not (text := text.strip()): return ""

    el_get = el.get
    href  = el_get('href')
    title = el_get('title')
    if (text.replace(r'\_', '_') == href and not title):
        return f'<{href}>'

    title_part = ' "%s"' % title.replace('"', r'\"') if title else ""
    return f'{prefix}[{text}]({href}{title_part}){suffix}' if href else text
pass

def convert_b(el, text, convert_as_inline):
    if not text: return ""
    prefix = " " if text[0]  == " " else ""
    suffix = " " if text[-1] == " " else ""
    if not (text := text.strip()): return ""
    return f'{prefix}**{text}**{suffix}'
pass

def convert_code(el, text, convert_as_inline):
    if not text: return ""
    if el.parent.name == 'pre': return text
    prefix = " " if text[0]  == " " else ""
    suffix = " " if text[-1] == " " else ""
    if not (text := text.strip()): return ""
    return f'{prefix}`{text}`{suffix}'
pass

def convert_del(el, text, convert_as_inline):
    if not text: return ""
    prefix = " " if text[0]  == " " else ""
    suffix = " " if text[-1] == " " else ""
    if not (text := text.strip()): return ""
    return f'{prefix}~~{text}~~{suffix}'
pass

def convert_em(el, text, convert_as_inline):
    if not text: return ""
    prefix = " " if text[0]  == " " else ""
    suffix = " " if text[-1] == " " else ""
    if not (text := text.strip()): return ""
    return f'{prefix}*{text}*{suffix}'
pass

def convert_img(el, text, convert_as_inline):
    el_attrs_get = el.attrs.get
    alt   = el_attrs_get('alt',   None) or ""
    src   = el_attrs_get('src',   None) or ""
    title = el_attrs_get('title', None) or ""
    title_part = ' "%s"' % title.replace('"', r'\"') if title else ""
    if convert_as_inline: return alt
    return f'![{alt}]({src}{title_part})'
pass

def convert_list(el, text, convert_as_inline):
    # Converting a list to inline is undefined.
    # Ignoring convert_to_inline for list.
    nested = False
    before_paragraph = False
    el_next_sibling = el.next_sibling
    if el_next_sibling and el_next_sibling.name != "ul" and el_next_sibling.name != "ol":
        before_paragraph = True
    while el:
        if el.name == 'li':
            nested = True
            break
        el = el.parent
    if nested:
        # remove trailing newline if nested
        return f"\n{NEWLINE.join(f'{TAB}{x}' for x in text.split(NEWLINE)).rstrip() if text else ''}"
    return f"{text}{NEWLINE if before_paragraph else ''}"
pass

def convert_li(el, text, convert_as_inline):
    parent = el.parent
    if parent is not None and parent.name == 'ol':
        if parent.get("start"):
            start = int(parent.get("start"))
        else:
            start = 1
        bullet = f'{(start + parent.index(el))}.'
    else:
        depth = -1
        while el:
            if el.name == 'ul':
                depth += 1
            el = el.parent
        bullets = '*+-'
        bullet = bullets[depth % len(bullets)]
    return f"{bullet} {(text or '').strip()}\n"
pass

def convert_pre(el, text, convert_as_inline):
    if not text: return ""
    code_language = el['class'][0] if el.has_attr('class') else ""
    return f'\n```{code_language}\n{text}\n```\n'
pass

def convert_sub(el, text, convert_as_inline):
    if not text: return ""
    prefix = " " if text[0]  == " " else ""
    suffix = " " if text[-1] == " " else ""
    if not (text := text.strip()): return ""
    return f'{prefix}{text}{suffix}'
pass

def convert_tr(el, text, convert_as_inline):

    cells = el.find_all(("td", "th",))
    n = len(cells)
    el_parent = el.parent
    el_previous_sibling = el.previous_sibling
    overline  = ""
    underline = ""

    # [Support conversion of header rows in tables without th tag] (https://github.com/matthewwithanm/python-markdownify/pull/83)
    is_headrow = all(cell.name == "th" for cell in cells) \
                 or (not el_previous_sibling and not el_parent.name == "tbody") \
                 or (not el_previous_sibling and el_parent.name == "tbody" and len(el_parent.parent.find_all("thead")) < 1)

    if is_headrow and not el_previous_sibling:
        # first row and is headline: print headline underline
        underline = f"{underline}| {' | '.join(['---'] * n)} |\n"

    elif (not el_previous_sibling
          and (el_parent.name == 'table'
               or (el_parent.name == 'tbody'
                   and not el_parent.previous_sibling))):
        # first row, not headline, and:
        # - the parent is table or
        # - the parent is tbody at the beginning of a table.
        # print empty headline above this row
        overline = f"{overline}| {' | '*(n-1) if n != 0 else ''} |\n"
        overline = f"{overline}| {' | '.join(['---'] * n)} |\n"

    return f"{overline}|{text}\n{underline}"
pass

def convert_blockquote(el, text, convert_as_inline):
    if convert_as_inline or not text: return text
    text = text.strip() # [Strip text before adding blockquote markers] (https://github.com/matthewwithanm/python-markdownify/pull/76)
    return f"\n{NEWLINE.join(f'> {x}' for x in text.split(NEWLINE))}\n"
pass

FUNCTIONS = {
    "a"          : convert_a,
    "b"          : convert_b,
    "strong"     : convert_b,
    "code"       : convert_code,
    "kbd"        : convert_code,
    "samp"       : convert_code,
    "pre"        : convert_pre,
    "del"        : convert_del,
    "s"          : convert_del,
    "em"         : convert_em,
    "i"          : convert_em,
    "img"        : convert_img,
    "list"       : convert_list,
    "ul"         : convert_list,
    "ol"         : convert_list,
    "li"         : convert_li,
    "sub"        : convert_sub,
    "sup"        : convert_sub,
    "tr"         : convert_tr,
    "blockquote" : convert_blockquote,

    # [Fix newline start in header tags] (https://github.com/matthewwithanm/python-markdownify/pull/89)
    "h1"         : convert_h1,
    "h2"         : convert_h2,
    "h3"         : lambda el, text, c: text if c else    f'### {text.strip()}\n',
    "h4"         : lambda el, text, c: text if c else   f'#### {text.strip()}\n',
    "h5"         : lambda el, text, c: text if c else  f'##### {text.strip()}\n',
    "h6"         : lambda el, text, c: text if c else f'###### {text.strip()}\n',

    "hr"         : lambda el, text, c: '\n\n---\n\n',
    "table"      : lambda el, text, c: f'\n\n{text}\n',
    "td"         : lambda el, text, c: f' {text.strip()} |', # [Tables not converted well - paragraphs] (https://github.com/matthewwithanm/python-markdownify/issues/90)
    "th"         : lambda el, text, c: f' {text} |',
    "br"         : lambda el, text, c: ""   if c else "  \n",
    "p"          : lambda el, text, c: text if c else f"{text}\n",
}


def process_tag(node, convert_as_inline, children_only = False):
    text = ""
    # markdown headings or cells can't include
    # block elements (elements w/newlines)
    node_name = node.name
    isHeading = ("h1" <= node_name <= "h6")
    isCell = node_name == "td" or node_name == "th"
    convert_children_as_inline = convert_as_inline

    if not children_only and (isHeading or isCell):
        convert_children_as_inline = True

    # Remove whitespace-only textnodes in purely nested nodes
    if node_name in IS_NESTED_NODE_SET:
        for el in node.children:
            # Only extract (remove) whitespace-only text node if any of the
            # conditions is true:
            # - el is the first element in its parent
            # - el is the last element in its parent
            # - el is adjacent to an nested node

            el_previous_sibling = el.previous_sibling
            el_next_sibling     = el.next_sibling

            # Remove whitespace-only textnodes in purely nested nodes
            can_extract = (   not el_previous_sibling
                           or not el_next_sibling
                           or (el_previous_sibling and el_previous_sibling.name in IS_NESTED_NODE_SET)
                           or (el_next_sibling     and el_next_sibling    .name in IS_NESTED_NODE_SET))
            if (isinstance(el, NavigableString) and el.strip() == "" and can_extract):
                el.extract()

    # Convert the children first
    for el in node.children:
        if isinstance(el, (Comment, Doctype)):
            continue
        elif isinstance(el, NavigableString):
            text += process_text(el)
        else:
            text += process_tag(el, convert_children_as_inline)

    if not children_only:
        if (node_name := node.name) in FUNCTIONS:
            text = FUNCTIONS[node_name](node, text, convert_as_inline)

    return text
pass


def process_text(el):
    text = el or ""

    # dont remove any whitespace when handling pre or code in pre
    el_parent = el.parent
    el_parent_name = el_parent.name
    el_next_sibling = el.next_sibling
    if not (el_parent_name == 'pre'
            or (el_parent_name == 'code' and el_parent.parent.name == 'pre')):
        text = WHITESPACE_RE.sub(' ', text)

    if el_parent_name != 'code' and el_parent_name != 'pre':
        text = text.replace('_', r'\_').replace('*', r'\*')

    # remove trailing whitespaces if any of the following condition is true:
    # - current text node is the last node in li
    # - current text node is followed by an embedded list
    if (el_parent_name == 'li'
            and (not el_next_sibling
                 or el_next_sibling.name == "ul" or el_next_sibling.name == "ol")):
        text = text.rstrip()

    return text
pass


def markdownify(text):
    """ First cleanup code sections by deleting <span> <div> etc """
    i = 0
    while (code_start := text.find(PRE_TAG, i)) != -1:

        start = code_start + len(PRE_TAG)
        if (code_end := text.find(PRE_END_TAG, start)) == -1: break
        code = REMOVE_HTML_TAGS.sub("", text[start : code_end])

        """ Check if Copy Code exists """
        if (language := CHECK_CODY_CODE.match(code)):
            pre = f'<pre class="{language.group(1)}">'
            code = code[language.span(0)[1]:]
        else:
            pre = PRE_TAG
        pass

        text = f"{text[:code_start]}{pre}{code}{text[code_end:]}"
        i = code_start + len(pre) + len(code) + len(PRE_END_TAG)
    pass

    soup = BeautifulSoup(text, "html.parser")
    return process_tag(soup, convert_as_inline = False, children_only = True)
pass
