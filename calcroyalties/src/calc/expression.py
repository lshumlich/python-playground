"""
This class is intended to evaluate expressions that are needed in the Royalty Calculation.

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

