from policyengine_us.model_api import *


class educator_expense(Variable):
    value_type = float
    entity = Person
    label = "Educator expenses"
    unit = USD
    documentation = (
        "Unreimbursed qualified expenses an eligible educator paid or "
        "incurred. An eligible educator is a teacher, instructor, counselor, "
        "principal or aide in a school for at least 900 hours in the school "
        "year. Kindergarten through grade 12 educators qualify in every year. "
        "Early childhood educators qualify for tax years beginning after "
        "2025 (Pub. L. 119-111, division B, section 1), in a school or "
        "childcare facility that serves more than two non-resident children "
        "under age 6 and is publicly funded or paid for those services. The "
        "model has no input for educator status and treats any positive "
        "amount as an eligible educator's, so enter an early childhood "
        "educator's expenses only for 2026 and later. Enter the full amount; "
        "the deduction applies the per-educator cap."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/62#a_2_D",
        "https://www.law.cornell.edu/uscode/text/26/62#d_1",
        # Pub. L. 119-111, division B, section 1 (140 Stat. 1049).
        "https://www.govinfo.gov/content/pkg/PLAW-119publ111/html/PLAW-119publ111.htm",
    )
