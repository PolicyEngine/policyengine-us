from policyengine_us.model_api import *


class az_family_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Arizona Family Tax Credit"
    definition_period = YEAR
    reference = (
        "https://www.azleg.gov/ars/43/01073.htm",
        "https://www.azleg.gov/ars/43/01001.htm",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.credits.family_tax_credits
        # Per ARS 43-1073: "Arizona adjusted gross income, plus the amount
        # subtracted for exemptions under section 43-1023"
        az_agi = tax_unit("az_agi", period)
        exemptions = tax_unit("az_exemptions", period)
        income = az_agi + exemptions
        filing_status = tax_unit("az_filing_status", period)
        status = filing_status.possible_values
        # The thresholds count dependents in the IRC 152 sense (A.R.S.
        # 43-1001(3)); a return on which the filer (or, if joint, either
        # spouse) can be claimed as a dependent has none (IRC 152(b)(1)).
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        dependents = where(
            filer_is_dependent, 0, tax_unit("tax_unit_dependents", period)
        )
        income_limit = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
            ],
            [
                p.income_limit.single,
                p.income_limit.joint.calc(dependents),
                p.income_limit.head_of_household.calc(dependents),
                p.income_limit.separate,
            ],
        )
        return income <= income_limit
