# Exercise 1: Build a Priming Command


## Goal

Create a priming command that loads tool development patterns from the reference folder into the agent's context, so when you're building tools, the agent already knows the patterns to follow.

---

## The Problem


Every time you start a new session to build a tool, you have to:
- Manually tell the agent to read that file
- Explain what patterns to follow
- Re-establish the context every time

**This is re-prompting!** Perfect use case for a command.

---

## Your Task

Build a priming command that:
1. Loads the tool patterns from the reference folder
2. Gives the agent context about when to use these patterns
3. Produces human-readable output so YOU can verify understanding

---

## Step-by-Step Instructions

### Step 1: Create the Command File (5 min)

Create: `/commands/prime-tools.md`

```bash
mkdir -p /commands
touch /commands/prime-tools.md
```

> This is for Claude Code, customize this to your AI coding assistant.Please adapt it to opencode.

### Step 2: Apply the Agent Perspective Framework (5 min)

Design your command by answering:

**INPUT: What does the agent NEED to see?**
- The `adding_tools_guide.md` file content
- When these patterns apply
- What the agent should understand

**PROCESS: What should the agent DO?**
- Read the tool patterns document
- Understand the key principles
- Internalize the template structure
- Note the examples

**OUTPUT: What format do YOU want back?**
- Human-readable summary
- Easy to scan sections
- Confirms agent understanding
- You can quickly verify it "got it"

### Step 3: Write Your Command (5-10 min)

Use this structure:

```markdown
# Prime for Tool Development

Load tool development patterns from reference folder

## Context

You are about to work on building or modifying agent tools.
Load the patterns and best practices we established in Module 3.

## Read

Read the tool docstring patterns: @adding_tools_guide.md (make this a full path!)

## Process

Understand:
1. The agent should understand the project in it's core.
2. The agent should understand the underlying computing approach on how to get the project to life.
3. The agent now can understand the new tool I want him to implement in a way that it serves the projects intention and the way it works with the used code.
4. The agent should search for existing tools or best practices online covering the new tool.

## Report Back

Provide a human-readable summary with:
- Make a short yet precise explanation of all four bulletpoints from the section abouve.
- Make a Markdownfile that is easy to read.
- The agent should do some individual assumptions about the project which is not covered yet. For example when makeing a wattering solution for plant and there is no scheduling in the project so far, suggest a schedule. When the project is some stock analysis tool and there is no trend analysis, suggest the trend analysis.
```

## Testing Your Command

### Test 1: Basic Usage

Invoke your command:
```
/prime-tools
```

**Verify:**
- [ ] Agent read the file
- [ ] Output is easy to scan
- [ ] You can quickly verify understanding
- [ ] You feel confident the agent knows the patterns

### Test 2: Follow-Up

After priming, test if the agent retained the context:

Ask: "What are the required elements for agent tool docstrings?"

**Expected:** Agent should remember without re-reading the file.

### Test 3: Real Usage

Try building a simple tool after priming:

Ask: "Help me write a docstring for a tool that reads files"

**Expected:** Agent should follow the patterns from the primer.

---

## Common Mistakes

**❌ Too much output:**
```markdown
Report back: Summarize the entire document in detail
```
Result: 2000+ word summary you won't read.

**✅ Right amount:**
```markdown
Report back:
- Key principles (3-5 bullets)
- Required elements (list)
- One example of good vs bad
```
Result: Scannable summary you can quickly verify.

---

**❌ No verification:**
```markdown
Report: "I read the file"
```
Result: Did the agent actually understand?

**✅ With verification:**
```markdown
Report:
- Key principles you understood
- Template structure you'll follow
- Anti-patterns you'll avoid
```
Result: You can verify comprehension.

---

**❌ Vague instructions:**
```markdown
Read the file and understand it
```
Result: Agent doesn't know what to focus on.

**✅ Specific guidance:**
```markdown
Read and understand:
1. The 7 required elements (especially "Use this when" and "Do NOT use")
2. Why token efficiency matters
3. The template structure you'll follow
```
Result: Focused understanding.

---

## Success Criteria

Your priming command is successful if:

- [ ] You can invoke it in 10 seconds flat
- [ ] Output takes 30 seconds to scan
- [ ] You can verify agent understanding immediately
- [ ] Agent retains patterns for the session
- [ ] You never have to manually re-explain patterns

**The real test:** Next time you build a tool, start with `/prime-tools` and see if the agent follows the patterns without additional prompting.

---

## What You Learned

This exercise demonstrates **Pattern 1: Context Loading**

**Characteristics:**
- Loads information into agent's current context
- Output optimized for YOU (human)
- Conversational, scannable format
- Used at session start
- Sets up the agent for upcoming work

**Key insight:** Good priming commands save you from re-explaining patterns every session. They're an investment that pays off immediately.

---

## Next Step

Move on to Exercise 2 where you'll design a **Pattern 2: Document Creation** command that creates artifacts for OTHER AGENTS to consume.

The output optimization will be completely different!
