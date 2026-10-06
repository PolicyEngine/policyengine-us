from policyengine_us.model_api import *


class medicaid_ltss_qit_adjusted_income(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS QIT-adjusted income"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Trusted monthly countable income after any qualified income trust "
        "treatment (TX MEPD F-6800; DSSM 20400.11). For an assistance unit "
        "of one, including an applicant with a community spouse, it is the "
        "applicant's own income after name-on-the-check and other "
        "ownership rules attribute income between the spouses (DSSM "
        "20990); for an assistance unit of two, it is the couple's combined "
        "income. The Delaware $20 general disregard is applied by the "
        "model, but any Delaware earned-income disregards (DSSM 20240.3) "
        "must already be reflected. The model does not validate trust "
        "legality, irrevocability, funding, payback terms, or which income "
        "was validly deposited. The user must perform those determinations "
        "before supplying this value."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396p#d_4_B",
        "https://fhb.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/f-6800-qualified-income-trust",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=54",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=71",
    )
