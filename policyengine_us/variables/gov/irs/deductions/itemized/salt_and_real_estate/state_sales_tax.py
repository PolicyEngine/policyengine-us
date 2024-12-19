from policyengine_us.model_api import *


class StateSalesTax(Enum):
    1 = "0"
    2 = "20000"
    3 = "30000"
    4 = "40000"
    5 = "50000"
    6 = "60000"
    7 = "70000"
    8 = "80000"
    9 = "90000"
    10 = "100000"
    11 = "120000"
    12 = "140000"
    13 = "160000"
    14 = "180000"
    15 = "200000"
    16 = "225000"
    17 = "250000"
    18 = "275000"
    19 = "300000"

class state_sales_tax(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = StateSalesTax
    # default_value = StateSalesTax.1
    definition_period = YEAR
    label = "State Sales Tax"

    def formula(tax_unit, period, parameters):
        income = tax_unit("total_income_tax", period)
        return select(
            [
                income > 0 & income < 20_000,
                income >= 20_000 & income < 30_000,
                income >= 30_000 & income < 40_000,
                income >= 40_000 & income < 50_000,
                income >= 50_000 & income < 60_000,
                income >= 60_000 & income < 70_000,
                income >= 70_000 & income < 80_000,
                income >= 80_000 & income < 90_000,
                income >= 90_000 & income < 100_000,
                income >= 100_000 & income < 120_000,
                income >= 120_000 & income < 140_000,
                income >= 140_000 & income < 160_000,
                income >= 160_000 & income < 180_000,
                income >= 180_000 & income < 200_000,
                income >= 200_000 & income < 225_000,
                income >= 225_000 & income < 250_000,
                income >= 250_000 & income < 275_000,
                income >= 275_000 & income < 300_000,
                income >= 300_000,
            ],
            [
                StateSalesTax.1,
                StateSalesTax.2,
                StateSalesTax.3,
                StateSalesTax.4,
                StateSalesTax.5,
                StateSalesTax.6,
                StateSalesTax.7,
                StateSalesTax.8,
                StateSalesTax.9,
                StateSalesTax.10,
                StateSalesTax.11,
                StateSalesTax.12,
                StateSalesTax.13,
                StateSalesTax.14,
                StateSalesTax.15,
                StateSalesTax.16,
                StateSalesTax.17,
                StateSalesTax.18,
                StateSalesTax.19,
            ],
            default=StateSalesTax.1,
        )