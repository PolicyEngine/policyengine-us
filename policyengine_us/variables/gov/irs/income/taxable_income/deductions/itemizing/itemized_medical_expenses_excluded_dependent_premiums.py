from policyengine_us.model_api import *


class itemized_medical_expenses_excluded_dependent_premiums(Variable):
    value_type = float
    entity = TaxUnit
    label = "Dependents' deducted medical insurance premiums excluded from Schedule A"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l_3",
        "https://www.law.cornell.edu/uscode/text/26/213#a",
    )
    documentation = (
        "Medical insurance premiums each dependent deducts through their own "
        "self-employed health insurance deduction. Each exclusion is limited "
        "to that person's paid medical premiums and the deduction left after "
        "its long-term care part. Premium inputs identify one payment per "
        "person without a separate payer, so the same payment cannot enter "
        "both the dependent's deduction and the parents' Schedule A. "
        "Undeducted premiums remain in the parents' medical expense base."
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        medical_part = min_(
            person("self_employed_health_insurance_ald_excluded_premiums", period),
            max_(0, person("self_employed_health_insurance_ald_person", period))
            - person("self_employed_health_insurance_ald_long_term_care_part", period),
        )
        return tax_unit.sum(medical_part * person("is_tax_unit_dependent", period))
