from policyengine_us.model_api import *


class mt_federal_income_tax_deduction_for_federal_itemization_indiv(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Montana federal income tax deduction when married couples are filing separately"
    reference = (
        "https://law.justia.com/codes/montana/2021/title-15/chapter-30/part-21/section-15-30-2131/"
        # MT Code § 15-30-2131 (2021) (1)(b)
    )
    unit = USD
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        unit_deds = person.tax_unit(
            "mt_federal_income_tax_deduction_for_federal_itemization", period
        )
        person_agi = person("mt_agi_indiv", period)
        total_agi = person.tax_unit.sum(person_agi)

        prorate = np.zeros_like(total_agi)
        mask = total_agi > 0
        prorate[mask] = person_agi[mask] / total_agi[mask]
        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.itemized.federal_income_tax
        cap = p.cap[filing_status]
        return min_(unit_deds * prorate, cap)
