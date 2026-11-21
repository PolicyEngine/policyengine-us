from policyengine_us.model_api import *


class nd_ccap_workforce_benefit_eligible_parent(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    default_value = False
    label = "North Dakota CCAP caretaker meets the Workforce Benefit employment test"
    documentation = (
        "Records whether this caretaker meets the Workforce Benefit employment "
        "conditions in CCAP manual 400-28-20-40 for the month. "
        "From June 1, 2024, an employee must work at least 25 hours weekly in a "
        "North Dakota licensed, tribally licensed or registered child care program. "
        "The employer verifies employment on SFN 354. "
        "Approved-relative, self-declared and out-of-state providers do not qualify. "
        "Owners qualify only when their children attend another licensed program. "
        "Employees could not care for their own children before September 1, 2024. "
        "From May 1, 2025, the provider must operate at least 25 hours weekly, "
        "and maternity leave can excuse reduced employee hours. "
        "From April 1, 2026, employees and providers average 25 hours weekly. "
        "Employer-confirmed vacation, temporary closure and temporary sick leave "
        "can excuse reduced hours for up to one month. "
        "Maternity and extended sick leave require an anticipated return date. "
        "A job change or questionable hours at review require a new SFN 354. "
        "Keep this input true through the month employment or the license ends, "
        "or hours fall below the minimum without an allowed exception. "
        "Ordinary income testing and co-payments resume the following month. "
        "Other family eligibility conditions still apply."
    )
    reference = (
        "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_20_40.htm",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/ML/2024/CCAP%20ML%203819%20Effective%20June.1.2024.pdf",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/ML/2024/CCAP%20ML%203862%20Effective%20September.1.2024.pdf",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/ML/2025/CCAP%20ML%203909%20Effective%20May.1.2025.pdf",
        "https://www.nd.gov/dhs/policymanuals/40028/Content/ML/2026/CCAP%20Release%2026.2%20Effective%20April.1.2026.pdf",
    )
