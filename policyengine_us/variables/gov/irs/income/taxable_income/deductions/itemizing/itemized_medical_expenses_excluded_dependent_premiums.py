from policyengine_us.model_api import *


class itemized_medical_expenses_excluded_dependent_premiums(Variable):
    value_type = float
    entity = TaxUnit
    label = "Dependents' deducted medical insurance premiums excluded from Schedule A"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapB-partVI-sec162.htm",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapB-partVII-sec213.htm",
        "https://www.ecfr.gov/current/title-26/section-1.213-1#p-1.213-1(a)(1)",
    )
    documentation = (
        "Medical insurance premiums each dependent deducts through their own "
        "self-employed health insurance deduction. Each exclusion is limited "
        "to that person's paid medical premiums and the deduction left after "
        "its long-term care part. Premium inputs identify one payment per "
        "person without a separate payer. Under section 213(a) and Treasury "
        "regulation 1.213-1(a)(1), parents may count only medical expenses "
        "they paid. A dependent who deducts their own premiums paid those "
        "premiums, so this amount leaves the parents' Schedule A. The formula "
        "retains the existing treatment of undeducted dependent premiums."
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        medical_part = min_(
            person("self_employed_health_insurance_ald_excluded_premiums", period),
            max_(0, person("self_employed_health_insurance_ald_person", period))
            - person("self_employed_health_insurance_ald_long_term_care_part", period),
        )
        return tax_unit.sum(medical_part * person("is_tax_unit_dependent", period))
