from policyengine_us.model_api import *


class ct_pension_annuity_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut pension and annuity subtraction"
    unit = USD
    reference = (
        "https://www.cga.ct.gov/current/pub/chap_229.htm#sec_12-701",  # Sec. 12-701 (20)(B)(xxi)&(xxii)
        "https://portal.ct.gov/-/media/drs/forms/2024/income/2024-ct-1040-instructions_1224.pdf#page=28",
    )
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        agi = tax_unit("adjusted_gross_income", period)

        p = parameters(
            period
        ).gov.states.ct.tax.income.subtractions.pensions_or_annuity

        # Get the rate based on AGI and filing status
        is_joint = (filing_status == status.JOINT) | (
            filing_status == status.SURVIVING_SPOUSE
        )

        rate = where(is_joint, p.joint.calc(agi), p.non_joint.calc(agi))

        # Apply the rate to eligible pension income
        pension_income = person("taxable_pension_income", period)
        eligible_pension = pension_income * head_or_spouse
        total_pension = tax_unit.sum(eligible_pension)

        return total_pension * rate
