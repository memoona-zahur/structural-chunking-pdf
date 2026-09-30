# Structural vs Recursive — on a real multi-page PDF

methods: ['structural', 'recursive'] | top-2 | questions: 6

| method | chunks | avg chunk chars | hits | P@2 | R@2 |
|---|---|---|---|---|---|
| structural | 93 | 813 | 6/6 | 1.0 | 1.0 |
| recursive | 137 | 551 | 1/6 | 0.333 | 0.333 |

per-question detail:

## structural
- Q: What is a 'data set', and how is the observation interval for Long Cadence data indicated?
  facts found: 2/2 · hit: True
  retrieved: ['1. Introduction', '2. Release Description']
- Q: When did Module 3 fail, and what is the impact on science observations?
  facts found: 2/2 · hit: True
  retrieved: ['4.6 Module 3 Failure']
- Q: Why are users cautioned about Argabrightening cadences?
  facts found: 2/2 · hit: True
  retrieved: ['5.8 Argabrightening', '7.3 Background Time Series']
- Q: How is the safe-mode anomaly in LC cadences 3553-3659 described, and what is the first valid cadence after it?
  facts found: 2/2 · hit: True
  retrieved: ['5.5 Downlink Earth Point', '5.13 Anomaly Summary Table']
- Q: What are the frequency and period values for the 10/LC spurious harmonic?
  facts found: 2/2 · hit: True
  retrieved: ['5.12 Spurious Frequencies in SC Data']
- Q: How are narrow and broad spurious lines defined?
  facts found: 2/2 · hit: True
  retrieved: ['5.12 Spurious Frequencies in SC Data']

## recursive
- Q: What is a 'data set', and how is the observation interval for Long Cadence data indicated?
  facts found: 0/2 · hit: False
  retrieved: ['recursive-5', 'recursive-10']
- Q: When did Module 3 fail, and what is the impact on science observations?
  facts found: 1/2 · hit: False
  retrieved: ['recursive-38', 'recursive-39']
- Q: Why are users cautioned about Argabrightening cadences?
  facts found: 0/2 · hit: False
  retrieved: ['recursive-75', 'recursive-79']
- Q: How is the safe-mode anomaly in LC cadences 3553-3659 described, and what is the first valid cadence after it?
  facts found: 1/2 · hit: False
  retrieved: ['recursive-27', 'recursive-99']
- Q: What are the frequency and period values for the 10/LC spurious harmonic?
  facts found: 0/2 · hit: False
  retrieved: ['recursive-93', 'recursive-94']
- Q: How are narrow and broad spurious lines defined?
  facts found: 2/2 · hit: True
  retrieved: ['recursive-90', 'recursive-96']
