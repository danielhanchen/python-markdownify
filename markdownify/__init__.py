from bs4 import BeautifulSoup, NavigableString, Comment, Doctype
# from textwrap import fill
import re


convert_heading_re = re.compile(r'convert_h(\d+)')
line_beginning_re = re.compile(r'^', re.MULTILINE)
whitespace_re = re.compile(r'[\t ]+')
all_whitespace_re = re.compile(r'[\s]+')
html_heading_re = re.compile(r'^h[1-6]')


# Heading styles
ATX = 'atx'
ATX_CLOSED = 'atx_closed'
UNDERLINED = 'underlined'
SETEXT = UNDERLINED

# Newline style
SPACES = 'spaces'
BACKSLASH = 'backslash'

# Strong and emphasis style
ASTERISK = '*'
UNDERSCORE = '_'


def chomp(text):
    """
    If the text in an inline tag like b, a, or em contains a leading or trailing
    space, strip the string and return a space as suffix of prefix, if needed.
    This function is used to prevent conversions like
        <b> foo</b> => ** foo**
    """
    prefix = ' ' if text.startswith(' ') else ''
    suffix = ' ' if text.endswith  (' ') else ''
    text = text.strip()
    return prefix, suffix, text


def abstract_inline_conversion(markup):
    """
    This abstracts all simple inline tags like b, em, del, ...
    Returns a function that wraps the chomped text in a pair of the string
    that is returned by markup_fn. markup_fn is necessary to allow for
    references to self.strong_em_symbol etc.
    """
    def implementation(el, text, convert_as_inline):
        # markup = markup_fn(self)
        prefix, suffix, text = chomp(text)
        if not text: return ''
        return f'{prefix}{markup}{text}{markup}{suffix}'
    return implementation


# def _todict(obj):
#     return dict((k, getattr(obj, k)) for k in dir(obj) if not k.startswith('_'))


is_nested_node_set = frozenset(['ol', 'ul', 'li',
                                'table', 'thead', 'tbody', 'tfoot',
                                'tr', 'td', 'th'])
# Remove whitespace-only textnodes in purely nested nodes
def is_nested_node(el):
    return el and el.name in is_nested_node_set

def escape(text):
    if not text:
        return ''
    #if self.options['escape_asterisks']:
    text = text.replace('*', r'\*')
    #if self.options['escape_underscores']:
    text = text.replace('_', r'\_')
    return text

def indent(text, level):
    return line_beginning_re.sub('\t' * level, text) if text else ''
    
def underline(text, pad_char):
    text = (text or '').rstrip()
    return f'{text}\n{pad_char * len(text)}\n\n' if text else ''


class MarkdownConverter(object):
    def __init__(self):
        return

    def convert(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # return self.convert_soup(soup)
        return MarkdownConverter.process_tag(soup, convert_as_inline=False, children_only=True)

    @staticmethod
    def process_tag(node, convert_as_inline, children_only=False):
        text = ''

        # markdown headings or cells can't include
        # block elements (elements w/newlines)
        node_name = node.name
        isHeading = html_heading_re.match(node_name) is not None
        isCell = node_name == "td" or node_name == "th"
        convert_children_as_inline = convert_as_inline

        if not children_only and (isHeading or isCell):
            convert_children_as_inline = True

        # Remove whitespace-only textnodes in purely nested nodes
        if is_nested_node(node):
            for el in node.children:
                # Only extract (remove) whitespace-only text node if any of the
                # conditions is true:
                # - el is the first element in its parent
                # - el is the last element in its parent
                # - el is adjacent to an nested node
                can_extract = (not el.previous_sibling
                               or not el.next_sibling
                               or is_nested_node(el.previous_sibling)
                               or is_nested_node(el.next_sibling))
                if (isinstance(el, NavigableString)
                        and el.strip() == ''
                        and can_extract):
                    el.extract()

        # Convert the children first
        for el in node.children:
            if isinstance(el, (Comment, Doctype)):
                continue
            elif isinstance(el, NavigableString):
                text += MarkdownConverter.process_text(el)
            else:
                text += MarkdownConverter.process_tag(el, convert_children_as_inline)

        if not children_only:
            node_name = node.name
            if (convert_fn := getattr(MarkdownConverter, f'convert_{node_name}', None)):
            # if convert_fn and self.should_convert_tag(node_name):
                text = convert_fn(node, text, convert_as_inline)

        return text

    @staticmethod
    def process_text(el):
        text = el or ''

        # dont remove any whitespace when handling pre or code in pre
        el_parent = el.parent
        el_parent_name = el_parent.name
        el_next_sibling = el.next_sibling
        if not (el_parent_name == 'pre'
                or (el_parent_name == 'code'
                    and el_parent.parent.name == 'pre')):
            text = whitespace_re.sub(' ', text)

        if el_parent_name != 'code' and el_parent_name != 'pre':
            text = escape(text)

        # remove trailing whitespaces if any of the following condition is true:
        # - current text node is the last node in li
        # - current text node is followed by an embedded list
        if (el_parent_name == 'li'
                and (not el_next_sibling
                     or el_next_sibling.name == "ul" or el_next_sibling.name == "ol")):
            text = text.rstrip()

        return text

    @staticmethod
    def convert_h1(el, text, convert_as_inline): return MarkdownConverter.convert_hn(1, el, text, convert_as_inline)
    @staticmethod
    def convert_h2(el, text, convert_as_inline): return MarkdownConverter.convert_hn(2, el, text, convert_as_inline)
    @staticmethod
    def convert_h3(el, text, convert_as_inline): return MarkdownConverter.convert_hn(3, el, text, convert_as_inline)
    @staticmethod
    def convert_h4(el, text, convert_as_inline): return MarkdownConverter.convert_hn(4, el, text, convert_as_inline)
    @staticmethod
    def convert_h5(el, text, convert_as_inline): return MarkdownConverter.convert_hn(5, el, text, convert_as_inline)
    @staticmethod
    def convert_h6(el, text, convert_as_inline): return MarkdownConverter.convert_hn(6, el, text, convert_as_inline)

    @staticmethod
    def convert_a(el, text, convert_as_inline):
        prefix, suffix, text = chomp(text)
        if not text:
            return ''
        href  = el.get('href')
        title = el.get('title')
        # For the replacement see #29: text nodes underscores are escaped
        # if (self.options['autolinks']
        #         and text.replace(r'\_', '_') == href
        #         and not title
        #         and not self.options['default_title']):
        if (text.replace(r'\_', '_') == href and not title):
            # Shortcut syntax
            return f'<{href}>'
        # if self.options['default_title'] and not title:
        #     title = href
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        return f'{prefix}[{text}]({href}{title_part}){suffix}' if href else text

    # convert_b = abstract_inline_conversion(lambda self: 2 * self.options['strong_em_symbol'])
    convert_b = staticmethod(abstract_inline_conversion(2 * ASTERISK))

    @staticmethod
    def convert_blockquote(el, text, convert_as_inline):

        if convert_as_inline:
            return text

        return f'\n{line_beginning_re.sub("> ", text)}\n\n' if text else ''

    @staticmethod
    def convert_br(el, text, convert_as_inline):
        if convert_as_inline:
            return ""

        # if self.options['newline_style'].lower() == BACKSLASH:
        #     return '\\\n'
        # else:
        #     return '  \n'
        return '  \n'

    _converter = staticmethod(abstract_inline_conversion('`'))

    @staticmethod
    def convert_code(el, text, convert_as_inline):
        if el.parent.name == 'pre':
            return text
        return MarkdownConverter._converter(el, text, convert_as_inline)

    convert_del = staticmethod(abstract_inline_conversion('~~'))

    # convert_em = abstract_inline_conversion(lambda self: self.options['strong_em_symbol'])
    convert_em = staticmethod(abstract_inline_conversion(ASTERISK))

    convert_kbd = convert_code

    @staticmethod
    def convert_hn(n, el, text, convert_as_inline):
        if convert_as_inline:
            return text

        # style = self.options['heading_style'].lower()
        style = UNDERLINED
        text = text.rstrip()
        # if style == UNDERLINED and n <= 2:
        if n <= 2:
            line = '=' if n == 1 else '-'
            return underline(text, line)
        hashes = '#' * n
        # if style == ATX_CLOSED:
        #     return '%s %s %s\n\n' % (hashes, text, hashes)
        return f'{hashes} {text}\n\n'

    @staticmethod
    def convert_hr(el, text, convert_as_inline):
        return '\n\n---\n\n'

    convert_i = convert_em

    @staticmethod
    def convert_img(el, text, convert_as_inline):
        alt = el.attrs.get('alt', None) or ''
        src = el.attrs.get('src', None) or ''
        title = el.attrs.get('title', None) or ''
        title_part = ' "%s"' % title.replace('"', r'\"') if title else ''
        # if (convert_as_inline
        #         and el.parent.name not in self.options['keep_inline_images_in']):
        if convert_as_inline:
            return alt

        return f'![{alt}]({src}{title_part})'

    @staticmethod
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
            return f'\n{indent(text, 1).rstrip()}'
        return "%s%s" % (text, ('\n' if before_paragraph else ''))

    convert_ul = convert_list
    convert_ol = convert_list

    @staticmethod
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

    @staticmethod
    def convert_p(el, text, convert_as_inline):
        if convert_as_inline:
            return text
        # if self.options['wrap']:
        #     text = fill(text,
        #                 width=self.options['wrap_width'],
        #                 break_long_words=False,
        #                 break_on_hyphens=False)
        return f"{text if text else ''}\n\n"

    @staticmethod
    def convert_pre(el, text, convert_as_inline):
        if not text:
            return ''
        # code_language = self.options['code_language']
        code_language = el['class'][0] if el.has_attr('class') else ""

        # if self.options['code_language_callback']:
        #     code_language = self.options['code_language_callback'](el) or code_language

        return f'\n```{code_language}\n{text}\n```\n'

    convert_s = convert_del

    convert_strong = convert_b

    convert_samp = convert_code

    # convert_sub = abstract_inline_conversion(lambda self: self.options['sub_symbol'])
    convert_sub = staticmethod(abstract_inline_conversion(""))

    # convert_sup = abstract_inline_conversion(lambda self: self.options['sup_symbol'])
    convert_sup = staticmethod(abstract_inline_conversion(""))

    @staticmethod
    def convert_table(el, text, convert_as_inline):
        return f'\n\n{text}\n'

    @staticmethod
    def convert_td(el, text, convert_as_inline):
        return f' {text} |'

    @staticmethod
    def convert_th(el, text, convert_as_inline):
        return f' {text} |'

    @staticmethod
    def convert_tr(el, text, convert_as_inline):
        cells = el.find_all(("td", "th",))
        is_headrow = all(cell.name == 'th' for cell in cells)
        overline = ''
        underline = ''
        el_parent = el.parent
        if is_headrow and not el.previous_sibling:
            # first row and is headline: print headline underline
            # underline += '| ' + ' | '.join(['---'] * len(cells)) + ' |' + '\n'
            underline = f"{underline}| {' | '.join(['---'] * len(cells))} |\n"
        elif (not el.previous_sibling
              and (el_parent.name == 'table'
                   or (el_parent.name == 'tbody'
                       and not el_parent.previous_sibling))):
            # first row, not headline, and:
            # - the parent is table or
            # - the parent is tbody at the beginning of a table.
            # print empty headline above this row
            # overline += '| ' + ' | '.join([''] * len(cells)) + ' |' + '\n'
            overline = f"{overline}| {' | '.join([''] * len(cells))} |\n"
            # overline += '| ' + ' | '.join(['---'] * len(cells)) + ' |' + '\n'
            overline = f"{overline}| {' | '.join(['---'] * len(cells))} |\n"
        return f"{overline}|{text}\n{underline}"

def markdownify(html):
    return MarkdownConverter().convert(html)
