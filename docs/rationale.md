# Rationale

Why a decision made explicit is worth more than the effort of making it, at
every scale from an architecture to a line, and what that has to do with
working alongside language models.

The README says why the standard exists; this document follows the idea past
it rather than restating it.

## Three scales of the same decision

A codebase answers one question at several scales: what has been decided here,
and what does a change have to respect?

An architecture answers it at the largest scale.

A domain model names each concept once and keeps each rule in one place, a
port declares a dependency on the outside world where the application needs
it, and an event names the one place where two processes meet and the delivery
guarantee that holds there.

A contract answers it at the scale of a call: a type annotation or an
interface says what a caller may pass and what it gets back, which would
otherwise have to be inferred from the implementation.

A convention answers it at the scale of a line: how a signature is laid out,
what a comment is for, which spelling a document uses, each decided once
rather than at every occurrence.

The three are not interchangeable, and a project can have good reasons to do
without any of them.

What they share is the effect: a later change starts from what was decided
instead of rediscovering it.

## What a settled boundary buys

Take the adapter behind an existing port that the README uses as its plain
case, and follow what each participant gets from the boundary.

Whoever writes it, a person or a model, still has to verify the contract and
understand the behavior around it, but the starting point is one boundary and
not the architecture.

Whoever reviews it reads that one boundary rather than all of them, and spends
the attention on whether the adapter is right instead of on where it belongs.

The same boundary lets work be divided: once a port is settled, its domain
behavior, its adapters, and its contract tests can proceed apart and meet at
the contract.

That is a property of the boundary and not of how many hands or sessions are
at work; without one, parallel work only multiplies the assumptions that have
to be reconciled later.

## Comprehension debt

Comprehension debt is the distance between a system as it is and what the
people working on it can explain of it: its structure, its constraints, how
its parts interact, and what a change will do to all of that.

It does not show up as a failure: the tests can pass over code nobody
understands, and the cost arrives later, as the inability to make the next
decision safely, because nobody can reason about a change to code they cannot
read.

It accumulates wherever a system grows faster than it is understood, through
haste, through inheritance, through many hands, and generation accelerates
that growth because a draft has become cheaper than the understanding of it.

Structure made explicit in advance is the alternative to paying the debt
afterward: a reader returning to an unfamiliar module reads a form already
known and spends the attention on what the module does, a reviewer finds the
boundary a change crosses instead of reconstructing the design, and the reason
behind a decision outlives the code it justified.

This standard removes one class of decisions from what has to be rediscovered
at every change, layout, naming, comments, docstrings, imports, and the form
of a commit, and it takes no architectural decision at all.

What remains is the larger part: the structure, the constraints, and the
interactions still have to be understood, and a convention makes that reading
cheaper without doing it.

## What a model gets from it

A model knows about a project only what it is given, and nothing it was told
last time carries over on its own, which is why the README's point about an
incomplete context weighs more for a model than for a colleague.

Most sources of a wrong result lie around the model rather than inside it: a
context that left something out, a requirement that allowed two readings, an
assumption the engineer brought in, a check that was never run at the layer
the claim is about.

Each of those has its own remedy, and none of the remedies is specific to
generated work: a structure that makes the relevant part of the system
visible, a requirement written before the implementation, a decision recorded
with its reason, and a check with a positive control.

A standard with a checker is the smallest of those remedies: the rule is
stated once, the reason travels with it, and the checker rejects the specified
violation whether or not its author, person or model, believed the change
conformed.

What it does not do is as definite: it does not eliminate comprehension debt,
it does not catch a wrong assumption the rules never reach, and it does not
decide whether a change means what it should, which remains the work of
review.

## The economics

When an adapter, a test, or a localized change costs little to draft, the
share of the work that is understanding, integrating, and reviewing grows, and
a boundary that lowers those costs is worth more relative to the effort of
keeping it than it was when the draft was the expensive part.

That does not make more structure always better, because every abstraction
costs something to build and to carry, and a boundary nobody crosses twice
pays for nothing.

The claim is conditional: explicit structure becomes a better investment where
it reduces the future cost of understanding, integrating, reviewing, and
changing a system, and a worse one where it does not, which is a question each
project answers for itself.
