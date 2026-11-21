from policyengine_us.model_api import *


class IDRetirementBenefitsDisabilityClassification(Enum):
    UNSPECIFIED = "Unspecified"
    DISABLED = "Classified as disabled"
    NOT_DISABLED = "Not classified as disabled"


class id_retirement_benefits_disability_classification(Variable):
    value_type = Enum
    possible_values = IDRetirementBenefitsDisabilityClassification
    default_value = IDRetirementBenefitsDisabilityClassification.UNSPECIFIED
    entity = Person
    definition_period = YEAR
    label = "Idaho disability classification for the retirement benefits deduction, as supplied"
    documentation = """
    Whether the person is classified as disabled under Idaho Code
    63-3022A(4), as supplied for this person. DISABLED: a person recognized
    as disabled by the Social Security Administration under title 42 (for
    example, a disability insurance or SSI disability award), by the Railroad
    Retirement Board or by the office of management and budget under title 5,
    or, if none of those has purview over the person, by the public employee
    retirement system or disability plan the person participates in
    (63-701(1)(d)); a veteran of a war engaged in by the United States whose
    disability the Department of Veterans Affairs recognizes as
    service-connected to a degree of 10% or more, or who has a VA pension for
    nonservice-connected disabilities (63-701(1)(e)); or a person whose
    physician certifies a permanent disability under 49-117(7)(b)(iv).
    NOT_DISABLED: anyone else, including a person whose only disability
    finding comes from outside those groups. UNSPECIFIED, the default, means
    not supplied: id_retirement_benefits_deduction_disabled then uses this
    person's own Social Security disability insurance benefits and
    is_disabled, whatever other people's classifications are. As with every
    input, Core carries a classification into a later year only when no one
    has one for that year: once anyone supplies a classification for a
    year, a person whose classification was supplied only for an earlier
    year is UNSPECIFIED in that year. Supply each person's classification
    for every year calculated.
    """
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/",
        "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch7/sect63-701/",
        "https://legislature.idaho.gov/statutesrules/idstat/title49/t49ch1/sect49-117/",
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=45",
    )
