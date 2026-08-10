from policyengine_us.model_api import *


class la_ccap_special_needs_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Louisiana CCAP special needs child"
    reference = "https://www.doa.la.gov/media/043btqeh/28v165.docx"
    defined_for = StateCode.LA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.la.ldoe.ccap.age
        # LAC 28:CLXV.103 "Care for Children with Disabilities": a child birth
        # through age 17 with a current IEP or IFSP under IDEA, or who receives
        # SSI. The IFSP (IDEA Part C, birth to age three) route is approximated
        # by a screening-indicated developmental delay; the general is_disabled
        # flag is also accepted as the broad disability signal underlying the
        # statutory IEP/IFSP/SSI channels.
        age = person("age", period.this_year)
        disabled = person("is_disabled", period.this_year)
        iep = person("has_individualized_education_program", period.this_year)
        developmental_delay = person("has_developmental_delay", period.this_year)
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        return (age < p.disabled_child_limit) & (
            disabled | iep | developmental_delay | receives_ssi
        )
