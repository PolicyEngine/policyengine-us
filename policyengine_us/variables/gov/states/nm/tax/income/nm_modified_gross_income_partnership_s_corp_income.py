from policyengine_us.model_api import *


class nm_modified_gross_income_partnership_s_corp_income(Variable):
    value_type = float
    entity = Person
    label = "New Mexico modified gross income partnership and S corporation income"
    unit = USD
    documentation = (
        "A person's partnership and S corporation income for New Mexico "
        "modified gross income. The loss from one business or activity shall "
        "not reduce the income from another, so partnership_income and "
        "s_corp_income are each floored at zero on their own. When neither is "
        "supplied, partnership_s_corp_income may be a combined amount entered "
        "directly (as the TAXSIM emulator and older datasets do), and that "
        "amount, floored at zero, is used instead; losses netted inside it "
        "cannot be separated."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/new-mexico/N-M-Admin-Code-SS-3.3.1.10",
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503656",
        "https://taxsim.nber.org/historical_state_tax_forms/NM/2025/NM_PIT_RC_INST.PDF#page=4",
    )
    defined_for = StateCode.NM

    def formula(person, period, parameters):
        # 3.3.1.10(B) NMAC: "The loss from one business or activity shall not
        # reduce the income from another business or activity."
        # NOTE: partnership_s_corp_income adds the two parts, but it can be
        # set directly with both parts left at zero; once it is an input for
        # anyone in a simulation, everyone else holds its default of zero, so
        # the parts decide whenever either is nonzero.
        partnership_income = person("partnership_income", period)
        s_corp_income = person("s_corp_income", period)
        parts_supplied = (partnership_income != 0) | (s_corp_income != 0)
        floored_parts = max_(partnership_income, 0) + max_(s_corp_income, 0)
        combined = max_(person("partnership_s_corp_income", period), 0)
        return where(parts_supplied, floored_parts, combined)
