"""

Just a little piece of code to help generate the boring stuff.

"""
attrs = """
abc
def
geh
ijk
asdf
"""

template = """
        <tr>
          <td><label for="{{name}}">{{name}}</label></td>
          <td><input type="text" name="{{name}}" value={{result.{{name}}}}></td>
        </tr>
"""


def gen_td():
    
    words = attrs.split("\n")
#     print(words)

    for attr in words:
        if attr:
            print(template.replace('{{name}}', attr))
    

gen_td()
