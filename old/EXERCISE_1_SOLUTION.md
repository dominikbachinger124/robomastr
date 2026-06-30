# Exercise 1 Solution: Priming Command

**Purpose**: Reference solution demonstrating best practices for the priming command exercise

---

## Important Note

This is an **example solution**, not the "correct" answer. Your solution may differ based on your preferences and use cases. The key is applying the pattern correctly: **output optimized for you (human)**.

---

## Solution: Priming Command for Tool Development

**File**: `.claude/commands/prime-tools.md`

```markdown
# Prime for Tool Development

Load tool development patterns from in the reference folder to prepare for building agent tools.

## Context

You are about to work on building or modifying agent tools that will be used by Pydantic AI agents. Load the comprehensive patterns and best practices we established in Module 3 for writing agent-optimized tool docstrings.

## Read

Read the tool docstring patterns: @adding_tools_guide.md

## Process

Understand and internalize:

1. **Core Philosophy** - How agent tool docstrings differ from standard docstrings
2. **7 Required Elements** - One-line summary, "Use this when", "Do NOT use", Args with guidance, Returns, Performance Notes, Examples
3. **Agent Perspective** - Writing for LLM comprehension and tool selection
4. **Token Efficiency** - Documenting token costs and optimization strategies
5. **Anti-patterns** - Common mistakes that confuse agents
6. **Template Structure** - The exact format to follow

Pay special attention to:

- "Use this when" (affirmative guidance for tool selection)
- "Do NOT use" (negative guidance to prevent tool confusion)
- Performance Notes (token costs, execution time, limits)
- Realistic examples (not "foo", "bar", "test.md")

## Report Back

Provide a concise summary with:

### Key Principles (5 bullets max)

- [What are the core principles you understood?]

### Critical Distinctions

- [What makes agent tool docstrings different from standard docstrings?]
- [Why does "Do NOT use" matter?]

### Template Internalized

- [Confirm you understand the structure you'll follow]

### Ready to Apply

- [One sentence confirming you're ready to write agent-optimized tool docstrings]

Keep it scannable - I want to verify understanding in 30 seconds.
```

---

## Why This Solution Works

**For Exercise 1 (Context Loading for Humans):**

✅ **Clear context setting**

- Agent knows WHY it's loading this information
- Establishes the upcoming work context

✅ **Specific reading instruction**

- Uses `@` file reference to load content
- One clear file to read

✅ **Focused processing**

- 6 specific things to understand
- Prioritizes most important elements
- Highlights critical sections

✅ **Human-optimized output**

- Scannable structure (headers + bullets)
- Concise summaries (not full regurgitation)
- Quick verification points
- 30-second scan target

✅ **Verification built-in**

- "List the 7 elements" - checks comprehension
- "Critical distinctions" - checks understanding
- "Ready to apply" - confirms readiness

**What makes it work for humans:**

- Bullet points for scanning
- Headers for structure
- Concise not verbose
- Verification questions
- Quick confidence check

---

## Using This Solution

**Don't copy blindly!** Instead:

1. **Understand the pattern** - Why each section exists
2. **Adapt to your needs** - Your workflow and context
3. **Test with real use** - Does it actually work for you?
4. **Iterate and improve** - Refine based on experience

The best command is the one that works for YOUR workflow.

---

## Reflection: Pattern Recognition

This exercise applied the Input → Process → Output framework optimized for human consumption:

- **Input**: Tool patterns document
- **Process**: Read and understand
- **Output**: Human-readable summary for verification

**Key insight:** When the output consumer is a human, optimize for scanning, conciseness, and quick verification.
