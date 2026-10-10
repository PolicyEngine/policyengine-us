from policyengine_us.model_api import *


class itemized_medical_expenses_excluded_premiums(Variable):
    value_type = float
    entity = TaxUnit
    label = "Self-employed health insurance premiums excluded from Schedule A"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/162#l_3",
        "https://www.irs.gov/instructions/i1040sca",
    ]
    documentation = (
        "The federal self-employed health insurance ALD, limited to premiums "
        "paid by the head and spouse. Premium inputs use payer attribution, "
        "including family coverage paid by a filer. This preserves supplied "
        "tax-unit ALDs without allocating them to individual filers. States "
        "that retain gross paid medical costs add this excluded amount back "
        "to itemized_medical_expenses, including a caller-supplied subtotal."
    )

    def formula(tax_unit, period, parameters):
        filer_premiums = tax_unit_non_dep_sum(
            "medical_expense_health_insurance_premiums", tax_unit, period
        )
        se_health_insurance_ald = tax_unit("self_employed_health_insurance_ald", period)
        return min_(filer_premiums, max_(0, se_health_insurance_ald))
