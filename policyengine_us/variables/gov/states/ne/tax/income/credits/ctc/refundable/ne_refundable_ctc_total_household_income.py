from policyengine_us.model_api import *


class ne_refundable_ctc_total_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska refundable Child Tax Credit total household income"
    unit = USD
    documentation = (
        "Total household income for the Nebraska child care refundable tax "
        "credit: federal modified adjusted gross income (Neb. Rev. Stat. "
        "77-7202(8)). The Department of Revenue's worksheet adds Schedule 8812 "
        "line 2d to federal adjusted gross income: income from Puerto Rico and "
        "American Samoa and the Form 2555 foreign earned income and housing "
        "amounts (IRC 933, 931 and 911)."
    )
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7202",
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7203",
        "https://revenue.nebraska.gov/businesses/child-care-tax-credit-act",
        # Child Care Refundable Tax Credit Total Household Income Calculation,
        # lines 1 to 3.
        "https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/Child_Care_Total_Household_Income_Calculation.pdf#page=1",
        # Form 7203 instructions, Part A.
        "https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/f_7203_instruction_only.pdf#page=2",
    )
    defined_for = StateCode.NE

    adds = ["agi_plus_section_911_931_933_exclusions"]
