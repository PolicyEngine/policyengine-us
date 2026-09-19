from policyengine_us.model_api import *


class medicaid_enrolled_before_work_requirements(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid enrolled, before any work requirement"
    definition_period = YEAR
    documentation = (
        "Mirrors medicaid_enrolled on is_medicaid_eligible_before_work_"
        "requirements. Equal to medicaid_enrolled for SSI recipients and "
        "other aged, blind or disabled people, whom the community engagement "
        "requirement never reaches. State supplements conditioned on Medicaid "
        "enrollment read this variable to stay out of the Medicaid, SNAP and "
        "state supplement dependency cycle that opens in 2027 (issue #9534)."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a"
    defined_for = "is_medicaid_eligible_before_work_requirements"
    adds = ["takes_up_medicaid_if_eligible"]
