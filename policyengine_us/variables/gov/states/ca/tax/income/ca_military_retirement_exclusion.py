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

        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # R&TC § 17132.9 excludes up to $20,000 of retired pay.
        # R&TC § 17132.10 excludes up to $20,000 of SBP survivor benefits.
        capped_retiree = min_(p.cap, person("military_retirement_pay", period))
        capped_survivors = min_(
            p.cap, person("military_retirement_pay_survivors", period)
        )
        total_person = (capped_retiree + capped_survivors) * head_or_spouse
        return eligible * tax_unit.sum(total_person)
