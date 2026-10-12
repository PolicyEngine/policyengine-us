from policyengine_us.model_api import *


class mn_child_and_working_families_credits_ctc_eligible_child(Variable):
    value_type = float
    entity = Person
    label = (
        "Minnesota child and working families credits child tax credit eligible child"
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0661#stat.290.0661.4",
        "https://www.revisor.mn.gov/statutes/cite/290.0671",
        "https://www.revenue.state.mn.us/sites/default/files/2025-01/m1cwfc-23.pdf",
    )
    defined_for = StateCode.MN

    def formula(person, period, parameters):
        age = person("age", period)
        # Minn. Stat. 290.0661, subd. 1 defines "qualifying child" by IRC 32(c)
        # but explicitly provides that "section 32(m) of the Internal Revenue
        # Code does not apply" (and 290.0671 does the same for the Working
        # Family Credit). Section 32(m) is the SSN-valid-for-employment
        # requirement, so Minnesota deliberately allows ITIN filers and ITIN
        # children. The M1CWFC instructions confirm this: filers whose spouse or
        # qualifying children lack an SSN "may use an Individual Taxpayer
        # Identification Number (ITIN) to claim these credits." We therefore do
        # not apply meets_eitc_identification_requirements (the 32(m) gate).
        p = parameters(period).gov.states.mn.tax.income.credits.cwfc.ctc
        age_eligible = age < p.age_limit
        is_dependent = person("is_tax_unit_dependent", period)
        return age_eligible & is_dependent
