from ConfigParser import ConfigParser
from HTMLParser import HTMLParser
import string

css_template = '<link rel="stylesheet" href="%s" />\n'
js_template = '<script type="text/javascript" src="%s"></script>\n'

class TagChecker(HTMLParser):
    def __init__(self, path, tag, attr, ext):
        HTMLParser.__init__(self)
        self.path = path
        self.tag = tag
        self.attr = attr
        self.ext = '.'+ext
        self.found = False
        self.str = ''

    def test(self, str, names):
        self.found = False
        self.names = names
        self.str = str
        self.reset()
        self.feed(str)
        return self.found

    def handle_starttag(self, tag, attrs):
        if tag == self.tag:
            for attr in attrs:
                if attr[0] == self.attr:
                    for name in self.names:
                        css = self.path + name + self.ext
                        if attr[1] == css:
                            self.found = True
                            self.pos = self.getpos()[1]
                            break

class HeadChecker(HTMLParser):
    def __init__(self):
        self.start = False
        self.end = False

    def test(self, str):
        self.reset()
        self.feed(str)

    def handle_starttag(self, tag, attrs):
        if tag == 'head':
            self.start = True
        
    def handle_endtag(self, tag):
        if tag == 'head':
            self.end = True
        

def parse_list(data, pre='', post=''):
    items = []
    for s in string.split(data, ','):
        items.append(pre+string.strip(s)+post)
    return items

def ntab(n):
    tab = ''
    for i in range(0,css.pos):
        tab=tab+' '
    return tab

def combine_files(file_list, fn):
    f = open(fn, 'w')
    for file in file_list:
        print 'Writing file %s' % file
        f.write(open(file).read())
    f.close()

if __name__ == '__main__':

    config = ConfigParser()
    config.read("mediacat.ini")

    css_input = parse_list(config.get("css", "input"))
    js_input  = parse_list(config.get("js",  "input"))
    css_out   = config.get("css", "output")+'.css'
    js_out    = config.get("js", "output")+'.js'
    css_path  = config.get("css", "href")
    js_path   = config.get("js", "src")

    html_path = config.get("main", "html")
    html = open(html_path, 'r').readlines()
    tmp_html = open(html_path+'.out', 'w')

    css = TagChecker(css_path, 'link',   'href', 'css')
    js =  TagChecker(js_path,  'script', 'src',  'js')

    replacedCss = False
    replacedJs = False

    head = HeadChecker()

    for line in html:
        if not head.end:
            head.test(line)
        inhead = head.start and not head.end

        if inhead and css.test(line, css_input):
            if not replacedCss:
                line = (ntab(css.pos) + css_template)%(css_path+css_out)
                replacedCss = True
                tmp_html.write(line)
        elif inhead and js.test(line, js_input):
            if not replacedJs:
                line = (ntab(js.pos) + js_template)%(js_path+js_out)
                replacedJs = True
                tmp_html.write(line)
        else:        
            tmp_html.write(line)
    tmp_html.close()

    css_path = config.get("css", "path")
    js_path  = config.get("js",  "path")
    combine_files(parse_list(config.get("css", "input"), css_path, '.css'), css_path+css_out)
    combine_files(parse_list(config.get("js", "input"),  js_path, '.js'),  js_path+js_out)



