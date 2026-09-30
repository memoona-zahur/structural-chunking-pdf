# Structural vs Recursive — on a real multi-page PDF

methods: ['structural', 'recursive'] | top-2 | questions: 6

| method | chunks | avg chunk chars | hits | P@2 | R@2 | MRR@2 | NDCG@2 |
|---|---|---|---|---|---|---|---|
| structural | 93 | 813 | 6/6 | 1.000 | 1.000 | 1.000 | 1.000 |
| recursive | 137 | 551 | 1/6 | 0.333 | 0.333 | 0.417 | 0.438 |

per-question detail:

## structural
- Q1: What is a 'data set', and how is the observation interval for Long Cadence data indicated?
  facts found: 2/2 · hit: True · mrr@2: 1.000 · ndcg@2: 1.000
  retrieved: ['2. Release Description', '1. Introduction']
- Q2: When did Module 3 fail, and what is the impact on science observations?
  facts found: 2/2 · hit: True · mrr@2: 1.000 · ndcg@2: 1.000
  retrieved: ['4.6 Module 3 Failure', '5.4 Reaction Wheel Zero Crossings']
- Q3: Why are users cautioned about Argabrightening cadences?
  facts found: 2/2 · hit: True · mrr@2: 1.000 · ndcg@2: 1.000
  retrieved: ['5.8 Argabrightening', '7.3 Background Time Series']
- Q4: How is the safe-mode anomaly in LC cadences 3553-3659 described, and what is the first valid cadence after it?
  facts found: 2/2 · hit: True · mrr@2: 1.000 · ndcg@2: 1.000
  retrieved: ['5.13 Anomaly Summary Table', '5.5 Downlink Earth Point']
- Q5: What are the frequency and period values for the 10/LC spurious harmonic?
  facts found: 2/2 · hit: True · mrr@2: 1.000 · ndcg@2: 1.000
  retrieved: ['5.12 Spurious Frequencies in SC Data', '6.4 Times in MAST FITS files']
- Q6: How are narrow and broad spurious lines defined?
  facts found: 2/2 · hit: True · mrr@2: 1.000 · ndcg@2: 1.000
  retrieved: ['5.12 Spurious Frequencies in SC Data', 'Boundaries']

## recursive
- Q1: What is a 'data set', and how is the observation interval for Long Cadence data indicated?
  facts found: 0/2 · hit: False · mrr@2: 0.000 · ndcg@2: 0.000
  retrieved: ['recursive-10', 'recursive-5']
- Q2: When did Module 3 fail, and what is the impact on science observations?
  facts found: 1/2 · hit: False · mrr@2: 0.500 · ndcg@2: 0.631
  retrieved: ['recursive-39', 'recursive-38']
- Q3: Why are users cautioned about Argabrightening cadences?
  facts found: 0/2 · hit: False · mrr@2: 0.000 · ndcg@2: 0.000
  retrieved: ['recursive-75', 'recursive-79']
- Q4: How is the safe-mode anomaly in LC cadences 3553-3659 described, and what is the first valid cadence after it?
  facts found: 1/2 · hit: False · mrr@2: 1.000 · ndcg@2: 1.000
  retrieved: ['recursive-99', 'recursive-27']
- Q5: What are the frequency and period values for the 10/LC spurious harmonic?
  facts found: 0/2 · hit: False · mrr@2: 0.000 · ndcg@2: 0.000
  retrieved: ['recursive-93', 'recursive-94']
- Q6: How are narrow and broad spurious lines defined?
  facts found: 2/2 · hit: True · mrr@2: 1.000 · ndcg@2: 1.000
  retrieved: ['recursive-96', 'recursive-90']
