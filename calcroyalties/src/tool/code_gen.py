"""

Just a little piece of code to help generate the boring stuff.

"""
attrs = """
ID
StartDate
EndDate
RightsGranted
RoyaltyScheme
CrownMultiplier
CrownModifier
OilPriceBasedOn
GasPriceBasedOn
ProductsPriceBasedOn
OilValueBasedOn
GasValueBasedOn
ProductsValueBasedOn
OilRoyaltyBasedOn
GasRoyaltyBasedOn
ProductsRoyaltyBasedOn
TransDeducted
ProcessingDeducted
GCADeducted
Gorr
OverrideRoyaltyClassification
MinRoyaltyRate
MaxRoyaltyRate
MinRoyaltyDollar
Notes
"""

template = """
            <tr>
                <td><label for="{{name}}">{{name}}</label> <sup><i data-help="LeaseRoyaltyMaster.{{name}}" class="fa fa-question-circle help"></i></sup></td>
                <td><input type="text" name="{{name}}" value="{{ royaltymaster.{{name}} }}" /></td>
            </tr>"""

templatexx = """
                <label for="{{name}}">{{name}}</label> <sup><i data-help="LeaseRoyaltyMaster.{{name}}" class="fa fa-question-circle help"></i></sup>
                <input type="text" name="{{name}}" value="{{ royaltymaster.{{name}} }}" />"""


def gen_td():
    words = attrs.split("\n")
    #     print(words)

    for attr in words:
        if attr:
            print(template.replace('{{name}}', attr))


gen_td()
