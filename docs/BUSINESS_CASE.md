# Business case

## The question behind the project

A retention team can see that customers are leaving and still be uncertain about its next action. An overall churn percentage does not show whether departures are concentrated among new customers, particular contracts, service subscriptions or billing arrangements. Choosing an intervention before examining those differences can lead to a broad offer that is expensive and poorly targeted.

Customer Churn & Retention Analytics provides an initial descriptive review. It uses the classic IBM Telco sample to count customers consistently, compare groups and identify questions worth investigating. The sample contains 7,043 records and a supplied `Churn` label. The analysis does not observe a real retention programme or establish a current operational problem at a particular company.

The intended output is a reasoned investigation priority: a manager should be able to explain why a group deserves attention, how many customers it contains, and which additional evidence is needed before acting.

## Users and their decisions

| User | User story | Useful outcome |
| --- | --- | --- |
| Retention manager | I want to compare recorded churn across customer groups, so I can decide where to investigate first. | A finding supported by both a rate and a customer count. |
| Customer operations analyst | I want to inspect the preparation rules and denominators, so I can reproduce and challenge a result. | Traceable source data, explicit definitions and summary tables. |
| Service or billing lead | I want to know whether a pattern warrants a closer review of our process, so I can identify evidence to collect. | A focused question about onboarding, service experience or billing. |
| Technical reviewer | I want to distinguish executed analysis from supplied implementation materials, so I can assess what has actually been demonstrated. | A runnable Python reference path and clear SQL Server/Power BI validation boundaries. |

## What the sample shows

Across the full sample, **1,869 of 7,043 customers are marked as churned**, giving an observed share of **26.54%**. The other 5,174 have `Churn=No`. These figures are labels within the supplied snapshot, not a current customer register.

Month-to-month customers are the clearest initial concentration by contract. They account for **1,655 churned records among 3,875 customers**, or **42.71%** within that group. One-year customers show 11.27%, and two-year customers show 2.83%. The differences justify closer review, but contract groups also differ in tenure and potentially in characteristics that the sample does not record. The comparison does not tell us how many departures a contract change would prevent.

The **1–12-month tenure group contains 1,037 churned records among 2,175 customers**, or **47.68%**. This supports a question about early customer experience: what happens during onboarding, activation and the first billing cycles? It does not measure the probability that a newly acquired customer will leave in the next year. A tenure comparison is a cross-sectional view of different customers, not a longitudinal retention curve.

Fibre-optic customers have a recorded churn share of **41.89%**; electronic-check customers have a share of **45.29%**. These categories overlap with contract and tenure groups. Adding their churn counts together would count some people more than once. Higher shares suggest service and billing questions, not a finding that a technology or payment method caused churn.

Figures come from the [pinned source](../data/source.json) and are reproduced by [the Python workflow](../scripts/build_project.py). The repository's `reports/` directory contains the resulting summaries after a build.

## How a manager could use the findings

The first decision is where to spend investigation effort. Rate and volume answer different parts of that decision. A high rate can identify an unusual group; a large count can identify a substantial concentration of departures. Neither alone establishes the best intervention, because the dataset does not include intervention cost, eligibility, customer preference or expected benefit.

The dashboard therefore presents rates with their denominators and lets the analyst examine contract and tenure together. That reduces the chance of treating a broad customer-mix difference as a simple service failure. Further segmentation remains observational: a pattern within a narrower group is still not proof of cause.

| Observed pattern | Next investigation | Additional evidence needed | A possible future test |
| --- | --- | --- | --- |
| High churn share among customers with 1–12 months of tenure | Review onboarding and the first billing experience. | Activation delays, early support contacts, complaints and cancellation reasons. | Test a targeted onboarding check-in for eligible current customers. |
| Large concentration in month-to-month contracts | Examine who chooses these contracts and how experience differs within tenure groups. | Offer eligibility, pricing history, contract choice and customer preferences. | Test an appropriate offer against a comparison group, including its cost. |
| Elevated share among fibre-optic customers | Review service experience and customer mix. | Outage history, support resolution, installation issues and plan details. | Evaluate a specific service improvement where a documented issue exists. |
| Elevated share among electronic-check customers | Investigate billing friction and payment problems. | Failed payments, bill disputes and payment-channel experience. | Test a clearer billing or payment-support intervention. |

These are proposals for further work. The sample does not contain the additional records, and this project has not run the tests or measured their effects.

## Moving from a finding to a retention pilot

An eventual pilot would need a defined population of eligible current customers. The historical `Churn=No` rows in this sample do not establish who is active or contactable now. A real implementation would use current operational data and applicable contact permissions.

Before testing an intervention, the team would agree on the problem, the offer or process change, the observation period and the comparison method. Random assignment, where appropriate, could help distinguish the intervention's effect from differences between customers who do and do not take part.

Success measures might include retention over the agreed period, offer uptake, customer complaints and the cost of the intervention. Those measures belong to the future pilot. The current analysis provides no achieved retention lift, revenue saved or return-on-investment estimate.

## Why the preparation decisions matter

The source contains 11 blank `TotalCharges` cells. All appear on zero-tenure records marked `Churn=No`. The workflow keeps those customers and preserves the missing values. This maintains the full 7,043-customer denominator while avoiding an unsupported assumption that an unknown cumulative charge equals zero.

Charge-based calculations would need to state their coverage. There are 7,032 known `TotalCharges` values, so a sum or average of that field does not have the same completeness as the churn count. The separate zero-month tenure band makes this small group visible instead of hiding it in the first-year comparison.

The same care applies to service categories. `No internet service` is a meaningful account state. For a comparison of TechSupport adoption, the workflow restricts the population to internet subscribers and states that scope. It does not treat every customer without internet as someone who declined a support product.

## What has been demonstrated

The Python reference implementation prepares the sample, calculates the measures and produces original static dashboard figures. The SQL Server scripts and Power BI materials express the intended native implementation and still require execution in those applications. The original Power BI file is unavailable and is not included in this refreshed repository.

The portfolio value is the connection between a business question, reliable preparation, transparent measures and an explainable recommendation. A reviewer can inspect the calculations and see where the analysis ends and a new operational investigation would begin.

## A short explanation for a manager

> I looked at 7,043 customers in IBM's Telco sample to understand where recorded churn was concentrated. Month-to-month contracts and customers in their first year stood out, so I would begin by examining early service and billing experience in those groups. I kept the customer counts and preparation decisions visible so the findings can be checked. The report identifies questions to investigate; a separate pilot would be needed to establish whether a proposed action improves retention.
