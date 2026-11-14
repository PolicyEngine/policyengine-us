from policyengine_us.model_api import *


class federal_scholarship_qualified_contributions(Variable):
    value_type = float
    entity = Person
    label = "Qualified cash contributions for the Federal Scholarship Tax Credit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Qualified, designated and substantiated cash contributions made while the "
        "donor met the section 7701 citizenship or tax-residence requirement to an "
        "approved SGO in a participating state, net of goods or services. This is a "
        "subset of resolved_charitable_cash_donations_50_pct: include the gross gift "
        "once in existing cash donation inputs. It does not add another cash outlay. "
        "Qualification is supplied rather than inferred from immigration or state "
        "of residence. The donor may contribute to an SGO in another state."
    )
    reference = (
        "https://uscode.house.gov/us/usc/t26/s25F/",
        "https://www.govinfo.gov/content/pkg/FR-2026-10-02/html/2026-20277.htm",
    )
