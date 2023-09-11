from policyengine_us.model_api import *


class or_wfhdc_table_letter(Variable):
    value_type = str
    entity = TaxUnit
    label = "Oregon WFHDC percentage table row letter"
    unit = USD
    definition_period = YEAR
    defined_for = "or_wfhdc_eligible"
    reference = "https://www.oregon.gov/dor/forms/FormsPubs/publication-or-wfhdc-tb_101-458_2022.pdf"
    default_value = ""

    def formula(tax_unit, period, parameters):
        # Get the parameter tree for the WFHDC table row letter.
        p = (
            parameters(period)
            .gov.states["or"]
            .tax.income.credits.wfhdc.table_letter
        )

        # Get the household size.
        household_size = tax_unit("tax_unit_size", period)

        # Get the household income, considered the larger of federal and Oregon AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)
        or_agi = tax_unit("or_income_after_subtractions", period)
        household_income = max_(federal_agi, or_agi)

        # Get the table row number based on household size and income.
        row_number = select(
            [
                household_size == 2,
                household_size == 3,
                household_size == 4,
                household_size == 5,
                household_size == 6,
                household_size == 7,
                household_size >= 8,
            ],
            [
                p.household_size_2.calc(household_income, right=True),
                p.household_size_3.calc(household_income, right=True),
                p.household_size_2.calc(household_income, right=True),
                p.household_size_2.calc(household_income, right=True),
                p.household_size_2.calc(household_income, right=True),
                p.household_size_2.calc(household_income, right=True),
                p.household_size_2.calc(household_income, right=True),
            ],
            default="",
        )

        # Create a mapping of numbers 1-26 to letters A-Z.
        letter_map = {
            1: "A",
            2: "B",
            3: "C",
            4: "D",
            5: "E",
            6: "F",
            7: "G",
            8: "H",
            9: "I",
            10: "J",
            11: "K",
            12: "L",
            13: "M",
            14: "N",
            15: "O",
            16: "P",
            17: "Q",
            18: "R",
            19: "S",
            20: "T",
            21: "U",
            22: "V",
            23: "W",
            24: "X",
            25: "Y",
            26: "Z",
        }

        # Get the corresponding letter from the mapping.
        row_number = pd.Series(row_number).astype(int)
        return row_number.map(letter_map)
