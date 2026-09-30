"""Hand-written questions that a user of the manual would actually ask.

Each question has two required facts TAKEN VERBATIM from the PDF (KSCI-19040-001,
the Kepler Data Characteristics Handbook). A question counts as answered only if
BOTH facts are present in the retrieved chunks.

The facts are substrings of the real document text, so scoring is exact and
deterministic -- no LLM and no human judgement at scoring time.
"""

QUESTIONS = [
    {
        "question": "What is a 'data set', and how is the observation interval for Long Cadence data indicated?",
        "facts": [
            "A data set refers to the data type and observation interval during which the data were collected",
            "The observation interval for Long Cadence data is usually a quarter, indicated by Q[n]",
        ],
    },
    {
        "question": "When did Module 3 fail, and what is the impact on science observations?",
        "facts": [
            "All 4 outputs of Module 3 failed at 17:52 UTC Jan 9, 2010, during LC CIN 12935",
            "20% of the FOV will suffer a one-Quarter data outage every year",
        ],
    },
    {
        "question": "Why are users cautioned about Argabrightening cadences?",
        "facts": [
            "a diffuse illumination of the focal plane, lasting on the order of a few minutes, possibly due to impact-generated debris",
            "users are cautioned about Argabrightening cadences because of the possible fine spatial structure",
        ],
    },
{
        "question": "How is the safe-mode anomaly in LC cadences 3553-3659 described, and what is the first valid cadence after it?",
        "facts": [
            "SAFE_MODE from 3553 to 3652",
            "the first valid LC back at science attitude",
        ],
    },
    {
        "question": "What are the frequency and period values for the 10/LC spurious harmonic?",
        "facts": [
            "10/LC narrow",
            "5663.9 489.36 176.56",
        ],
    },
    {
        "question": "How are narrow and broad spurious lines defined?",
        "facts": [
            "Narrow lines are defined as > 50",
            "broad lines as < 50",
        ],
    },
]