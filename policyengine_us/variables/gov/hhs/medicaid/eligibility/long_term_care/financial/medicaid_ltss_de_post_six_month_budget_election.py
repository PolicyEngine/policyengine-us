from policyengine_us.model_api import *


class MedicaidLTSSDEPostSixMonthBudgetElection(Enum):
    INDIVIDUAL = "Individual"
    COUPLE = "Couple"
    NOT_SUPPLIED = "Not supplied"


class medicaid_ltss_de_post_six_month_budget_election(Variable):
    value_type = Enum
    possible_values = MedicaidLTSSDEPostSixMonthBudgetElection
    default_value = MedicaidLTSSDEPostSixMonthBudgetElection.NOT_SUPPLIED
    entity = MaritalUnit
    label = "Delaware Medicaid LTSS post-six-month budgeting election"
    definition_period = MONTH
    documentation = (
        "The couple's actual choice to be budgeted as two individuals or "
        "as a couple after six completed months together in the same "
        "institutional facility (DSSM 20810). This is a reported election, "
        "independent of income and resource calculations. NOT_SUPPLIED "
        "retains the budget admitting more spouses under both financial "
        "thresholds, with individual budgets on a tie. The election has "
        "no effect before six completed months, for spouses in different "
        "facilities, for same-address HCBS budgeting, for a one-person "
        "marital unit, or outside Delaware. In those cases the model "
        "continues to derive the mandatory unit from the service and "
        "location facts."
    )
    reference = "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=67"
