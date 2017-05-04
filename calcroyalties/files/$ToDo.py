
"""
TO DO:

Add RTPInfo to Data Dictionary (Lorraine)
BaseTrans GORRTrans say only oil in DD (Lorraine)
BaseGCA GORRGCA say only gas in DD (Lorraine)
Update CrownMultiplier and Modifier in DD to say only SKProvCrownVar (Lorraine)
Update LeaseRoyaltyMaster.RoyaltyBasedOn in DD Larry Research Now Update (Lorraine prove with examples)
    Royalty Based On - Used for IOGR1995 Gas, Oil, SKProvCrownVar Oil, Gas (Options: prod, sales, gj)
Update LeaseRoyaltyMaster.PriceBasedOn in DD Larry Research Now Update (Lorraine prove with examples)
    Price Based On - Used for IOGR1995 Gas, Oil (Only options are a formula '=(' or blank which means SalesPrice)
Update LeaseRoyaltyMaster.ValueBasedOn in DD Larry Research Now Update (Lorraine prove with examples)
    Value Based On - Used for GORR when a % is determine, SKProvCrownVar Oil, Gas (Options are formula '=(' or blank which means SalesPrice * SalesVol)
Crown Modifier example Well 6 2015-01 (Lorraine add an example to DD)

check / add / RoyaltyBasedOn, PriceBasedOn, ValueBasedOn to the header remove None (well 6) (Think done)
Change MOP < message in the royalty calculation to say sales or MOP
Show a message for Min Royalty $ Well 54 Gas
Default royalty based on to prod

Did

2017-05-02

SKProvCrownVar Well 65 Royalty should be based on Sales not working? Coded it for Gas.
Show Crown Modifier being added into the Royalty Rate (Larry) (Looks like it works for oil)
Royalty Based On should be: Royalty % Based On:
Move Royalty Payor data on next line below Monthly Data:
Remove CrownMultiplier and Modifier from IOGR1995
Allow zero for transportation and GCA
Add Lease # to the process message


Notes:



"""

print('Hello World')

