from policyengine_us.model_api import *


class qualified_passenger_vehicle_loan_interest_person(Variable):
    value_type = float
    entity = Person
    label = "qualified passenger vehicle loan interest on this person's loans"
    unit = USD
    documentation = (
        "Interest paid by this person on loans this person incurred that meet "
        "the federal qualified passenger vehicle loan interest requirements, "
        "including qualifying vehicle and loan requirements. It counts on the "
        "return of the tax unit this person heads or is the spouse in; a tax "
        "unit dependent's loans do not reach the filer's return."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/163#h_4_B_i",
        # PDF pages 24, 30
        "https://www.govinfo.gov/content/pkg/FR-2026-09-08/pdf/2026-18219.pdf#page=24",
    )
    uprating = "gov.bls.cpi.cpi_u"
