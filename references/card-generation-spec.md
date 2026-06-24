# Anki English Card Generation Specification

This reference is the source of truth for generating new English Anki cards with this skill.

## Goal

Generate concise Anki cards for English words, phrases, sentence patterns, and grammar structures. The cards should support vocabulary memory, not function as full dictionary entries.

Default target learner: Chinese-speaking English learner around A2-B1.

## Core principles

- Keep each card concise and atomic.
- Prefer high-frequency, useful meanings.
- Keep at most 3 core meaning units per card.
- Use daily, natural examples that are easy to understand.
- Use British English spelling and phonetics by default.
- Use the user's existing HTML structure.

## Terms

- `meaning line`: one HTML line using `<div class="meaning">...</div>`.
- `core meaning unit`: one actual sense that needs its own example.
- A meaning line can contain one or more core meaning units.
- The limit is 3 core meaning units per card, not 3 HTML meaning lines.

Example:

```html
<div class="meaning">n. 规模，程度；刻度，等级；鳞片</div>
```

This is one meaning line but three core meaning units.

## Front field rules

- Ordinary words and phrases default to lowercase: `commonly`, `put away`.
- Proper nouns keep normal capitalization: `Hong Kong`, `Vancouver`, `UNESCO`.
- British spellings are preferred: `colour`, `favour`, `metre`, `theatre`.
- If the user supplies a special front, such as a sentence pattern, grammar structure, Chinese cue, or POS restriction, preserve that front.
- If the front includes a POS restriction such as `mean (adj.)`, generate only the relevant meaning and examples.

## Back HTML structure

Use this structure:

```html
<div class="phonetic">/音标/</div>

<div class="meanings">
  <div class="meaning">词性 高频中文义</div>
  <div class="meaning">词性 高频中文义</div>
</div>

<div class="examples">
  <div class="example">英文例句</div>
  <div class="translation">中文翻译</div>

  <div class="example">英文例句</div>
  <div class="translation">中文翻译</div>
</div>

<div class="tip">Tip: 简短、具体、有记忆价值的补充。</div>
```

Omit the `tip` block when no useful Tip is needed.

## Phonetic rules

- Use British phonetics.
- Put phonetics in `/.../`.
- Put phonetics inside `<div class="phonetic">`.
- For phrases, provide a natural phrase pronunciation if reliable.
- If pronunciation is uncertain, do not invent it. Use `需核对英式音标`.

## Meaning rules

- Keep 1-3 core meaning units.
- Count core meaning units across the whole word or phrase, not separately per POS.
- Do not force 3 meanings when 1 or 2 are enough.
- Omit lower-frequency or less useful senses unless the user asks for them.
- Choose retained senses in this order:
  1. the sense explicitly requested or implied by the user's context;
  2. common everyday senses that a learner is likely to review and use;
  3. senses that require different examples, collocations, grammar patterns, or Chinese translations;
  4. exam-relevant or high-frequency specialised senses, only when they are useful for the user.
- Default to omitting rare, literary, archaic, highly technical, or dictionary-completeness senses.
- If more than 3 useful senses are possible, keep the best 3 by the priority above. Prefer fewer clear senses over 3 weakly useful senses.
- Different parts of speech must use different meaning lines.
- All retained senses with the same POS must stay on the same meaning line.
- Do not create two separate `v.` lines, two separate `n.` lines, etc.
- Same-POS similar Chinese glosses for the same English sense use commas.
- Same-POS different English senses use Chinese semicolons `；`.
- Count each semicolon-separated same-POS sense as one core meaning unit.
- A different-POS meaning line without a semicolon is also one core meaning unit.
- Do not list long synonym, antonym, or collocation sections.

## Comma vs semicolon

Base the decision on English sense, not on how different the Chinese translations look.

Use commas when several Chinese glosses translate the same English sense and can be shown by one natural English example.

Use semicolons only when the English word is used in genuinely different senses that need different contexts or examples.

Decision tests:

- Definition test: if the English definition is essentially the same, use a comma.
- Example-coverage test: before using a comma between Chinese glosses, check whether one natural English example can clearly cover all glosses. If not, they are different core meaning units and must be separated by a Chinese semicolon `；`.
- Scenario test: if each sense needs a different real-life situation, use a semicolon.
- Noun sense-boundary test: for nouns, especially check process/result, action/product, institution/system, field/discipline, person/group, and quantity/activity distinctions. These are usually different senses unless one natural English example clearly covers both.
- Domain test: if one meaning is everyday and another is domain-specific, usually keep only the useful high-frequency meaning.
- Register test: if the difference is only style or register, use a comma or explain it in Tip.
- Uncertainty rule: if unsure, first apply the example-coverage test. If one natural example clearly covers all glosses, compress them into one natural Chinese gloss with commas. If one example cannot clearly cover all retained glosses, use semicolons and provide one example for each semicolon-separated sense.

Examples:

- `n. 创作者，创造者` is one English sense for `creator`: a person who creates something. Use one example.
- `n. 建筑工人，建筑承包商；建造者，塑造者` has two English senses for `builder`: a construction profession and an abstract role. Use two examples.
- `n. 时期，阶段；句号` has two English senses for `period`. Use two examples.
- `n. 规模，程度；刻度，等级；鳞片` has three English senses for `scale`. Use three examples if all three are retained.
- Wrong: `n. 生产，产量` with only one example such as `Food production has increased in recent years.` This covers the quantity/result sense but not the production-process sense.
- Correct: `n. 生产，制作；产量，生产量` with one example for the production process and one example for output quantity.

## Example rules

- Maximum: 3 examples.
- Example count should match the number of retained core meaning units.
- A simple one-sense word should have exactly 1 example by default.
- A card with 2 retained core meaning units should have 2 examples.
- A card with 3 retained core meaning units should have 3 examples.
- If a word has more than 3 possible senses, keep only the best 3 senses and write exactly 3 examples for those retained senses.
- Example order must match meaning order.
- If same-POS different English senses are separated by semicolons on one line, examples must cover those senses in order.
- If a retained meaning cannot be shown with a useful example, remove that meaning.
- Do not add POS labels at the end of examples.
- Avoid mechanical examples such as:
  - `People often ... this problem.`
  - `The ... is important here.`
  - `The situation is ...`
  - `Please ... today.`

## Translation rules

- Every English example must have one Chinese translation.
- Translation should be natural and accurate.
- Do not translate word by word if the result is unnatural.
- Keep translations short and useful for memory.

## Tip rules

Tip is optional and should be absent by default.

The purpose of Tip is to warn the learner about the easiest place to misremember, misuse, or confuse the target word or retained sense.

Add Tip only when the target word or retained sense clearly belongs to one of the 8 categories below. If it does not belong to one of these categories, do not add Tip.

Each card may have at most 1 Tip. If a word fits multiple categories, choose only the category that most reduces likely misuse.

Priority order:

1. common learner mistake
2. preposition pattern
3. fixed collocation
4. countable or uncountable noun warning
5. non-literal Chinese-English mismatch
6. easily confused word
7. near-synonym usage boundary
8. context, register, or formality

### Tip category details

1. Common learner mistake
   - Use when the word has a typical learner error, such as a wrong structure, wrong object, or wrong expression.
   - Prefer a "do not say A; say B" pattern.
   - Example Tips: `Tip: discuss 后面直接接宾语，不说 discuss about something。` `Tip: enter 后面直接接地点，不说 enter into the room。`

2. Preposition pattern
   - Use when the word normally takes a fixed preposition and learners often choose the wrong one.
   - Write only the core preposition pattern; do not list many variants.
   - Example Tips: `Tip: 常说 be interested in something，不说 interested about。` `Tip: depend 后面通常接 on：depend on someone/something。`

3. Fixed collocation
   - Use when the meaning is not difficult, but the word strongly prefers a common collocation and the wrong collocation sounds unnatural.
   - Give only the most common or most error-prone collocation.
   - Example Tips: `Tip: 常说 make a decision，不说 do a decision。` `Tip: 常说 take a photo，不说 make a photo。`

4. Countable or uncountable noun warning
   - Use when the Chinese translation may make learners treat an English uncountable noun as countable, or add `a/an` or plural `-s` incorrectly.
   - State the countability and give one correct expression.
   - Example Tips: `Tip: advice 是不可数名词，不说 an advice，可说 a piece of advice。` `Tip: information 是不可数名词，不说 informations。`

5. Non-literal Chinese-English mismatch
   - Use when the Chinese translation may mislead learners into direct translation and produce unnatural or wrong English.
   - State what cannot be translated directly and give a natural English expression.
   - Example Tips: `Tip: convenient 通常形容时间、地点或事物方便；不要直译成 I am convenient，可说 It is convenient for me。` `Tip: funny 常指“好笑的/奇怪的”，不等于所有场景里的“有趣”；“有趣”常用 interesting 或 fun。`

6. Easily confused word
   - Use when the target word and one common word have similar Chinese translations but different English usage.
   - Compare only the most easily confused word and state the core difference.
   - Example Tips: `Tip: borrow 是“借入”，lend 是“借出”：borrow money from someone；lend money to someone。` `Tip: price 指“价格/标价”，cost 更强调实际花费或代价。`

7. Near-synonym usage boundary
   - Use when several common English words can share the same Chinese translation but have different usage situations.
   - Explain only the key boundary; do not write a full synonym comparison.
   - Example Tips: `Tip: watch 强调看一个过程，如 watch TV；see 强调看到，look 强调主动看。` `Tip: tell 常接“人”：tell someone something；say 更强调说出的内容。`

8. Context, register, or formality
   - Use when the target word and another word have similar meaning but differ in formality, spoken/written style, or usage context.
   - State the register and give the more common alternative when useful.
   - Example Tips: `Tip: purchase 比 buy 更正式，日常口语通常用 buy。` `Tip: kid 是口语说法，正式写作中更常用 child。`

### Tip exclusion rules

Do not add Tip for simple words.

Do not use Tip to restate, summarize, or explain the retained meanings themselves. If the Tip only says that a word has meaning A and meaning B, or repeats information already shown by semicolons in the meaning line, omit the Tip.

Do not add Tip for roots, memory tricks, abstract core images, etymology, rare edge knowledge, or dictionary completeness.

Tip must be short, direct, and solve exactly one problem.

Before adding Tip, apply this test:

- If deleting the Tip would not remove a specific warning about misuse, wrong structure, preposition, collocation, countability, Chinese-English mismatch, word confusion, synonym boundary, or register, delete it.

Bad Tip examples:

- `Tip: 重点记住这个词最常见的用法。`
- `Tip: 注意根据句子判断词性。`
- `Tip: 这个词建议整体记忆。`
- `Tip: builder 既可指建筑行业的人，也可抽象指建立、塑造某事物的人。`
- `Tip: charge 表示“收费”和“充电”是两个不同常见义项。`

## Phrases, sentence patterns, and grammar structures

- Use `phr.` for phrases.
- Use `structure.` for sentence patterns.
- Use `rule.` for grammar rules.
- Do not force sentence patterns or grammar structures into ordinary word-card form.
- For contrastive structures, the number of examples may follow the number of contrasted patterns rather than ordinary vocabulary core meaning units.
- For contrastive structures, explain the contrast briefly and provide matching examples.

Example:

```html
<div class="phonetic">需核对英式音标</div>

<div class="meanings">
  <div class="meaning">structure. stop to do sth 停下来去做另一件事；stop doing sth 停止正在做的事</div>
</div>

<div class="examples">
  <div class="example">I stopped to drink water.</div>
  <div class="translation">我停下来去喝水。</div>

  <div class="example">I stopped drinking coffee.</div>
  <div class="translation">我停止喝咖啡。</div>
</div>
```

## British English rules

- Prefer British spelling: `colour`, `favour`, `metre`, `theatre`.
- Use British phonetics.
- Use British phrasing where natural.
- Exception: computer software is normally `program`; TV/radio show or plan is usually `programme`.

## Do not do

- Do not turn cards into dictionary entries.
- Do not add every possible meaning.
- Do not add Tip unless it clearly matches one of the 8 Tip categories.
- Do not add vague Tip text, memory tricks, abstract core images, etymology, or rare edge knowledge.
- Do not add POS labels after examples.
- Do not use semicolons for similar Chinese glosses of the same English sense.
- Do not use advanced examples far above B1 unless the target word requires it.

## Final full-batch quality check

Run this once after all cards for the current request are generated or prepared, and before any write that will sync. Check every card in the batch against the final requested output, not only the card most recently generated.

- Front uses correct lowercase or proper-noun capitalization.
- British spelling and phonetic style are used.
- Back uses the required HTML structure.
- Phonetic, meanings, examples, and translations are present.
- Retained core meaning units are no more than 3 and reflect the senses the learner is most likely to review or use.
- Distinct English senses are not collapsed into comma-separated Chinese glosses.
- Same-POS similar Chinese glosses use commas only when one natural English example can clearly cover every gloss.
- Same-POS different English senses use Chinese semicolons on one line.
- Different POS meanings are split into separate lines.
- Examples are no more than 3, except for special contrastive structures where extra examples are necessary.
- One ordinary core meaning has exactly 1 example by default.
- Each retained ordinary core meaning unit has its own matching example.
- Example order matches meaning order.
- Chinese example translations match the target sense in natural Chinese, not word-for-word English structure.
- Same POS never appears on multiple meaning lines.
- Examples have no ending POS labels.
- Tip is absent unless the word or retained sense clearly matches one of the 8 Tip categories.
- If Tip is present, it solves exactly one likely misuse or confusion problem and does not restate the meanings already shown.
- If any card fails this check, fix the whole batch before writing or syncing.

## Examples

### Simple word

Front:

```text
humid
```

Back:

```html
<div class="phonetic">/ˈhjuː.mɪd/</div>

<div class="meanings">
  <div class="meaning">adj. 潮湿的，湿热的</div>
</div>

<div class="examples">
  <div class="example">The air is humid today.</div>
  <div class="translation">今天空气很潮湿。</div>
</div>
```

### Same-POS multi-sense word

Front:

```text
period
```

Back:

```html
<div class="phonetic">/ˈpɪə.ri.əd/</div>

<div class="meanings">
  <div class="meaning">n. 时期，阶段；句号</div>
</div>

<div class="examples">
  <div class="example">It was a difficult period.</div>
  <div class="translation">那是一段困难时期。</div>

  <div class="example">Put a full stop at the end.</div>
  <div class="translation">在末尾加一个句号。</div>
</div>
```

### Same-POS three-sense word

Front:

```text
scale
```

Back:

```html
<div class="phonetic">/skeɪl/</div>

<div class="meanings">
  <div class="meaning">n. 规模，程度；刻度，等级；鳞片</div>
</div>

<div class="examples">
  <div class="example">The scale of the problem is huge.</div>
  <div class="translation">这个问题的规模很大。</div>

  <div class="example">Rate your pain on a scale of one to ten.</div>
  <div class="translation">请按一到十的等级评估你的疼痛。</div>

  <div class="example">Fish are covered with scales.</div>
  <div class="translation">鱼身上覆盖着鳞片。</div>
</div>
```

### Multi-POS word

Front:

```text
work
```

Back:

```html
<div class="phonetic">/wɜːk/</div>

<div class="meanings">
  <div class="meaning">v. 工作；运转，起作用</div>
  <div class="meaning">n. 工作，任务</div>
</div>

<div class="examples">
  <div class="example">She works in a hotel.</div>
  <div class="translation">她在一家酒店工作。</div>

  <div class="example">This printer does not work.</div>
  <div class="translation">这台打印机不能运转。</div>

  <div class="example">My work starts at nine.</div>
  <div class="translation">我的工作九点开始。</div>
</div>
```

### Phrase

Front:

```text
put away
```

Back:

```html
<div class="phonetic">/pʊt əˈweɪ/</div>

<div class="meanings">
  <div class="meaning">phr. 收好，放回原处</div>
</div>

<div class="examples">
  <div class="example">Put away your clothes.</div>
  <div class="translation">把你的衣服收好。</div>
</div>
```

### Word that needs Tip

Front:

```text
convenient
```

Back:

```html
<div class="phonetic">/kənˈviː.ni.ənt/</div>

<div class="meanings">
  <div class="meaning">adj. 方便的，便利的</div>
</div>

<div class="examples">
  <div class="example">This time is convenient for me.</div>
  <div class="translation">这个时间对我来说方便。</div>
</div>

<div class="tip">Tip: convenient 通常形容时间、地点或事物方便；不要直译成 I am convenient。</div>
```

### Compact high-frequency multi-meaning word

Front:

```text
charge
```

Back:

```html
<div class="phonetic">/tʃɑːdʒ/</div>

<div class="meanings">
  <div class="meaning">v. 收费，要价；给……充电</div>
  <div class="meaning">n. 费用</div>
</div>

<div class="examples">
  <div class="example">They charge £10 for delivery.</div>
  <div class="translation">他们收取 10 英镑的配送费。</div>

  <div class="example">I need to charge my phone.</div>
  <div class="translation">我需要给手机充电。</div>

  <div class="example">There is no extra charge.</div>
  <div class="translation">没有额外费用。</div>
</div>

```
