from policyengine_us.model_api import *


class medicaid_ltss_qit_adjusted_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS QIT-adjusted income"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Trusted monthly income input after any qualified income trust "
        "treatment and applicant/spouse ownership allocation (TX MEPD "
        "F-6800; DSSM 20400.11). The model does not validate trust "
        "legality, irrevocability, funding, payback terms, or which income "
        "was validly deposited. The user must perform those determinations "
        "before supplying this value."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396p#d_4_B",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78",
    )
