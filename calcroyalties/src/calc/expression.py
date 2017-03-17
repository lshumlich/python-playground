"""
This generic class is intended to evaluate expressions that are needed in the Royalty Calculation. The expressions are
expected is a format like: "=(prod + 10 - (sales * 3))". The expression itself can be anywhere in the string.

One place where this will be used is in the royalty calculation of a GORR. The GORR requires a formula to be
done based on monthly input. The formula expression uses a python package called py-expression-eval.

For our purposes we expect a string with =(expression) within the string. A few examples might be:
- "=(prod / sales * m.somelookup * 2)" or
- "=(prod / (sales * m.somelookup) * 2)" or
- "what ever =(prod / (sales * m.somelookup) * 2) somthing after" or

the tokens / or values
 - prod --> Prod from Monthly Data
 - sales --> Sales from Monthly Data
 - gj --> GJ from Monthly Data
 - whatever --> will lookup the string "whatever" with a ProdMonth of 0 in the table called Lookups
 - m.whatever --> will lookup the string "whatever" with a ProdMonth of the prod month in the table called Lookups

The evaluation is done and passed back.

Lorraine with write this up so it makes more sense.

Look at Sphinx for documentation generation.

"""

from py_expression_eval import Parser
from src.util.apperror import AppError


class Expression():

    def find_expression(selfs, s):
        a = s.find('=(')
        if a < 0:
            raise AppError('No formula found in string: ' + s)
        brace_count = 1
        for i in range(a + 2, len(s)):
            if s[i] == ')' : brace_count -= 1
            if s[i] == '(' : brace_count += 1
            if brace_count == 0 : break

        if brace_count != 0:
            raise AppError('The formula was not ended. Looking for matching ending ")" in string: ' + s)

        return a, i

    def get_expression(self, s):
        b, e = self.find_expression(s)
        return s[b+2:e]

    def evaluate_expression(self, s, m):
        e = self.get_expression(s)
        parse = Parser()
        expr = parse.parse(e)
        print("tostring : ", expr.toString())
        print("variables: ", expr. variables())

    def resolve_expression(self, s, m):
        return "asdf"

    def lookup(self, var_list, monthly):
        var_values = {}
        for v in var_list:
            if v == "sales":
                var_values[v] = monthly.SalesVol
            elif v == "prod":
                var_values[v] = monthly.ProdVol
            elif v == "gj":
                var_values[v] = monthly.GJ
            else:
                var_values[v] = "wtf"
            print(v)
        return var_values