from policyengine_us.model_api import *


class or_ssp_excluding_in_home_supplement(Variable):
    value_type = float
    entity = Person
    label = "Oregon SSP excluding the in-home supplement"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.9#c_5",
        "https://odhsssprulesprdwu1st01.blob.core.windows.net/rules/461-145-0410.pdf#page=2",
        # 24 CFR 5.609(b)(6), (b)(19)
        "https://www.law.cornell.edu/cfr/text/24/5.609",
        "https://sharedsystems.dhsoha.state.or.us/DHSForms/Served/de2818.pdf#page=583",
    )
    defined_for = StateCode.OR
    documentation = "The Oregon SSP payment excluding the in-home supplement, which is a reimbursement for uncovered assistance needs. SNAP and HUD count this amount as unearned income."

    def formula(person, period, parameters):
        # NOTE: OAR 461-145-0410(7)(c)(D) excludes most special needs payments
        # from SNAP income as reimbursements. The model follows 7 CFR
        # 273.9(c)(5), which counts payments for normal living expenses such
        # as room and board, and excludes only the in-home supplement.
        category = person("or_ssp_category", period)
        in_home = category == category.possible_values.IN_HOME
        return where(in_home, 0, person("or_ssp", period))
