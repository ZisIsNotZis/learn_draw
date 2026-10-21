# mail/ — this project's mailbox

A message for this project sits here as one markdown file per message, under version control. The
box is read before any other work in a session: an unread message can change the roadmap, so it
outranks whatever was about to be started. Reading it means landing it — the fact into the document
that owns the decision, the order carried out — and then deleting the file and committing. Deletion
is tidying, not a reply.

## File shape

Name: `YYYY-MM-DD-<slug>.md`. Four header lines, then a blank line, then the body:

```
kind:    report | resource | cost | direction | contract
from:    <agent or node name>
to:      <agent or node name>
spend:   <spend class: idle-compute | person-attention | money | time …>
id:      <the id of the message this answers, or "none — <why>">

<body: the question or the order, and nothing else>

<effort: what answering costs, or "none">
```

- `kind` sets the route: `resource` goes up to whoever holds the budget, `cost` to whoever owns the
  commitment, `direction` to the person unchanged, `contract` to the parent that wrote the contract.
- `spend` is this message's own price; `effort` at the end is what the answer costs the receiver.
- A report names what is now true, its evidence pointer, and the decision needed, which may be none.
