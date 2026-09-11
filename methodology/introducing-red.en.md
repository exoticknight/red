# Introducing RED: A Methodology for AI Understanding

[中文原文](introducing-red.md) · English

**Abstract:** This paper presents RED, a methodology for collaboration with AI. RED organizes project knowledge into three states: Research, which addresses unknowns; Evolve, which develops changes; and Document, which preserves accepted understanding. Its central argument concerns the gap between an AI's flat conversational context and the distinctions people make when organizing knowledge. By making knowledge states explicit, RED helps an AI distinguish facts, hypotheses, and decisions, and maintain an understanding of a project without relying on an ever-longer context window. The methodology grew out of AI-assisted programming, but its principles apply to other kinds of cognitive work that people and AI undertake together.

---

You ask an AI to add CSV export to a project. In the first conversation, it understands the task and produces working code. Two weeks later, you ask it to change the exported fields. It starts changing the format on its own. After three unsuccessful attempts, you discover that it has been following a passing remark you made three months ago.

Its context has become polluted. The conversation is long, old decisions sit alongside new ideas, and no document tells it which statements represent settled decisions and which were passing suggestions.

We began working extensively with AI programming after the release of GPT-4o. Across personal projects, team collaboration, prototypes, and production maintenance, hundreds of conversations and repeated experiments on dozens of projects brought one problem into focus: **sustaining a correct understanding of the project had become a greater obstacle than generating code.**

We tried feeding the AI the entire conversation history, pasting the README into every session, and relying on longer context windows. In our experience, projects could begin to drift after only a few days. Through repeated attempts, we developed a way to separate project knowledge by state, so that the AI could draw on different kinds of context for different purposes. We call it RED.

Many implementation details remain open to discussion. This paper explains the underlying ideas.

## 1. Four recurring difficulties in AI collaboration

If you have used AI extensively in a project, you may recognize these situations.

**The AI loses track of the project's foundations.**

At the start of a new conversation, the AI does not know what the project is for, why you designed it this way, or who will use it. You paste in the README. It reads it, but later in the conversation it loses track of the opening context. By the third requirements change, it recommends an approach that conflicts with the project's direction.

**The AI fails to distinguish the authority of different statements.**

You give it design documents, conversation logs, and user feedback together. It treats a product manager's casual speculation like a confirmed requirement. You ask, “Should we consider supporting iOS?” It takes this as a commitment and adds iOS-specific interfaces to the code.

**People cannot inspect and correct the AI's understanding.**

The AI writes code that you know is wrong, but you cannot see how it has interpreted the project. Which assumptions led to this design? Which details did it infer from context, and which did it invent? You keep changing the prompt and generating another answer until you happen to get the right output.

**Conversations never reach a useful conclusion.**

You spend a long time analyzing a problem, comparing approaches, and developing ideas with the AI. Afterwards, the work tends toward one of two outcomes. Sometimes nothing happens, and the next conversation starts over. Sometimes you save every transcript and summary to prevent forgetting, creating a growing collection of repetitive documents with unclear status. In one case, you lose the value of the discussion; in the other, you create more context noise.

These difficulties point to a shared need: a structure that helps the AI maintain its understanding and helps people turn conversations into useful outcomes.

## 2. Why giving the AI more documentation is insufficient

A common response is to organize the documents and give them to the AI. In practice, that leaves several problems unresolved. We tried:

- Pasting the README: later in a long conversation, the AI lost track of the beginning.
- Supplying design documents: the documents could be outdated or too abstract to support concrete decisions.
- Supplying the entire conversation history: the AI could not reliably distinguish conclusions from discussion or passing suggestions.
- Generating a summary after every conversation: records accumulated without identifying what required action, what awaited confirmation, or what had become obsolete.
- Repeating “Only do what I tell you”: this reduced the AI's initiative and its ability to help identify problems.

At the knowledge-management level, the AI receives a flat stream of context. Confirmed requirements, casual ideas, its own guesses, and previously generated code all arrive as text. The conversation alone does not provide a dependable account of their authority.

People organize that knowledge through distinctions: concluded versus under discussion, committed versus worth considering, established project practice versus a temporary choice for this task. The gap between those distinctions and the context we provide creates confusion in collaboration.

The slogan “vibe coding” encourages people to guide AI coding by feel. In our experience, sustained work with that approach can become difficult within days. Without a baseline, boundaries, or maintained conclusions, each conversation asks the AI to guess the project's intent again.

RED starts by making the project's knowledge structure available to both people and AI.

## 3. The three knowledge states

RED classifies project content by **knowledge state**.

### R: Research

Research addresses **unknowns**.

A project contains many unanswered questions. What do users need? How does the existing system work? Is a proposed technical approach feasible? What do competing products do? Which claims rest on reliable evidence?

These questions appear at the beginning of a project and throughout its development.

Research provides a place for material that remains unsettled. It can include:

- Incomplete investigations.
- Questions that still lack an answer after investigation.
- Contradictory information from different sources.
- Personal judgments that may be wrong but are worth recording.

Research can remain private. It may consist of personal drafts, investigation notes, or external material that has not yet been organized. Its value comes from identifying uncertainty, so that an unverified claim does not quietly become the basis of a later decision.

The threshold for entering Research is low. The material need not be verified, but its status must be represented honestly.

### E: Evolve

Evolve addresses **change**.

When a project decides to pursue a feature, design adjustment, architectural change, or new rule, the details may still need development before they belong in maintained documentation.

Evolve holds that work as it takes shape. It usually includes:

- The problem or opportunity motivating the change.
- Candidate approaches and their tradeoffs.
- The affected parts of the project.
- Acceptance conditions.
- Unresolved questions.

People and agents can revise Evolve material throughout the work. Several approaches may coexist. A rejected approach can remain there with the reasoning behind its rejection.

Evolve has a higher entry threshold than Research: supporting facts cannot consist of unmarked guesses, and assumptions must be identified as assumptions. A change can enter Evolve directly when the problem and objective are clear. Research is needed when an unknown could affect the choice of approach.

Evolve includes the work of developing a proposal into an accepted change: design, programming, testing, trial use, revision, and discussions between people and AI about tradeoffs.

### D: Document

Document addresses **accepted understanding**.

When project participants, including AI agents, need to know what the project should be and which goals, rules, and constraints remain in force, Document is the normative source. It expresses the project's current agreements and commitments. Its description of the running system may still be incomplete or inaccurate.

Document contains confirmed knowledge that participants can rely on:

- Project goals and boundaries.
- Core concepts and terminology.
- Usage and APIs.
- Design principles and engineering rules.
- Contribution practices.

Document gives newcomers and existing participants a common entry point. A new contributor should use it to understand the project. An AI should begin each task with the relevant Document sources to establish a baseline, then load related Evolve material, Research, code, and tests as needed. It need not reread the entire project history.

Document changes as the project changes. Altering the agreement it expresses requires discussion and acceptance through Evolve. Corrections and formatting changes that preserve meaning can proceed directly. Research drafts and provisional Evolve proposals need resolution before their conclusions belong in Document.

Document has the highest entry threshold: its contents should have sufficient verification and acceptance to support continued use and long-term reading.

## 4. How the states work together

A typical route in an existing project looks like this:

```text
Current Document + implementation evidence
                    |
           Problem, request, or conflict
                    |
       +------------+-----------------------+
       |                                    |
Critical unknowns                    Clear goal and boundaries
       |                                    |
Research: investigate                        |
       |                                    |
Human authorizes Evolve                      |
       +----------------+-------------------+
                        |
          Evolve: design, implement, test, revise
                        |
          Present evidence and proposed Document changes
                        |
                  Wait for acceptance
                        |
          Update Document and align the implementation
```

Document provides the starting point for normative understanding and the place to preserve accepted conclusions. Code, tests, and runtime results provide implementation evidence. People and AI use them to detect differences between actual behavior and the project's agreements. Work begins from the current baseline and verifiable implementation state, and ends with the implementation and Document aligned.

Choose the route according to the knowledge state. Work does not have to pass through every state in sequence. A person can authorize a clear change directly in Evolve. Routine implementation under existing Document, or a small correction that preserves meaning, may not need a separate Evolve record. Use Research when an unknown could change the decision or acceptance conditions. Persist Research or Evolve in files or another system when work needs review, handoff, or continued tracking.

Route selection is flexible; transitions require an explicit decision. When an AI's Research findings support a proposal, it presents the findings, risks, and suggested scope, then pauses in Research. A person confirms whether the work should enter Evolve. Within the authorized scope, the AI can continue designing, coding, testing, and discussing the work. Once acceptance conditions are met, it presents evidence and the proposed Document changes, then waits for acceptance. It updates Document only after a person or the project's designated decision process accepts the result. A broad instruction at the beginning of the task cannot supply those later decisions before the results exist for review.

Consider a command-line task manager whose Document specifies JSON storage. A user asks to add tags to tasks. The request leaves enough uncertainty that it needs clarification before it can become an accepted requirement or an implementation task.

Start with Research. How often has the request appeared in issues? Does “tag” mean a category or a priority marker? How do other tools handle it? The investigation may remain incomplete or overturn earlier assumptions. The AI reports what it found, and you decide whether to enter Evolve and what scope to pursue.

After that decision, compare an approach using `+tag` syntax with one using a `--tag` option. Record their tradeoffs, affected components, and compatibility with old data. Both approaches can remain in Evolve while you decide. Once the boundaries are clear, the AI implements the change, adds relevant tests, and revises it in response to feedback.

When the acceptance conditions pass, the AI presents the results and proposed documentation. After you or the team accepts the result, update Document with the `tags` field and command examples. Preserve the accepted behavior there; keep the investigation and discussion history in their working records.

Research and Evolve need not be visible to everyone. Personal notes and short experiments can stay local. Work that needs shared review or continuation can use Git, issues, pull requests, or another collaboration system. Each project chooses how to share it, while Document remains the common source of accepted understanding.

RED does not prescribe whether file-based Research and Evolve belong in Git. Tracking them does not change their knowledge state or turn them into Document.

### Bringing a conversation to a conclusion

RED does not require saving every conversation. A conversation is a temporary workspace for a person and an AI. It does not inherently belong to Research, Evolve, or Document. Persist material when someone will need to use it across tasks, people, or time.

At the end of a substantive conversation, the AI should help account for its outcomes:

| Outcome | Treatment |
|---|---|
| An unresolved question that affects later choices | Keep it in Research with evidence, assumptions, and unknowns |
| A change the participants have decided to pursue | Develop it in Evolve through a plan, actions, implementation, and acceptance conditions |
| Accepted understanding that future work will depend on | Update Document to establish the new baseline |
| Digressions, repetition, and temporary drafts with no future use | Let them go when the conversation ends |

Moving material into a state does not require creating a new file. A small change that fits within the current task may become code, tests, or a revision to existing documentation. Create a separate Research or Evolve record when it helps with handoff, review, or further tracking. Document preserves accepted conclusions that remain valid, rather than the complete process that produced them.

The aim is to account for the conversation's work: retain questions worth investigating, turn intended changes into action, preserve accepted understanding, and let the rest expire. This avoids both losing useful work and retaining the same unresolved problem in a growing collection of summaries.

If a proposal is rejected, Document stays as it is. Keep tradeoff reasoning with lasting value in Evolve or the project's chosen collaboration system. Short-lived experiments can end. If only part of a proposal is accepted, Document should reflect that accepted scope.

Code and tests are executable evidence throughout this process. They do not form a fourth knowledge state. During Research, people use them and runtime results to investigate the system. During Evolve, they help validate candidate approaches and acceptance conditions. After acceptance, they help establish whether implementation matches the agreement.

Document describes what the project should be; code and tests show how the system currently behaves. Either can be incomplete or outdated. Investigate conflicts in Research, then enter Evolve if resolving them requires a project change. The existence of code does not make its behavior an accepted requirement, and a written requirement does not justify ignoring contradictory implementation evidence.

The four difficulties from the opening now have corresponding practices:

| Difficulty | RED practice |
|---|---|
| Losing the project's foundations | Begin with a maintained Document baseline |
| Treating speculation like a requirement | Apply explicit entry criteria to each knowledge state |
| Being unable to inspect the AI's understanding | Review Evolve proposals and Document changes rather than guessing at hidden reasoning |
| Leaving conversations unresolved | Account for outcomes as unknowns, actions, accepted understanding, or material to discard |

## 5. Why this structure remains useful

It is reasonable to ask whether a sufficiently large context window could make this structure unnecessary. If a model could hold one million, ten million, or a billion tokens, could it remember everything about a project?

Three distinctions matter.

First, retaining information does not establish how to use it. A larger window helps only with material that has been loaded. Information omitted from a new conversation remains unavailable. Even when the complete history fits, the model needs to distinguish current agreements from obsolete designs, rejected proposals, and records of bugs that have since been fixed.

Second, larger windows can increase the amount of competing material. The AI encounters more facts, discussions, and historical records at once. Without explicit indications of what has expired, what remains under discussion, and what participants currently accept, the additional context can make judgment harder.

Third, the authority of a statement may depend on facts outside its wording. “Should we consider supporting iOS?” does not, by itself, establish whether the speaker was making a suggestion or recording a decision. That status comes from the collaboration process and the judgment of its participants.

Larger models and context windows improve how much information an AI can extract from text. RED provides information about the status that participants assign to that text. These capabilities address different parts of the problem.

People make such distinctions in ordinary work. “Write that down so we can check it later” and “We have decided; proceed on that basis” lead to different actions. We classify the information and give it different authority. An AI needs us to make those distinctions explicit in the material it uses.

RED turns that practice into rules an AI can follow:

- **Document contains accepted understanding.** The AI relies on it by default. If verifiable evidence conflicts with it, the AI reports the conflict and routes it through Research or Evolve instead of disregarding or rewriting the baseline on its own.
- **Evolve contains understanding in development.** The AI participates in shaping it while keeping provisional choices distinct from final commitments.
- **Research contains unsettled material.** The AI uses it to guide investigation and keeps unverified claims from becoming decisions.

Making the status explicit gives both participants a shared basis for the next action.

## 6. Beyond AI programming

RED grew out of programming, but investigating unknowns, developing changes, and preserving accepted understanding also occur in other kinds of collaborative work.

For a market analysis, use Research to gather missing data, conduct interviews, and examine competitors. In Evolve, develop the analytical framework and revise the analysis. The accepted report becomes Document. In strategic planning, investigate unknowns that could alter the direction, compare options in Evolve, and preserve the agreed strategy in Document. In teaching, investigate students' backgrounds or unfamiliar materials when necessary, then develop lesson plans, try them, and revise them before establishing the course materials and syllabus. With reliable source material and clear delivery criteria, any of these tasks can enter Evolve directly.

These activities share a familiar pattern: explore, narrow the choices, and preserve the result. AI programming has accelerated that pattern and made its consequences more visible. RED describes a process that people often leave implicit but need to make explicit when collaborating with AI.

## 7. Conclusion

Return to the CSV export example. A passing remark from three months earlier became a rule because its status was never established. It was neither an identified Research hypothesis, an Evolve proposal under discussion, nor an accepted agreement in Document. It remained an unclassified statement in the conversation.

RED makes that missing status explicit. The participants can distinguish “we do not know yet,” “we are working through this,” and “we have accepted this.” The AI has less reason to guess at the authority of a remark. People can review the developing proposal and the proposed changes to accepted understanding, instead of repeatedly correcting an interpretation they cannot inspect.

Someone still has to make and maintain those distinctions. Longer context windows, retrieval, and stronger reasoning cannot establish an agreement that the participants have never made explicit. People remain responsible for confirming the status of project knowledge.

RED gives their judgment a form the AI can recognize: whether it is working with an idea that is still taking shape or an agreement it is expected to follow.
