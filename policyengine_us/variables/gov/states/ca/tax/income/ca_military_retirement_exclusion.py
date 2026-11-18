from policyengine_us.model_api import *


class ca_military_retirement_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "California military retirement and survivor benefit exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17132.9.&lawCode=RTC",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=17132.10.&lawCode=RTC",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.agi.military_retirement
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        limit = p.agi_limit[filing_status]
        eligible = agi <= limit

        # R&TC § 17132.9 excludes up to $20,000 of retired pay per return.
        # R&TC § 17132.10 excludes up to $20,000 of SBP survivor benefits per return.
        # The exclusion is capped at $20,000 for each payment category on a joint return,
        # surviving spouse, or any other individual (Schedule CA (540) line 5a/5b).
        retiree_pay = tax_unit_non_dep_add(
            tax_unit, period, ["military_retirement_pay"]
        )
        survivor_pay = tax_unit_non_dep_add(
            tax_unit, period, ["military_retirement_pay_survivors"]
        )
        capped_retiree = min_(p.cap, retiree_pay)
        capped_survivors = min_(p.cap, survivor_pay)
        return eligible * (capped_retiree + capped_survivors)
