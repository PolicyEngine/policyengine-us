from policyengine_us.model_api import *

class StateSalesTaxIncomeBracket(Enum):
    One = "ONE"
    Two = "TWO"
    Three = "THREE"
    Four = "FOUR"
    Five = "FIVE"
    Six = "SIX"
    Seven = "SEVEN"
    Eight = "EIGHT"
    Nine = "NINE"
    Ten = "TEN"
    Eleven = "ELEVEN"
    Twelve = "TWELVE"
    Thirteen = "THIRTEEN"
    Fourteen = "FOURTEEN"
    Fifteen = "FIFTEEN"
    Sixteen = "SIXTEEN"
    Seventeen = "SEVENTEEN"
    Eighteen = "EIGHTEEN"
    Nineteen = "NINETEEN"


class state_sales_tax_income_bracket(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = StateSalesTaxIncomeBracket
    definition_period = YEAR
    label = "State Sales Tax Income Bracket"

    def formula(tax_unit, period, parameters):
        income = tax_unit("total_income_tax", period)
        return select(
            [
                (income > 0) & (income < 20_000),
                (income >= 20_000) & (income < 30_000),
                (income >= 30_000) & (income < 40_000),
                (income >= 40_000) & (income < 50_000),
                (income >= 50_000) & (income < 60_000),
                (income >= 60_000) & (income < 70_000),
                (income >= 70_000) & (income < 80_000),
                (income >= 80_000 & income < 90_000),
                (income >= 90_000 & income < 100_000),
                (income >= 100_000 & income < 120_000),
                (income >= 120_000 & income < 140_000),
                (income >= 140_000 & income < 160_000),
                (income >= 160_000 & income < 180_000),
                (income >= 180_000 & income < 200_000),
                (income >= 200_000 & income < 225_000),
                (income >= 225_000 & income < 250_000),
                (income >= 250_000 & income < 275_000),
                (income >= 275_000 & income < 300_000),
                (income >= 300_000),
            ],
            [
                StateSalesTaxIncomeBracket.One,
                StateSalesTaxIncomeBracket.Two,
                StateSalesTaxIncomeBracket.Three,
                StateSalesTaxIncomeBracket.Four,
                StateSalesTaxIncomeBracket.Five,
                StateSalesTaxIncomeBracket.Six,
                StateSalesTaxIncomeBracket.Seven,
                StateSalesTaxIncomeBracket.Eight,
                StateSalesTaxIncomeBracket.Nine,
                StateSalesTaxIncomeBracket.Ten,
                StateSalesTaxIncomeBracket.Eleven,
                StateSalesTaxIncomeBracket.Twelve,
                StateSalesTaxIncomeBracket.Thirteen,
                StateSalesTaxIncomeBracket.Fourteen,
                StateSalesTaxIncomeBracket.Fifteen,
                StateSalesTaxIncomeBracket.Sixteen,
                StateSalesTaxIncomeBracket.Seventeen,
                StateSalesTaxIncomeBracket.Eighteen,
                StateSalesTaxIncomeBracket.Nineteen,

            ],
            default=StateSalesTaxIncomeBracket.One,
        )