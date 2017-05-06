
"""
TO DO:

- Change MOP < message in the royalty calculation to say sales or MOP
- Show a message for Min Royalty $ Well 54 Gas
- Add 'Unit' / 'Well' to the appropriate tables
- Start using Extract Date correctly and do amendment processing
- write the proofed logic
- Figure out the amendment no (One for volume, allocation, revenue)



Did
2017-05-06

- ValueBaseOn Default Oil to prod * price and gas to sales * price
- Default Crown multiplier to 1.0
- Change Monthly.ExtractMonth to Monthly.ExtractDate

2017-05-04
- Add RTPInfo to Data Dictionary (Lorraine)
- BaseTrans GORRTrans say only oil in DD (Lorraine)
- BaseGCA GORRGCA say only gas in DD (Lorraine)
- Update CrownMultiplier and Modifier in DD to say only SKProvCrownVar (Lorraine)
- Update LeaseRoyaltyMaster.RoyaltyBasedOn in DD Larry Research Now Update (Lorraine prove with examples)
    Royalty Based On - Used for IOGR1995 Gas, Oil, SKProvCrownVar Oil, Gas (Options: prod, sales, gj)
- Update LeaseRoyaltyMaster.PriceBasedOn in DD Larry Research Now Update (Lorraine prove with examples)
    Price Based On - Used for IOGR1995 Gas, Oil (Only options are a formula '=(' or blank which means SalesPrice)
- Update LeaseRoyaltyMaster.ValueBasedOn in DD Larry Research Now Update (Lorraine prove with examples)
    Value Based On - Used for GORR when a % is determine, SKProvCrownVar Oil, Gas (Options are formula '=(' or blank which means SalesPrice * SalesVol)
- Crown Modifier example Well 6 2015-01 (Lorraine add an example to DD)

2017-05-02

- SKProvCrownVar Well 65 Royalty should be based on Sales not working? Coded it for Gas.
- Show Crown Modifier being added into the Royalty Rate (Larry) (Looks like it works for oil)
- Royalty Based On should be: Royalty % Based On:
- Move Royalty Payor data on next line below Monthly Data:
- Remove CrownMultiplier and Modifier from IOGR1995
- Allow zero for transportation and GCA
- Add Lease # to the process message

"""

print('Hello World')

