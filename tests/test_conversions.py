from markdownify import markdownify as md


def inline_tests(tag, markup):
    # test template for different inline tags
    assert md(f'<{tag}>Hello</{tag}>') == f'{markup}Hello{markup}'
    assert md(f'foo <{tag}>Hello</{tag}> bar') == f'foo {markup}Hello{markup} bar'
    assert md(f'foo<{tag}> Hello</{tag}> bar') == f'foo {markup}Hello{markup} bar'
    assert md(f'foo <{tag}>Hello </{tag}>bar') == f'foo {markup}Hello{markup} bar'
    assert md(f'foo <{tag}></{tag}> bar') in ['foo  bar', 'foo bar']  # Either is OK


def test_a():
    assert md('<a href="https://google.com">Google</a>') == '[Google](https://google.com)'
    assert md('<a href="https://google.com">https://google.com</a>') == '<https://google.com>'
    assert md('<a href="https://community.kde.org/Get_Involved">https://community.kde.org/Get_Involved</a>') == '<https://community.kde.org/Get_Involved>'
    # assert md('<a href="https://community.kde.org/Get_Involved">https://community.kde.org/Get_Involved</a>', autolinks=False) == '[https://community.kde.org/Get\\_Involved](https://community.kde.org/Get_Involved)'


def test_a_spaces():
    assert md('foo <a href="http://google.com">Google</a> bar') == 'foo [Google](http://google.com) bar'
    assert md('foo<a href="http://google.com"> Google</a> bar') == 'foo [Google](http://google.com) bar'
    assert md('foo <a href="http://google.com">Google </a>bar') == 'foo [Google](http://google.com) bar'
    assert md('foo <a href="http://google.com"></a> bar') == 'foo  bar'


def test_a_with_title():
    text = md('<a href="http://google.com" title="The &quot;Goog&quot;">Google</a>')
    assert text == r'[Google](http://google.com "The \"Goog\"")'
    # assert md('<a href="https://google.com">https://google.com</a>', default_title=True) == '[https://google.com](https://google.com "https://google.com")'


def test_a_shortcut():
    text = md('<a href="http://google.com">http://google.com</a>')
    assert text == '<http://google.com>'


# def test_a_no_autolinks():
#     assert md('<a href="https://google.com">https://google.com</a>', autolinks=False) == '[https://google.com](https://google.com)'


def test_b():
    assert md('<b>Hello</b>') == '**Hello**'


def test_b_spaces():
    assert md('foo <b>Hello</b> bar') == 'foo **Hello** bar'
    assert md('foo<b> Hello</b> bar') == 'foo **Hello** bar'
    assert md('foo <b>Hello </b>bar') == 'foo **Hello** bar'
    assert md('foo <b></b> bar') == 'foo  bar'


def test_blockquote():
    # [Strip text before adding blockquote markers] (https://github.com/matthewwithanm/python-markdownify/pull/76)
    assert md('<blockquote>Hello</blockquote>') == '\n> Hello\n'
    assert md('<blockquote>\nHello\n</blockquote>') == '\n> Hello\n'


def test_blockquote_with_nested_paragraph():
    # [Strip text before adding blockquote markers] (https://github.com/matthewwithanm/python-markdownify/pull/76)
    assert md('<blockquote><p>Hello</p></blockquote>') == '\n> Hello\n'
    assert md('<blockquote><p>Hello</p><p>Hello again</p></blockquote>') == '\n> Hello\n> Hello again\n'


def test_blockquote_with_paragraph():
    assert md('<blockquote>Hello</blockquote><p>handsome</p>') == '\n> Hello\nhandsome\n'


def test_blockquote_nested():
    # [Strip text before adding blockquote markers] (https://github.com/matthewwithanm/python-markdownify/pull/76)
    text = md('<blockquote>And she was like <blockquote>Hello</blockquote></blockquote>')
    assert text == '\n> And she was like \n> > Hello\n'


def test_br():
    assert md('a<br />b<br />c') == 'a  \nb  \nc'
    # assert md('a<br />b<br />c', newline_style=BACKSLASH) == 'a\\\nb\\\nc'


def test_code():
    inline_tests('code', '`')
    assert md('<code>this_should_not_escape</code>') == '`this_should_not_escape`'


def test_del():
    inline_tests('del', '~~')


def test_div():
    assert md('Hello</div> World') == 'Hello World'


def test_em():
    inline_tests('em', '*')


def test_header_with_space():
    # [Fix newline start in header tags] (https://github.com/matthewwithanm/python-markdownify/pull/89)
    assert md('<h3>\n\nHello</h3>') == '### Hello\n'
    assert md('<h4>\n\nHello</h4>') == '#### Hello\n'
    assert md('<h5>\n\nHello</h5>') == '##### Hello\n'
    assert md('<h5>\n\nHello\n\n</h5>') == '##### Hello\n'
    assert md('<h5>\n\nHello   \n\n</h5>') == '##### Hello\n'


def test_h1():
    assert md('<h1>Hello</h1>') == 'Hello\n=====\n'


def test_h2():
    assert md('<h2>Hello</h2>') == 'Hello\n-----\n'


def test_hn():
    assert md('<h3>Hello</h3>') == '### Hello\n'
    assert md('<h4>Hello</h4>') == '#### Hello\n'
    assert md('<h5>Hello</h5>') == '##### Hello\n'
    assert md('<h6>Hello</h6>') == '###### Hello\n'


# def test_hn_chained():
#     assert md('<h1>First</h1>\n<h2>Second</h2>\n<h3>Third</h3>', heading_style=ATX) == '# First\n\n\n## Second\n\n\n### Third\n\n'
#     assert md('X<h1>First</h1>', heading_style=ATX) == 'X# First\n\n'


# def test_hn_nested_tag_heading_style():
#     assert md('<h1>A <p>P</p> C </h1>', heading_style=ATX_CLOSED) == '# A P C #\n\n'
#     assert md('<h1>A <p>P</p> C </h1>', heading_style=ATX) == '# A P C\n\n'


def test_hn_nested_simple_tag():
    tag_to_markdown = [
        ("strong", "**strong**"),
        ("b", "**b**"),
        ("em", "*em*"),
        ("i", "*i*"),
        ("p", "p"),
        ("a", "a"),
        ("div", "div"),
        ("blockquote", "blockquote"),
    ]

    for tag, markdown in tag_to_markdown:
        assert md('<h3>A <' + tag + '>' + tag + '</' + tag + '> B</h3>') == '### A ' + markdown + ' B\n'

    # assert md('<h3>A <br>B</h3>', heading_style=ATX) == '### A B\n\n'

    # Nested lists not supported
    # assert md('<h3>A <ul><li>li1</i><li>l2</li></ul></h3>', heading_style=ATX) == '### A li1 li2 B\n\n'


def test_hn_nested_img():
    image_attributes_to_markdown = [
        ("", "", ""),
        ("alt='Alt Text'", "Alt Text", ""),
        ("alt='Alt Text' title='Optional title'", "Alt Text", " \"Optional title\""),
    ]
    for image_attributes, markdown, title in image_attributes_to_markdown:
        assert md('<h3>A <img src="/path/to/img.jpg" ' + image_attributes + '/> B</h3>') == '### A ' + markdown + ' B\n'
        # assert md('<h3>A <img src="/path/to/img.jpg" ' + image_attributes + '/> B</h3>', keep_inline_images_in=['h3']) == '### A ![' + markdown + '](/path/to/img.jpg' + title + ') B\n\n'


# def test_hn_atx_headings():
#     assert md('<h1>Hello</h1>', heading_style=ATX) == '# Hello\n\n'
#     assert md('<h2>Hello</h2>', heading_style=ATX) == '## Hello\n\n'


# def test_hn_atx_closed_headings():
#     assert md('<h1>Hello</h1>', heading_style=ATX_CLOSED) == '# Hello #\n\n'
#     assert md('<h2>Hello</h2>', heading_style=ATX_CLOSED) == '## Hello ##\n\n'


def test_head():
    assert md('<head>head</head>') == 'head'


def test_hr():
    assert md('Hello<hr>World') == 'Hello\n\n---\n\nWorld'
    assert md('Hello<hr />World') == 'Hello\n\n---\n\nWorld'
    assert md('<p>Hello</p>\n<hr>\n<p>World</p>') == 'Hello\n\n\n\n---\n\n\nWorld\n'


def test_i():
    assert md('<i>Hello</i>') == '*Hello*'


def test_img():
    assert md('<img src="/path/to/img.jpg" alt="Alt text" title="Optional title" />') == '![Alt text](/path/to/img.jpg "Optional title")'
    assert md('<img src="/path/to/img.jpg" alt="Alt text" />') == '![Alt text](/path/to/img.jpg)'


def test_kbd():
    inline_tests('kbd', '`')


def test_p():
    assert md('<p>hello</p>') == 'hello\n'
    assert md('<p>123456789 123456789</p>') == '123456789 123456789\n'
    # assert md('<p>123456789 123456789</p>', wrap=True, wrap_width=10) == '123456789\n123456789\n\n'
    # assert md('<p><a href="https://example.com">Some long link</a></p>', wrap=True, wrap_width=10) == '[Some long\nlink](https://example.com)\n\n'
    # assert md('<p>12345<br />67890</p>', wrap=True, wrap_width=10, newline_style=BACKSLASH) == '12345\\\n67890\n\n'
    # assert md('<p>12345678901<br />12345</p>', wrap=True, wrap_width=10, newline_style=BACKSLASH) == '12345678901\\\n12345\n\n'


def test_pre():
    assert md('<pre>test\n    foo\nbar</pre>') == '\n```\ntest\n    foo\nbar\n```\n'
    assert md('<pre><code>test\n    foo\nbar</code></pre>') == '\n```\ntest\n    foo\nbar\n```\n'
    assert md('<pre>this_should_not_escape</pre>') == '\n```\nthis_should_not_escape\n```\n'


def test_s():
    inline_tests('s', '~~')


def test_samp():
    inline_tests('samp', '`')


def test_strong():
    assert md('<strong>Hello</strong>') == '**Hello**'


# def test_strong_em_symbol():
#     assert md('<strong>Hello</strong>', strong_em_symbol=UNDERSCORE) == '__Hello__'
#     assert md('<b>Hello</b>', strong_em_symbol=UNDERSCORE) == '__Hello__'
#     assert md('<em>Hello</em>', strong_em_symbol=UNDERSCORE) == '_Hello_'
#     assert md('<i>Hello</i>', strong_em_symbol=UNDERSCORE) == '_Hello_'


def test_sub():
    assert md('<sub>foo</sub>') == 'foo'
    # assert md('<sub>foo</sub>', sub_symbol='~') == '~foo~'


def test_sup():
    assert md('<sup>foo</sup>') == 'foo'
    # assert md('<sup>foo</sup>', sup_symbol='^') == '^foo^'


# def test_lang():
#     assert md('<pre>test\n    foo\nbar</pre>', code_language='python') == '\n```python\ntest\n    foo\nbar\n```\n'
#     assert md('<pre><code>test\n    foo\nbar</code></pre>', code_language='javascript') == '\n```javascript\ntest\n    foo\nbar\n```\n'


# def test_lang_callback():
#     def callback(el):
#         return el['class'][0] if el.has_attr('class') else None

#     assert md('<pre class="python">test\n    foo\nbar</pre>', code_language_callback=callback) == '\n```python\ntest\n    foo\nbar\n```\n'
#     assert md('<pre class="javascript"><code>test\n    foo\nbar</code></pre>', code_language_callback=callback) == '\n```javascript\ntest\n    foo\nbar\n```\n'
#     assert md('<pre class="javascript"><code class="javascript">test\n    foo\nbar</code></pre>', code_language_callback=callback) == '\n```javascript\ntest\n    foo\nbar\n```\n'

def test_lang_callback2():
    assert md('<pre class="python">test\n    foo\nbar</pre>') == '\n```python\ntest\n    foo\nbar\n```\n'
    assert md('<pre class="javascript"><code>test\n    foo\nbar</code></pre>') == '\n```javascript\ntest\n    foo\nbar\n```\n'
    assert md('<pre class="javascript"><code class="javascript">test\n    foo\nbar</code></pre>') == '\n```javascript\ntest\n    foo\nbar\n```\n'


def test_large_codeblock():
    code = """<div class="markdown prose w-full break-words dark:prose-invert light"><p>You can use the <code>String.format()</code> method in Java to replace placeholders in a string with values from a map. Here's an example code snippet that demonstrates how you can achieve this:</p><pre><div class="bg-black mb-4 rounded-md"><div class="flex items-center relative text-gray-200 bg-gray-800 px-4 py-2 text-xs font-sans"><span class="">java</span><button class="flex ml-auto gap-2"><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>Copy code</button></div><div class="p-4 overflow-y-auto"><code class="!whitespace-pre hljs language-java"><span class="hljs-keyword">import</span> java.util.HashMap;
<span class="hljs-keyword">import</span> java.util.Map;

<span class="hljs-keyword">public</span> <span class="hljs-keyword">class</span> <span class="hljs-title class_">StringReplaceExample</span> {
    <span class="hljs-keyword">public</span> <span class="hljs-keyword">static</span> <span class="hljs-keyword">void</span> <span class="hljs-title function_">main</span><span class="hljs-params">(String[] args)</span> {
        <span class="hljs-type">String</span> <span class="hljs-variable">input</span> <span class="hljs-operator">=</span> <span class="hljs-string">"This is a new {object} at {place}"</span>;
        Map&lt;String, String&gt; replacements = <span class="hljs-keyword">new</span> <span class="hljs-title class_">HashMap</span>&lt;&gt;();
        replacements.put(<span class="hljs-string">"object"</span>, <span class="hljs-string">"student"</span>);
        replacements.put(<span class="hljs-string">"place"</span>, <span class="hljs-string">"point 3, 4"</span>);

        <span class="hljs-type">String</span> <span class="hljs-variable">output</span> <span class="hljs-operator">=</span> replacePlaceholders(input, replacements);
        System.out.println(output);
    }

    <span class="hljs-keyword">public</span> <span class="hljs-keyword">static</span> String <span class="hljs-title function_">replacePlaceholders</span><span class="hljs-params">(String input, Map&lt;String, String&gt; replacements)</span> {
        <span class="hljs-keyword">for</span> (Map.Entry&lt;String, String&gt; entry : replacements.entrySet()) {
            <span class="hljs-type">String</span> <span class="hljs-variable">placeholder</span> <span class="hljs-operator">=</span> <span class="hljs-string">"{"</span> + entry.getKey() + <span class="hljs-string">"}"</span>;
            <span class="hljs-type">String</span> <span class="hljs-variable">replacement</span> <span class="hljs-operator">=</span> entry.getValue();
            input = input.replace(placeholder, replacement);
        }
        <span class="hljs-keyword">return</span> input;
    }
}
</code></div></div></pre><p>In this example, we define the input string as "This is a new {object} at {place}", and create a <code>HashMap</code> called <code>replacements</code> that maps the placeholders "object" and "place" to their corresponding values "student" and "point 3, 4". We then pass these values to the <code>replacePlaceholders()</code> method, which iterates over the entries in the <code>replacements</code> map and replaces each placeholder in the input string with its corresponding value using the <code>replace()</code> method. Finally, the <code>replacePlaceholders()</code> method returns the modified string, which is printed to the console.</p><p>The output of this program will be:</p><pre><div class="bg-black mb-4 rounded-md"><div class="flex items-center relative text-gray-200 bg-gray-800 px-4 py-2 text-xs font-sans"><span class="">csharp</span><button class="flex ml-auto gap-2"><svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>Copy code</button></div><div class="p-4 overflow-y-auto"><code class="!whitespace-pre hljs language-csharp">This <span class="hljs-keyword">is</span> a <span class="hljs-keyword">new</span> student at point <span class="hljs-number">3</span>, <span class="hljs-number">4</span>
</code></div></div></pre><p>Note that you can modify the <code>replacements</code> map to include additional placeholders and their corresponding values, and the <code>replacePlaceholders()</code> method will automatically replace them in the input string.</p></div>"""
    
    check_code = """You can use the `String.format()` method in Java to replace placeholders in a string with values from a map. Here's an example code snippet that demonstrates how you can achieve this:

```java
import java.util.HashMap;
import java.util.Map;

public class StringReplaceExample {
    public static void main(String[] args) {
        String input = "This is a new {object} at {place}";
        Map<String, String> replacements = new HashMap<>();
        replacements.put("object", "student");
        replacements.put("place", "point 3, 4");

        String output = replacePlaceholders(input, replacements);
        System.out.println(output);
    }

    public static String replacePlaceholders(String input, Map<String, String> replacements) {
        for (Map.Entry<String, String> entry : replacements.entrySet()) {
            String placeholder = "{" + entry.getKey() + "}";
            String replacement = entry.getValue();
            input = input.replace(placeholder, replacement);
        }
        return input;
    }
}

```
In this example, we define the input string as "This is a new {object} at {place}", and create a `HashMap` called `replacements` that maps the placeholders "object" and "place" to their corresponding values "student" and "point 3, 4". We then pass these values to the `replacePlaceholders()` method, which iterates over the entries in the `replacements` map and replaces each placeholder in the input string with its corresponding value using the `replace()` method. Finally, the `replacePlaceholders()` method returns the modified string, which is printed to the console.
The output of this program will be:

```csharp
This is a new student at point 3, 4

```
Note that you can modify the `replacements` map to include additional placeholders and their corresponding values, and the `replacePlaceholders()` method will automatically replace them in the input string.
"""

    assert md(code) == check_code
pass
