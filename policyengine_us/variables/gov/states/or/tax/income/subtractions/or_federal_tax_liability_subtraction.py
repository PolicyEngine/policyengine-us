from policyengine_us.model_api import *


class or_federal_tax_liability_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR federal tax liability subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=13",
        "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",  # Subsection 316.800
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        income = tax_unit("adjusted_gross_income", period)
        # Use no-SALT income tax to avoid circular logic, until we add
        # withholding rules.
        federal_tax_liability = tax_unit("no_salt_income_tax", period)
        # Instructions for line 14:
        # "This is your federal income tax liability after refundable credits
        #  (other than the EITC)."
        eitc = tax_unit("eitc", period)
        federal_tax_liability_less_eitc = federal_tax_liability + eitc
        non_negative_federal_tax_liability = max_(
            0, federal_tax_liability_less_eitc
        )
        caps = (
            parameters(period)
            .gov.states["or"]
            .tax.income.subtractions.federal_tax_liability.cap
        )
        cap = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.JOINT,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.WIDOW,
            ],
            [
                caps.single.calc(income),
                caps.joint.calc(income),
                caps.head_of_household.calc(income),
                caps.separate.calc(income),
                caps.widow.calc(income),
            ],
        )
        return min_(non_negative_federal_tax_liability, cap)
