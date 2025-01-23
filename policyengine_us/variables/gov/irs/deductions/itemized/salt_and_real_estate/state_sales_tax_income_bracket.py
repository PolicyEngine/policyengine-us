from policyengine_us.model_api import *

class StateSalesTaxIncomeBracket(Enum):
    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    FIVE = "FIVE"
    SIX = "SIX"
    SEVEN = "SEVEN"
    EIGHT = "EIGHT"
    NINE = "NINE"
    TEN = "TEN"
    ELEVEN = "ELEVEN"
    TWELVE = "TWELVE"
    THIRTEEN = "THIRTEEN"
    FOURTEEN = "FOURTEEN"
    FIFTEEN = "FIFTEEN"
    SIXTEEN = "SIXTEEN"
    SEVENTEEN = "SEVENTEEN"
    EIGHTEEN = "EIGHTEEN"
    NINETEEN = "NINETEEN"

class state_sales_tax_income_bracket(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = StateSalesTaxIncomeBracket
    default_value = StateSalesTaxIncomeBracket.ONE
    definition_period = YEAR
    label = "State Sales Tax Income Bracket"

    def formula(tax_unit, period, parameters):
        print("Formula method called")  # The Formula is not called
        income = tax_unit("federal_state_income_tax", period)
        print(f"Income: {income}")  # No output

        return select(
            [
                (income > 0) & (income < 20_000),
                (income >= 20_000) & (income < 30_000),
                (income >= 30_000) & (income < 40_000),
                (income >= 40_000) & (income < 50_000),
                (income >= 50_000) & (income < 60_000),
                (income >= 60_000) & (income < 70_000),
                (income >= 70_000) & (income < 80_000),
                (income >= 80_000) & (income < 90_000),
                (income >= 90_000) & (income < 100_000),
                (income >= 100_000) & (income < 120_000),
                (income >= 120_000) & (income < 140_000),
                (income >= 140_000) & (income < 160_000),
                (income >= 160_000) & (income < 180_000),
                (income >= 180_000) & (income < 200_000),
                (income >= 200_000) & (income < 225_000),
                (income >= 225_000) & (income < 250_000),
                (income >= 250_000) & (income < 275_000),
                (income >= 275_000) & (income < 300_000),
                (income >= 300_000),
            ],
            [
                StateSalesTaxIncomeBracket.ONE,
                StateSalesTaxIncomeBracket.TWO,
                StateSalesTaxIncomeBracket.THREE,
                StateSalesTaxIncomeBracket.FOUR,
                StateSalesTaxIncomeBracket.FIVE,
                StateSalesTaxIncomeBracket.SIX,
                StateSalesTaxIncomeBracket.SEVEN,
                StateSalesTaxIncomeBracket.EIGHT,
                StateSalesTaxIncomeBracket.NINE,
                StateSalesTaxIncomeBracket.TEN,
                StateSalesTaxIncomeBracket.ELEVEN,
                StateSalesTaxIncomeBracket.TWELVE,
                StateSalesTaxIncomeBracket.THIRTEEN,
                StateSalesTaxIncomeBracket.FOURTEEN,
                StateSalesTaxIncomeBracket.FIFTEEN,
                StateSalesTaxIncomeBracket.SIXTEEN,
                StateSalesTaxIncomeBracket.SEVENTEEN,
                StateSalesTaxIncomeBracket.EIGHTEEN,
                StateSalesTaxIncomeBracket.NINETEEN,

            ]
        )