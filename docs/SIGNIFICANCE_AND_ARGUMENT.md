# Significance first: the three-step "So what?" formula and five-part argument

The research lab treats two different questions separately:

1. **Is this a worthwhile question to ask?** Frame reader significance *before* building an experiment.
2. **Does the completed argument withstand scrutiny?** After evidence exists, test its claim, reasons, evidence, alternative explanations, and inference.

This is a way to direct scientific effort toward consequential understanding and to detect missing pieces in an argument. It is not an automated measure of publication impact, novelty, causality, or correctness.

## Stage 1 — Reader significance: name topic, question, and significance

The statement is built from exactly three parts:

> **I am studying** [a concrete phenomenon]
>
> **because I want to find out** [a precise question or unknown relationship]
>
> **in order to help my reader understand** [a wider consequence, relationship, or decision].

**Worked illustrative example** (a potential industrial-AI question, not a claim of novelty):

- **Topic:** how industrial forecasting model-selection procedures behave when replenishment lead times vary
- **Question:** whether a cheaper predeployment screening method can identify selections likely to produce high inventory-decision regret
- **Reader significance:** when operations teams can safely rely on benchmark rankings and when they need additional decision-oriented validation

As a single sentence:

> I am studying how industrial forecasting model-selection procedures behave when replenishment lead times vary **because I want to find out** whether a cheaper predeployment screening method can identify selections likely to produce high inventory-decision regret **in order to help my reader understand** when operations teams can safely rely on benchmark rankings and when they need additional decision-oriented validation.

This is a **research proposal**, not a proven fact or original contribution. Similar questions may already be resolved by literature. The separate novelty and feasibility gates still apply.

### Three failure modes to challenge

- **Topic is not a question:** "I am studying AI forecasting because I want to study forecasting." No unknown is specified.
- **Significance describes the author instead of the reader:** "in order to build a portfolio, get a paper accepted, or show my skills." These may be motivations but are not reader contributions.
- **Significance is only a performance number:** "to raise accuracy by 2%." Explain what understanding or decision changes, not only that the metric might improve.

### Run framing preflight

First scaffold any question:

~~~bash
python -m research_lab.study init your-question --title "Your precise research question"
~~~

Fill the first three sections of \`research/your-question/significance.md\`. Then run:

~~~bash
python -m research_lab.study preflight your-question --stage framing
~~~

The command exits with status **2** and specific missing sections if the worksheet is empty, too short, repetitive, or contains placeholders. It exits **0** only when all three sections are populated. Status \`READY_FOR_HUMAN_REVIEW\` means a reviewer can now assess the framing; it **does not mean** that the topic is objectively important or novel.

## Stage 2 — The five questions every scientific argument must answer

After results exist, write a claim supported by **actual evidence**, not the hoped-for outcome.

| Element | Reader's question | What must be written |
|---|---|---|
| **Claim** | What is your point? | Specific, scoped assertion supported by the research |
| **Reasons** | Why should I believe it? | Mechanism, logic, and supporting observations |
| **Evidence** | How do you know that? | Verifiable sources, result artifacts, quantitative estimates, proofs, uncertainty |
| **Acknowledgement & Response** | But what about this other idea? | A credible competing explanation and a fair evaluation of it |
| **Warrant** | How does your "why" connect to the point? | Inference explaining why the evidence supports this claim, and its boundaries |

**Illustrative structure (not fictional empirical evidence):**

- **Claim:** In the tested settings, a screening method may identify decisions for which accuracy-led selection has high operational regret.
- **Reasons:** Accuracy and decision costs can weight errors differently under lead-time and inventory uncertainty.
- **Evidence:** *Not yet available.* Run a version-pinned, leakage-controlled study and cite its exact result artifact, uncertainty and independent baseline comparison. **Do not claim the result before observing it.**
- **Acknowledgement & Response:** Existing forecast-congruence techniques or partial policy replay may explain any observed improvement; match their compute budgets and compare them directly.
- **Warrant:** Even an observed association would support only a scoped warning rule within the tested decision regimes, not proof of general industrial benefit.

Because the evidence is **not yet available**, this example should **fail** the argument preflight. That is correct behavior.

### Run argument preflight

When evidence and a critical review exist, fill all five argument sections of the same worksheet:

~~~bash
python -m research_lab.study preflight your-question --stage argument
~~~

A successful structural check requires complete, substantive text and an **inspectable evidence locator**, such as a source DOI or URL, \`runs/.../results.json\`, or a stated mathematical proof. It cannot verify the actual source or validate the inference. The reviewer must still do that.

## How this integrates with other gates

- The \`study init\` command creates \`significance.md\` with explicit placeholder sections.
- \`study preflight\` checks framing or argument separately.
- \`study run\` still allows a toy exploratory execution with incomplete framing and records the current framing preflight status in the run manifest. This is intentional: the framework can be smoke-tested while the science is not yet ready.
- The Codex hypothesis-generation skill demands reader-facing significance; the independent-review skill tests the five reader objections.
- Proposal and critical review templates use the same vocabulary, preventing the writer from losing the question's reader-facing purpose.
- A human reviewer can still reject a perfectly populated worksheet because of weak external significance, unsupported evidence, invalid methodology, novelty overlap, or poor inference.

## Checklist for a genuine scientific result

The strongest chain is not "a model beat another model." It is:

**Reader-relevant question → competing hypotheses → suitable evidence → defensible scoped claim → alternative explanations → explicit warrant → independent review.**

If a study offers only a performance number, ask what it changes about a reader's understanding. If the claim lacks a credible warrant, narrow the claim or improve the evidence. If novelty is absent, publish an appropriately labeled replication or reusable benchmark rather than asserting a discovery.

This worksheet follows the three-part reader-significance formula and five reader objections supplied for the project; it does not itself establish authorship or originality of those concepts.
