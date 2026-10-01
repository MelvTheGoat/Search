# Mock test with worked answers: Meriti Inc data science test (Coderbyte)

Every question here is laid out the same way:

1. **Question**
2. **How to solve it:** the method, step by step, and how to spot this kind of
   question
3. **Answer**
4. **Similar questions:** other questions that use the same method, so you can
   solve one even if it is not the exact question you see

Try each question yourself for a few minutes first. Then read how it is solved.

## What we know about the real test

These come from the real test page and from research on how Coderbyte tests work.

- **Time:** 3 hours, one sitting. The timer cannot be paused, and you cannot
  leave and come back.
- **Type:** made from Coderbyte's Data Science template. Video answers are
  switched on, so some questions will ask you to talk on camera.
- **Likely parts:** Python coding challenges, maybe SQL and a data question,
  multiple choice on statistics and ML, and video answers. Tests of this length
  usually have up to 5 coding challenges plus questions.
- **Coding screen:** the question and some sample tests are on the left and the
  editor is on the right. Hidden test cases mark your code on a 1 to 10 scale.
- **Names:** coding challenges are called "String Challenge", "Array Challenge",
  "Searching Challenge" or "Math Challenge", each marked Easy, Medium or Hard.
- **Starter code:** the editor gives you something like this. Never change the
  last line.

  ```
  def StringChallenge(strParam):
      # your code goes here
      return strParam

  # do not change this line
  print(StringChallenge(input()))
  ```

- **Rules:** do not paste code from outside the editor, and do not leave the
  tab. Coderbyte flags both. Short comments that explain your thinking are
  welcome.

## How to solve any coding question

Use these steps for every coding question, including ones you have never seen.

1. **Read to the end.** The last lines often add a rule, such as the
   ChallengeToken step.
2. **Find the input type.** Is it one string, a list of strings or a number?
   Lists of numbers often come as text, like `"1, 3, 4"`. Split the text and
   change each part into a number.
3. **Work one example by hand.** Write it as a comment if that helps.
4. **Write the simplest version that works.** When inputs are small (for
   example up to 50 characters), trying every option is fast enough.
5. **Test the sample cases, then the edge cases:** an empty result, a tie, one
   item, repeated items.
6. **Add the ChallengeToken step last,** as its own small function.
7. **Use leftover time** to make it faster or cleaner, and add short comments.

### Which method fits which question

When the question says one of these things, reach for the method next to it.

| The question says | Method |
|---|---|
| "check if valid", "follows these rules" | Check each rule one by one and stop at the first one that fails |
| "appears in both", "common", "unique", "seen before" | A set |
| "how many times", "most frequent" | A counter (`collections.Counter`) |
| "shortest or longest substring or subarray that..." | Sliding window (two pointers) |
| "how many ways", "number of arrangements" | Recursion that tries each choice, then remembers answers (memo) or uses a formula |
| "two numbers that add up to X" | A set of numbers seen so far |
| "brackets balanced" | A stack (a list you add to and take from the end) |
| "for each group, total or average" | Group by (a dict in plain Python, `groupby` in pandas) |
| SQL "for each X, count or average Y" | `GROUP BY` |
| SQL "top N in each group" | A window function such as `RANK() OVER (PARTITION BY ...)` |

## The ChallengeToken step

Many Coderbyte challenges end with: "Once your function is working, take the
final output string and ..." plus a short code called the ChallengeToken.
Your answer only counts if this step is right too. Three styles have been seen
in real tests.

**1. Intersperse:** mix the output and the token, one character at a time.
When one runs out, add the rest of the other.

- **Output:** `aBCDEFG`
- **Token:** `r1omjb4zc8f`
- **How it mixes:** `a`+`r`, `B`+`1`, `C`+`o`, `D`+`m`, `E`+`j`, `F`+`b`,
  `G`+`4`, then the rest of the token, `zc8f`
- **Result:** `arB1CoDmEjFbG4zc8f`

**2. Wrap:** put `--` on both sides of every output character that appears in
the token.

- **Output:** `1,4,13`
- **Token:** `13ab`
- **Result:** `--1--,4,--1----3--`

**3. Remove:** delete every output character that appears in the token,
ignoring upper and lower case. If nothing is left, return `EMPTY`.

- **Output:** `42`
- **Token:** `2x7`
- **Result:** `4`

Code for all three. Keep these ready and copy the one you need into your
answer.

```python
def intersperse(out, token):
    res = []
    for i in range(max(len(out), len(token))):
        if i < len(out):
            res.append(out[i])
        if i < len(token):
            res.append(token[i])
    return "".join(res)

def wrap_token_chars(out, token):
    return "".join(f"--{c}--" if c in token else c for c in out)

def remove_token_chars(out, token):
    t = token.lower()
    res = "".join(c for c in out if c.lower() not in t)
    return res if res else "EMPTY"
```

## Time plan for practice

| Part | What | Questions | Time |
|---|---|---|---|
| A | Coding challenges (Python) | 4 | 65 min |
| B | Data and SQL | 3 | 45 min |
| C | Multiple choice | 20 | 30 min |
| D | Video answers | 3 | 15 min |
|  | Spare time to check your work |  | 25 min |

---

## Part A: Coding challenges (Python)

### A1. String Challenge (Easy, 10 min)

**Question**

Have the function `StringChallenge(str)` take the `str` parameter and check
whether it is a valid username. The rules:

1. It is between 4 and 25 characters long.
2. It starts with a letter.
3. It contains only letters, numbers and the underscore character.
4. It does not end with an underscore.

Return the string `true` if the username is valid, otherwise `false`.

Once your function is working, take the final output string and intersperse it
character by character with your ChallengeToken.
Your ChallengeToken: `k7m2xq`

| Input | Output | Final output |
|---|---|---|
| `"aa_"` | `false` | `fka7lms2exq` |
| `"u__hello_world123"` | `true` | `tkr7ume2xq` |

**How to solve it**

This is a **rule check**. Turn each rule into one test in Python:

| Rule | Python test |
|---|---|
| 4 to 25 characters | `4 <= len(s) <= 25` |
| Starts with a letter | `s[0].isalpha()` |
| Only letters, numbers and `_` | `all(c.isalnum() or c == "_" for c in s)` |
| Does not end with `_` | `not s.endswith("_")` |

The username is valid only if all four tests pass, so join them with `and`.
Python stops at the first test that fails. Put the length test first, so
`s[0]` never runs on an empty string.

Work the examples by hand:

- `"aa_"` is only 3 characters, so it fails the first rule and gives `false`.
- `"u__hello_world123"` is 17 characters, starts with `u`, only uses letters,
  numbers and `_`, and ends with `3`. It gives `true`.

Last, mix `true` or `false` with the token. `false` and `k7m2xq` give `f`+`k`,
`a`+`7`, `l`+`m`, `s`+`2`, `e`+`x`, then `q`, which is `fka7lms2exq`.

**Answer**

```python
def StringChallenge(s):
    ok = (4 <= len(s) <= 25
          and s[0].isalpha()
          and all(c.isalnum() or c == "_" for c in s)
          and not s.endswith("_"))
    return intersperse("true" if ok else "false", "k7m2xq")
```

More tests: `"1abc_def"` gives `fka7lms2exq` (it starts with a number).
`"Code_Land99"` gives `tkr7ume2xq`.

**Similar questions**

The same method (turn each rule into a test) works for password rules,
"is this a palindrome" (`s == s[::-1]`) and any other "check if valid" question.

A real Coderbyte String Challenge asks you to change text into camel case:
`"cats AND*Dogs-are Awesome"` becomes `catsAndDogsAreAwesome`. The method is
to split the text into words, then rebuild it.

1. Split on anything that is not a letter or a number.
2. Make the first word lower case.
3. Make every other word start with a capital letter.

```python
import re

def camel(s):
    words = [w for w in re.split(r"[^A-Za-z0-9]+", s) if w]
    return words[0].lower() + "".join(w[:1].upper() + w[1:].lower() for w in words[1:])
```

**Common mistakes:** forgetting one rule (the "does not end with `_`" rule is
the one people miss), and returning `True` (a Python value) instead of the
string `"true"`.

### A2. Array Challenge (Easy, 10 min)

**Question**

Have the function `ArrayChallenge(strArr)` read the array of strings stored in
`strArr`. It has 2 elements, and each one is a list of comma separated numbers
sorted from smallest to largest. Return the numbers that appear in both lists,
as a comma separated string from smallest to largest, with no spaces. If no
number appears in both, return the string `false`.

Once your function is working, take the final output string and replace every
character that appears in your ChallengeToken with `--[CHAR]--`.
Your ChallengeToken: `13ab`

| Input | Output | Final output |
|---|---|---|
| `["1, 3, 4, 7, 13", "1, 2, 4, 13, 15"]` | `1,4,13` | `--1--,4,--1----3--` |
| `["2, 5", "3, 4"]` | `false` | `f--a--lse` |

**How to solve it**

"Appears in both" means a **set**.

1. **Turn each text into numbers:** `"1, 3, 4"` split on `,` gives
   `["1", " 3", " 4"]`. `int(" 3")` gives `3`, because `int` ignores spaces.
2. **Put the second list in a set.** Checking `x in a_set` is instant, while
   checking a list means scanning every item.
3. **Go through the first list in order and keep each number that is in the
   set.** The first list is already sorted, so the result is sorted too.
4. **Build the output:** join with commas, or return `"false"` if nothing
   matched.
5. **Do the token step.**

Work the first example by hand. The set is `{1, 2, 4, 13, 15}`. Going through
`1, 3, 4, 7, 13`, keep 1, skip 3, keep 4, skip 7, keep 13. The result is
`1,4,13`.

Then wrap: `1` is in `13ab`, so it becomes `--1--`. The comma stays. `4` stays.
In `13`, both `1` and `3` are in the token. The result is
`--1--,4,--1----3--`.

**Answer**

```python
def ArrayChallenge(strArr):
    a = [int(x) for x in strArr[0].split(",")]
    b = set(int(x) for x in strArr[1].split(","))
    common = [x for x in a if x in b]
    out = ",".join(str(x) for x in common) if common else "false"
    return wrap_token_chars(out, "13ab")
```

More tests: `["1, 3, 9, 10, 17, 18", "1, 4, 9, 10"]` gives `--1--,9,--1--0`.
`["4", "4"]` gives `4`.

**Similar questions**

- "Numbers in the first list but not the second": keep `x` when
  `x not in b`.
- "Remove duplicates but keep the order": keep a `seen` set and skip anything
  already in it.
- "Do two numbers in the list add up to the target?" For each number, check
  whether `target - x` is in the set of numbers seen so far. This is one pass
  through the list.

```python
def has_pair(nums, target):
    seen = set()
    for x in nums:
        if target - x in seen:
            return True
        seen.add(x)
    return False
```

**Common mistakes:** comparing the numbers as text (`" 4"` is not `"4"`),
leaving spaces in the output, and returning an empty string instead of
`false`.

### A3. Searching Challenge (Medium, 25 min)

**Question**

Have the function `SearchingChallenge(strArr)` take `strArr`, which holds two
strings, N and K. Return the shortest part of N (letters next to each other)
that contains every character of K. Repeats count: if K is `aad`, the part
needs at least two `a` and one `d`. If more than one part has the shortest
length, return the one that starts first.

N and K are 1 to 50 lowercase letters long, and N always has every character
of K, repeats included.

Once your function is working, take the final output string and intersperse it
character by character with your ChallengeToken.
Your ChallengeToken: `x9z`

| Input | Output | Final output |
|---|---|---|
| `["aaabaaddae", "aed"]` | `dae` | `dxa9ez` |
| `["aabdccdbcacd", "aad"]` | `aabd` | `axa9bzd` |

**How to solve it**

"Shortest part of a string that contains..." is a **sliding window** question.
There are two ways to do it. Write the simple way first.

**The simple way: try every window.** Try window sizes from `len(K)` upward.
For each size, slide across N from the left. The first window that contains
everything is the answer: it is the shortest because the sizes go up, and it
starts first because each size is checked from the left.

To check a window, count its letters with `Counter` and make sure each letter
of K appears at least as many times as K needs it. With N at most 50
characters, this is fast enough.

**The faster way: one moving window.** Use two pointers, `left` and `right`.

1. Move `right` forward one letter at a time, adding each letter to the window.
2. As soon as the window has everything, move `left` forward to shrink it,
   for as long as it still has everything.
3. Each time it has everything, save it if it is the shortest so far.

The variable `missing` counts how many needed letters the window still lacks.
When `missing` is 0, the window is complete.

Work the first example with the faster way. N is `aaabaaddae` and K needs one
`a`, one `e` and one `d`.

- `right` moves to the end before the window first holds an `e`, so the first
  complete window is the whole string.
- Now `left` moves in. Taking away the first `a`, `a`, `a`, `b`, `a`, `a` and
  `d` still leaves an `a`, a `d` and an `e`. The window shrinks to `dae`.
- Taking away that `d` would lose the last `d`, so it stops. The answer is
  `dae`.

Then intersperse `dae` with `x9z` to get `dxa9ez`.

**Answer (simple version, enough for this test)**

```python
from collections import Counter

def SearchingChallenge(strArr):
    n, k = strArr
    need = Counter(k)
    for size in range(len(k), len(n) + 1):
        for start in range(len(n) - size + 1):
            window = Counter(n[start:start + size])
            if all(window[c] >= need[c] for c in need):
                return intersperse(n[start:start + size], "x9z")
```

**Answer (faster version)**

```python
from collections import Counter

def SearchingChallenge(strArr):
    n, k = strArr
    need = Counter(k)
    missing = len(k)
    have = Counter()
    best = None
    left = 0
    for right, ch in enumerate(n):
        if have[ch] < need[ch]:
            missing -= 1
        have[ch] += 1
        while missing == 0:
            if best is None or right - left + 1 < len(best):
                best = n[left:right + 1]
            lc = n[left]
            have[lc] -= 1
            if have[lc] < need[lc]:
                missing += 1
            left += 1
    return intersperse(best, "x9z")
```

More tests: `["ahffaksfajeeubsne", "jefaa"]` gives `aksfaje`, final
`axk9szfaje`. `["aaffhkksemckelloe", "fhea"]` gives `affhkkse`, final
`axf9fzhkkse`.

**Similar questions**

The sliding window works for any "shortest or longest stretch that..." question.

- **Longest part with no repeated letter:** move `right` forward. When a letter
  repeats, jump `left` to just after the last time that letter appeared.
  `"abcabcbb"` gives 3.

```python
def longest_unique(s):
    last = {}
    left = best = 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best
```

- **Shortest run of positive numbers that adds up to at least the target:** add
  numbers on the right, and remove numbers on the left while the total is still
  big enough. `[2, 3, 1, 2, 4, 3]` with target 7 gives 2 (the run `4, 3`).

```python
def min_len_sum(nums, target):
    left = total = 0
    best = None
    for right, x in enumerate(nums):
        total += x
        while total >= target:
            size = right - left + 1
            best = size if best is None else min(best, size)
            total -= nums[left]
            left += 1
    return best or 0
```

**Common mistakes:** ignoring repeats in K (`aad` needs two `a`), and returning
a later window of the same length instead of the first one.

### A4. Math Challenge (Hard, 20 min)

**Question**

Have the function `MathChallenge(num)` take `num`, a whole number from 1 to 15,
and return how many different ways `num` pairs of brackets can be arranged so
that they are balanced. For example, 3 pairs can be arranged as `((()))`,
`(()())`, `(())()`, `()(())` and `()()()`, so the answer is 5.

Once your function is working, take the final output string and remove every
character that appears in your ChallengeToken (ignore case). If nothing is
left, return `EMPTY`.
Your ChallengeToken: `2x7`

| Input | Output | Final output |
|---|---|---|
| `3` | `5` | `5` |
| `2` | `2` | `EMPTY` |

**How to solve it**

"How many ways" is a **counting** question. Build the answer one choice at a
time with recursion.

1. Build the bracket string one character at a time.
2. You may add `(` if you have used fewer than `num` of them.
3. You may add `)` only if more brackets are open than closed. This rule keeps
   the string balanced.
4. When you have used `num` of each, you have one valid arrangement, so count
   it.

Check by hand with `num = 2`. The only strings you can build are `(())` and
`()()`, so the answer is 2. This matches the table.

**The problem with plain recursion:** it visits every arrangement one by one.
At 15 pairs there are almost 10 million, which takes a few seconds in Python
and could time out.

**The fix is to remember answers (memoization).** The number of ways to finish
depends only on how many `(` and `)` you have used so far, so the same
question gets asked again and again. `lru_cache` saves each answer the first
time and reuses it after that. With it, 15 pairs takes well under a second.

**The shortcut:** the answers 1, 2, 5, 14, 42 are the Catalan numbers, which
have a formula: `comb(2n, n) // (n + 1)`. You do not need to remember it, but
if you see these numbers in a question, now you know.

Then do the token step. 5 has no `2` or `7`, so it stays `5`. 2 loses its only
character, so the result is `EMPTY`.

**Answer (recursion with memo)**

```python
from functools import lru_cache

def MathChallenge(num):
    @lru_cache(maxsize=None)
    def ways(opened, closed):
        if opened == num and closed == num:
            return 1
        total = 0
        if opened < num:
            total += ways(opened + 1, closed)
        if closed < opened:
            total += ways(opened, closed + 1)
        return total
    return remove_token_chars(str(ways(0, 0)), "2x7")
```

**Answer (formula)**

```python
import math

def MathChallenge(num):
    out = str(math.comb(2 * num, num) // (num + 1))
    return remove_token_chars(out, "2x7")
```

More tests: 4 gives `14`. 5 gives 42, final `4`. 6 gives 132, final `13`.
10 gives 16796, final `1696`.

**Similar questions**

- **Ways to climb `n` stairs, taking 1 or 2 steps at a time:** the ways to
  reach step `k` are the ways to reach step `k - 1` plus the ways to reach step
  `k - 2`. This is the same "try each choice, remember answers" method.

```python
from functools import lru_cache

def stairs(n):
    @lru_cache(maxsize=None)
    def ways(k):
        if k <= 1:
            return 1
        return ways(k - 1) + ways(k - 2)
    return ways(n)
```

- **Is a string of brackets balanced?** (Coderbyte calls this "Bracket
  Matcher".) This uses a different method, a stack. Push each opening bracket.
  At each closing bracket, the last opening bracket must be its partner. At
  the end, the stack must be empty.

```python
def balanced(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
```

**Common mistakes:** allowing `)` when nothing is open, and returning a number
when the token step needs a string (use `str(...)` first).

---

## Part B: Data and SQL

### B1. Data Challenge (Medium, 15 min)

**Question**

Have the function `DataChallenge(csvText)` take a string of CSV data with the
header `user_id,date,amount`. Each row is one transaction. Some rows have an
empty amount or one that is not a number. Ignore those rows completely,
including their dates.

Find the user with the highest total amount. If two users have the same total,
pick the smaller `user_id`. Return a string in this form:

```
user_id:total:days
```

`total` has exactly 2 decimal places. `days` is the number of days between the
user's first and last valid transaction, or 0 if they have only one. You may
use pandas or plain Python.

Example input:

```
user_id,date,amount
1,2026-01-01,50
2,2026-01-03,200
1,2026-01-10,30
3,2026-01-05,80
2,2026-01-04,
1,2026-01-02,10.5
2,2026-01-09,abc
```

Output: `2:200.00:0`

**How to solve it**

This is **clean, group, then summarise**, the most common kind of data
question.

1. **Read** the CSV text. In plain Python, `csv.DictReader` gives each row as
   a dict.
2. **Clean:** try `float(row["amount"])`. If it fails (empty or `abc`), skip
   the whole row with `continue`. An amount of 0 is valid, so do not drop it.
3. **Group:** keep one dict for each user's total and one for each user's list
   of dates.
4. **Pick the winner with the tie rule:** `min(totals, key=lambda u:
   (-totals[u], u))` sorts by the highest total first (that is why the minus
   sign is there), then by the smallest ID. This trick works for any
   "highest, then break ties by..." rule.
5. **Days:** the latest date minus the earliest date, then `.days`.
6. **Format:** `f"{total:.2f}"` always gives 2 decimal places.

Work the example by hand. User 1 has 50 + 30 + 10.5 = 90.50. User 2 has 200,
because their empty row and their `abc` row are skipped. User 3 has 80. User 2
wins with one valid transaction, so days is 0. The answer is `2:200.00:0`.

**The pandas way** is the same steps with pandas tools:

| Step | pandas |
|---|---|
| Read | `pd.read_csv(io.StringIO(csvText))` |
| Clean | `pd.to_numeric(df["amount"], errors="coerce")` turns bad values into NaN, then `dropna` removes those rows |
| Dates | `pd.to_datetime(df["date"])` |
| Group | `groupby("user_id").agg(total=("amount", "sum"), first=("date", "min"), last=("date", "max"))` |
| Tie rule | `sort_values(["total", "user_id"], ascending=[False, True])`, then take the first row |

**Answer (plain Python, tested)**

```python
import csv, io
from datetime import date

def DataChallenge(csvText):
    totals, dates = {}, {}
    for row in csv.DictReader(io.StringIO(csvText)):
        try:
            amount = float(row["amount"])
        except (TypeError, ValueError):
            continue
        uid = int(row["user_id"])
        totals[uid] = totals.get(uid, 0.0) + amount
        dates.setdefault(uid, []).append(date.fromisoformat(row["date"]))
    best = min(totals, key=lambda u: (-totals[u], u))
    days = (max(dates[best]) - min(dates[best])).days
    return f"{best}:{totals[best]:.2f}:{days}"
```

**Answer (pandas, not run here because pandas is not installed in this workspace)**

```python
import io
import pandas as pd

def DataChallenge(csvText):
    df = pd.read_csv(io.StringIO(csvText))
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])
    df["date"] = pd.to_datetime(df["date"])
    g = (df.groupby("user_id")
           .agg(total=("amount", "sum"), first=("date", "min"), last=("date", "max"))
           .reset_index()
           .sort_values(["total", "user_id"], ascending=[False, True]))
    top = g.iloc[0]
    days = (top["last"] - top["first"]).days
    return f"{int(top['user_id'])}:{top['total']:.2f}:{days}"
```

More tests:

```
user_id,date,amount
4,2026-03-01,120.25
5,2026-03-02,60
4,2026-03-15,0
5,2026-02-20,60.25
6,2026-03-03,n/a
4,2026-02-27,
```

Output: `4:120.25:14`. Users 4 and 5 tie at 120.25, so the smaller ID wins. The
2026-02-27 row has no amount, so its date is ignored. The amount of 0 is still
valid.

```
user_id,date,amount
8,2026-05-01,100
7,2026-05-04,60
7,2026-05-09,40
```

Output: `7:100.00:5`. Users 7 and 8 tie at 100, so user 7 wins.

**Similar questions (pandas tools to know)**

| Question | pandas |
|---|---|
| Average for each group | `df.groupby("g")["x"].mean()` |
| Count for each category | `df["g"].value_counts()` |
| Top 2 rows in each group | `df.sort_values("x", ascending=False).groupby("g").head(2)` |
| Fill missing numbers with the median | `df["x"] = df["x"].fillna(df["x"].median())` |
| Put ages into groups | `pd.cut(df["age"], bins=[0, 30, 50, 120], labels=["young", "middle", "senior"])` |
| Join two tables | `df.merge(other, on="user_id", how="left")` |
| Each row's share of its group total | `df["x"] / df.groupby("g")["x"].transform("sum")` |
| 7 day moving average | `df["x"].rolling(7).mean()` |

**Common mistakes:** keeping the date of a row whose amount was bad, treating
0 as missing, forgetting the tie rule, and printing `200.0` instead of
`200.00`.

### B2. SQL: team sizes (Medium, 15 min)

**Question**

Table `employees`:

| id | first_name | last_name | reports_to | position | age |
|---|---|---|---|---|---|
| 1 | Sam | Cole | Lena Park | Engineer | 25 |
| 2 | Omar | Diaz | Lena Park | Analyst | 22 |
| 3 | Lena | Park | NULL | CTO | 45 |
| 4 | Ivy | Chen | Sam Cole | Intern | 21 |
| 5 | Tom | Reed | Lena Park | Engineer | 30 |
| 6 | Nia | Grant | Mia Kent | Analyst | 28 |
| 7 | Mia | Kent | NULL | CEO | 50 |
| 8 | Leo | Ross | Mia Kent | Designer | 27 |

Write a query that returns one row for every person who has at least one
person reporting to them, with these columns:

- `ReportsTo`: their name, as written in `reports_to`
- `Members`: how many people report to them
- `AvgAge`: the average age of those people, rounded to the nearest whole number

Leave out rows where `reports_to` is NULL. Order the result by `ReportsTo`
from A to Z.

**How to solve it**

"For each manager, count and average" means **GROUP BY the manager**.

The order SQL runs a query in helps you build it:

1. `FROM employees`: start with the table.
2. `WHERE reports_to IS NOT NULL`: remove rows **before** grouping. Use
   `IS NOT NULL`, never `!= NULL`, which never matches anything.
3. `GROUP BY reports_to`: one group for each manager.
4. `SELECT`: what to show for each group: the name, `COUNT(*)` for the number
   of people, and `ROUND(AVG(age), 0)` for the average age.
5. `ORDER BY reports_to`: A to Z.

Work it by hand. Lena Park has Sam (25), Omar (22) and Tom (30). That is 3
people, and the average is 77 / 3 = 25.67, which rounds to 26.

**Answer**

```sql
SELECT reports_to AS ReportsTo,
       COUNT(*) AS Members,
       ROUND(AVG(age), 0) AS AvgAge
FROM employees
WHERE reports_to IS NOT NULL
GROUP BY reports_to
ORDER BY reports_to;
```

| ReportsTo | Members | AvgAge |
|---|---|---|
| Lena Park | 3 | 26 |
| Mia Kent | 2 | 28 |
| Sam Cole | 1 | 21 |

Tested in SQLite, which prints 26.0 instead of 26. MySQL prints 26. Coderbyte
shows which SQL version it uses at the top of the question, so check it first.

**Similar questions**

- **Only managers with 2 or more people:** `WHERE` filters rows before
  grouping, and `HAVING` filters groups after grouping. Use `HAVING` for
  conditions on `COUNT`, `SUM` or `AVG`.

```sql
SELECT reports_to, COUNT(*) AS Members
FROM employees
WHERE reports_to IS NOT NULL
GROUP BY reports_to
HAVING COUNT(*) >= 2
ORDER BY reports_to;
```

This gives Lena Park (3) and Mia Kent (2).

- **Show each person with their manager's age:** join the table to itself (a
  self join). `e` is the employee and `m` is the manager. In MySQL, join names
  with `CONCAT(m.first_name, ' ', m.last_name)` instead of `||`.

```sql
SELECT e.first_name || ' ' || e.last_name AS employee,
       m.age AS manager_age
FROM employees e
JOIN employees m ON e.reports_to = m.first_name || ' ' || m.last_name
ORDER BY employee;
```

**Common mistakes:** `= NULL` instead of `IS NULL`, putting `COUNT(*) >= 2` in
`WHERE` instead of `HAVING`, and forgetting `ORDER BY` (Coderbyte compares
your rows in order).

### B3. SQL: top customers per month (Medium, 15 min)

**Question**

Table `orders`:

| order_id | customer_id | order_date | amount |
|---|---|---|---|
| 1 | 10 | 2026-01-03 | 100 |
| 2 | 11 | 2026-01-05 | 300 |
| 3 | 10 | 2026-01-20 | 250 |
| 4 | 12 | 2026-01-22 | 300 |
| 5 | 13 | 2026-01-25 | 50 |
| 6 | 11 | 2026-02-02 | 80 |
| 7 | 13 | 2026-02-14 | 500 |
| 8 | 10 | 2026-02-15 | 80 |
| 9 | 12 | 2026-02-28 | 20 |

Return the top 2 customers by total spend in each month. If customers tie,
give them the same rank, so a month can have more than 2 rows. Columns:
`month` (as `YYYY-MM`), `customer_id`, `total`, `rnk`. Order by `month`, then
`rnk`, then `customer_id`.

**How to solve it**

"Top N in each group" means a **window function**. Build it in three steps,
each in its own block (`WITH ... AS`):

1. **Totals:** one row for each month and customer, with `GROUP BY month,
   customer_id` and `SUM(amount)`.
2. **Rank inside each month:** `RANK() OVER (PARTITION BY month ORDER BY total
   DESC)`. `PARTITION BY month` means the ranking starts again at 1 for each
   month.
3. **Keep the top 2:** `WHERE rnk <= 2`. This must go in an outer query. You
   cannot use a window function's result in the `WHERE` of the same query,
   because `WHERE` runs before the window function.

Pick the right ranking function:

| Function | Totals 350, 300, 300, 50 | Use it when |
|---|---|---|
| `RANK()` | 1, 2, 2, 4 | Ties share a rank and the next rank is skipped. This question. |
| `DENSE_RANK()` | 1, 2, 2, 3 | Ties share a rank with no gaps, as in "second highest value". |
| `ROW_NUMBER()` | 1, 2, 3, 4 | You need exactly N rows and ties do not matter. |

Work January by hand. Customer 10 has 100 + 250 = 350, customer 11 has 300,
customer 12 has 300 and customer 13 has 50. The ranks are 1, 2, 2 and 4, so
three rows are kept.

**Answer**

```sql
WITH monthly AS (
  SELECT strftime('%Y-%m', order_date) AS month,
         customer_id,
         SUM(amount) AS total
  FROM orders
  GROUP BY month, customer_id
),
ranked AS (
  SELECT month, customer_id, total,
         RANK() OVER (PARTITION BY month ORDER BY total DESC) AS rnk
  FROM monthly
)
SELECT month, customer_id, total, rnk
FROM ranked
WHERE rnk <= 2
ORDER BY month, rnk, customer_id;
```

The month function depends on the database. SQLite uses `strftime('%Y-%m',
order_date)`, MySQL uses `DATE_FORMAT(order_date, '%Y-%m')` and PostgreSQL uses
`TO_CHAR(order_date, 'YYYY-MM')`.

| month | customer_id | total | rnk |
|---|---|---|---|
| 2026-01 | 10 | 350 | 1 |
| 2026-01 | 11 | 300 | 2 |
| 2026-01 | 12 | 300 | 2 |
| 2026-02 | 13 | 500 | 1 |
| 2026-02 | 10 | 80 | 2 |
| 2026-02 | 11 | 80 | 2 |

If the database is an old one with no window functions, a customer's rank is
1 plus the number of customers in the same month with a higher total. Count
them with a subquery.

**Similar questions (other window functions)**

- **Running total for each customer:** `SUM` with `OVER` adds up row by row.
  Customer 10 gets 100, 350, 430.

```sql
SELECT customer_id, order_date, amount,
       SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS running_total
FROM orders
ORDER BY customer_id, order_date;
```

- **The previous order's amount:** `LAG` looks one row back. The first row
  gets NULL.

```sql
SELECT customer_id, order_date, amount,
       LAG(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_amount
FROM orders
ORDER BY customer_id, order_date;
```

- **The second highest amount:** this gives 300. Use `DISTINCT`, so the two
  orders of 300 do not count twice.

```sql
SELECT DISTINCT amount
FROM orders
ORDER BY amount DESC
LIMIT 1 OFFSET 1;
```

**Common mistakes:** putting `rnk <= 2` in the same query as `RANK()`, using
`ROW_NUMBER` when ties should share a rank, and forgetting the last
`ORDER BY` tie breaker (`customer_id`).

---

## Part C: Multiple choice (20 questions)

### 1. pandas `loc` and `iloc`

**Question:** `df` has 10 rows and the default index 0 to 9. How many rows do
`df.loc[0:2]` and `df.iloc[0:2]` return?

- A. 2 and 2
- B. 3 and 2
- C. 2 and 3
- D. 3 and 3

**How to work it out:** `loc` works with labels and includes the end label, so
it gives labels 0, 1 and 2 (3 rows). `iloc` works with positions like normal
Python slicing and leaves out the end, so it gives positions 0 and 1 (2 rows).

**Answer: B.** Remember: `loc` means labels, end included. `iloc` means
positions, end left out.

### 2. `groupby` with `transform`

**Question:** What does `df.groupby("user")["amount"].transform("sum")` return?

- A. One row per user with their total
- B. A Series the same length as `df`, where each row holds its user's total
- C. A DataFrame with the sum of every column
- D. An error unless you call `reset_index()` first

**How to work it out:** think about the shape of the result. `agg` or `sum`
gives one row per group. `transform` gives one value per original row, filled
with that row's group result. That is useful for things like "each row's share
of its user's total".

**Answer: B.**

### 3. Mean with a missing value

**Question:** `s = pd.Series([1, None, 3])`. What does `s.mean()` return?

- A. `nan`
- B. `2.0`
- C. `1.33`
- D. An error

**How to work it out:** pandas skips missing values by default, so it averages
only 1 and 3: (1 + 3) / 2 = 2.0. NumPy does not skip them. `np.mean` on an
array with `nan` gives `nan`, and you need `np.nanmean` to skip them.

**Answer: B.**

### 4. NumPy broadcasting

**Question:** `a.shape` is `(3, 1)` and `b.shape` is `(4,)`. What is
`(a + b).shape`?

- A. `(3, 4)`
- B. `(4, 3)`
- C. An error
- D. `(3, 1)`

**How to work it out:** line the shapes up from the right. A missing size
counts as 1. Each pair of sizes must be equal, or one of them must be 1, and
the 1 stretches to match. Here `(3, 1)` and `(1, 4)` give `(3, 4)`.

**Answer: A.**

### 5. p-value

**Question:** A test gives a p-value of 0.03. What does this mean?

- A. There is a 3% chance the null hypothesis is true
- B. If the null hypothesis were true, a result at least this extreme would happen 3% of the time
- C. There is a 97% chance the alternative hypothesis is true
- D. The effect is large

**How to work it out:** a p-value assumes the null hypothesis is true, then asks
how surprising your data would be. It is never the chance that a hypothesis is
true, and it says nothing about how big the effect is.

**Answer: B.**

### 6. Bayes' rule (false alarms)

**Question:** 1% of transactions are fraud. A rule flags 90% of fraud and 5% of
normal transactions. A transaction is flagged. What is the chance it is fraud?

- A. 90%
- B. 50%
- C. About 15%
- D. 5%

**How to work it out:** imagine 10,000 transactions, which makes the sum easy.

- 100 are fraud, and the rule flags 90% of them: 90.
- 9,900 are normal, and the rule flags 5% of them: 495.
- That is 585 flagged in total, and 90 of them are fraud: 90 / 585 = 0.154,
  about 15%.

Use this "imagine 10,000" trick for any Bayes question. When the thing you are
looking for is rare, most alarms are false.

**Answer: C.**

### 7. Confidence interval width

**Question:** To make a 95% confidence interval for a mean half as wide, you
need about how much data?

- A. 2 times as much
- B. 4 times as much
- C. 8 times as much
- D. Half as much

**How to work it out:** the width shrinks with the square root of the sample
size. To halve the width, the square root of n must double, so n must be 4
times bigger.

**Answer: B.**

### 8. Type I error

**Question:** What is a Type I error?

- A. Rejecting the null hypothesis when it is true
- B. Not rejecting the null hypothesis when it is false
- C. Using the wrong test
- D. A bug in the data

**How to work it out:** Type I is a false alarm, where you see an effect that
is not there. Type II is a miss, where you fail to see an effect that is
there.

**Answer: A.**

### 9. Overfitting

**Question:** A model has 99% training accuracy and 70% validation accuracy.
What is the most likely problem, and a good fix?

- A. Underfitting, so add more features
- B. Overfitting, so add regularisation, get more data or use a simpler model
- C. Data leakage, so train for longer
- D. The learning rate is too low, so raise it

**How to work it out:** a big gap between training and validation scores means
the model memorised the training data. That is overfitting. The fixes are
regularisation, more data, a simpler model, early stopping or dropout. If both
scores were low, it would be underfitting.

**Answer: B.**

### 10. L1 and L2 regularisation

**Question:** Which regularisation tends to set some weights to exactly zero?

- A. L1 (Lasso)
- B. L2 (Ridge)
- C. Dropout
- D. Batch normalisation

**How to work it out:** L1 adds the size of each weight to the loss, and this
pushes small weights all the way to 0, which removes those features. L2 adds
the squared weights, which makes weights small but rarely exactly 0.

**Answer: A.**

### 11. Metric for rare classes

**Question:** 1% of the data is fraud. A model that always predicts "not fraud"
gets 99% accuracy. Which metric is better here?

- A. Accuracy
- B. PR AUC (or precision and recall)
- C. R squared
- D. Mean squared error

**How to work it out:** accuracy is dominated by the common class, so it hides
a useless model. Precision, recall, F1 and PR AUC look at the rare class.
R squared and mean squared error are for regression.

**Answer: B.**

### 12. Precision and recall

**Question:** A model flags 50 transactions and 40 of them are fraud. There are
100 fraud cases in total. What are precision and recall?

- A. 0.8 and 0.4
- B. 0.4 and 0.8
- C. 0.8 and 0.5
- D. 0.5 and 0.4

**How to work it out:**

- **Precision** asks: of what I flagged, how much was right? 40 / 50 = 0.8.
- **Recall** asks: of all the real cases, how many did I catch? 40 / 100 = 0.4.

**Answer: A.**

### 13. Data leakage

**Question:** Which of these causes data leakage?

- A. Fitting a `StandardScaler` on the full dataset before the train and test split
- B. Fitting the scaler on the training set, then using it on the test set
- C. Using a stratified split
- D. Setting a random seed

**How to work it out:** leakage is any information from the test data reaching
training. A scaler fitted on all the data has learned the test set's mean and
spread. Split first, fit on the training set only, then apply it to both.

**Answer: A.**

### 14. Random forest and gradient boosting

**Question:** Which statement about random forests and gradient boosting is
true?

- A. Both train their trees one after another
- B. A random forest trains trees independently and averages them. Boosting trains trees one after another, each fixing the errors of the ones before
- C. Boosting averages independent trees. A random forest trains them one after another
- D. Neither uses decision trees

**How to work it out:** a random forest is "bagging": many trees, each trained
on a random sample, averaged together. This mainly lowers variance. Boosting
adds small trees one at a time, each one fitting what the model still gets
wrong. This mainly lowers bias.

**Answer: B.**

### 15. Validating a time series model

**Question:** You are forecasting next month's sales. How should you validate
the model?

- A. Random k-fold cross-validation
- B. Train on earlier dates and test on later dates, for example with a rolling or expanding window
- C. Test on the training data
- D. Shuffle the rows, then split 80/20

**How to work it out:** the model must never see the future during training.
Random splits mix future rows into training. Use time-ordered splits.
(Your forecasting project used rolling-origin backtesting across 6 folds,
which you can mention if asked.)

**Answer: B.**

### 16. Semantic segmentation

**Question:** What does semantic segmentation do?

- A. Gives one label to the whole image
- B. Draws boxes around objects
- C. Gives a class to every pixel
- D. Groups similar images together

**How to work it out:** classification gives one label per image. Detection
draws boxes. Semantic segmentation gives a class to every pixel. Instance
segmentation also tells apart separate objects of the same class.

**Answer: C.**

### 17. IoU and Dice

**Question:** A predicted mask has 50 pixels and the true mask has 40. They
overlap on 30 pixels. What are the IoU and the Dice score?

- A. 0.5 and 0.667
- B. 0.6 and 0.75
- C. 0.75 and 0.6
- D. 0.667 and 0.5

**How to work it out:**

- **IoU** is overlap divided by union. The union is both masks minus the
  overlap: `50 + 40 - 30 = 60`, so IoU = 30 / 60 = 0.5.
- **Dice** is twice the overlap divided by the two sizes added: `2 x 30 /
  (50 + 40) = 0.667`.

Dice is always at least as big as IoU.

**Answer: A.**

### 18. Training with point labels

**Question:** Only a few pixels in each training image have labels (point
labels). What is the right way to compute the cross-entropy loss?

- A. Treat every unlabelled pixel as background
- B. Compute the loss only on labelled pixels and divide by the number of labelled pixels
- C. Fill each unlabelled pixel with the nearest label, then train normally
- D. Skip images where fewer than half the pixels are labelled

**How to work it out:** an unlabelled pixel is unknown, not background.
Calling it background (A) or guessing it (C) teaches the model wrong answers,
and D throws away almost all the data. So count the loss only where a label
exists, and average over those pixels. This is the idea behind the partial
cross-entropy in Meriti's assessment PDF.

**Answer: B.**

### 19. Focal loss

**Question:** What does focal loss change compared with plain cross-entropy?

- A. It gives more weight to easy, well classified examples
- B. It gives less weight to easy examples, so training focuses on hard ones. With gamma set to 0 it is plain cross-entropy
- C. It only works for regression
- D. It removes the need for labels

**How to work it out:** focal loss multiplies the cross-entropy by
`(1 - p) ** gamma`, where `p` is the predicted chance of the right class. An
easy example has `p` near 1, so the multiplier is near 0 and its loss almost
disappears. Hard examples keep most of their loss. With `gamma = 0`, the
multiplier is 1, which is plain cross-entropy. It helps when some classes are
rare.

**Answer: B.**

### 20. Transfer learning

**Question:** You have very little labelled data for an image model. Why start
from an encoder pretrained on ImageNet?

- A. It makes the model smaller
- B. It reuses features already learned from millions of images, so the model needs fewer labels to learn well
- C. It removes the need for a validation set
- D. ImageNet contains satellite images of every place

**How to work it out:** early layers learn general things like edges, colours
and textures, which are useful for most images. Reusing them means your few
labels only need to teach the last part of the model.

**Answer: B.**

---

## Part D: Video answers (about 2 minutes each)

How to answer any video question:

- Look at the camera and speak slowly.
- Use a simple order: what, how, the hard part, the result.
- Give one or two real numbers.
- Stop at about 2 minutes.

Record yourself on your phone, then watch it back.

### D1. A system you built

**Question:** Walk us through a machine learning system you built. What was the
hardest part, and how did you solve it?

**How to build the answer:** use the order "what I built, how I measured it,
the hard part, what I did, the result". Pick your strongest project and say
one or two sentences for each part.

**Model answer (fraud project; every fact is from your CV)**

- **What:** I built a fraud detection system that reads each customer's history
  of transactions. I compared three sequence models, a GRU, a TCN and a
  Transformer, with a strong LightGBM baseline.
- **How I measured it:** PR AUC, and precision in the top 0.1%, 0.5% and 1% of
  transactions, because a fraud team can only review a few. I used 3 seeds and
  broke the results down by attack type.
- **The hard part:** class imbalance. Focal loss hurt calibration (ECE 0.0063),
  and weighted sampling cost 0.042 PR AUC instead.
- **What I did:** I fixed calibration with temperature scaling and isotonic
  regression, which brought ECE down to 0.0005.
- **The result:** the sequence models cut expected cost per transaction by 27%.
  I exported the model to ONNX Runtime, which ran 2.9 times faster than
  PyTorch at batch size 1, and served it at 5.1 ms p99 against a 50 ms budget.

### D2. Segmentation with few labels

**Question:** You have satellite images where only a few pixels in each image
are labelled. How would you train a segmentation model?

**How to build the answer:** say the problem in one line, give your plan in
steps, then say how you would check that it works.

**Model answer**

- **The problem:** only a few pixels are labelled, so the model has very little
  to learn from.
- **Plan:**
  1. Start from a pretrained encoder, so the few labels go further.
  2. Compute the loss only on labelled pixels, averaged over them, and never
     treat unlabelled pixels as background.
  3. If some classes are rare, use focal loss or class weights.
  4. Use flips and rotations as augmentation, since satellite images have no
     fixed "up".
  5. Optionally, use confident predictions on unlabelled pixels as extra
     labels (semi-supervised learning).
- **How I would check it:** measure mean IoU for each class on a small, fully
  labelled validation set.

### D3. Remote work in PST hours

**Question:** This role is remote and works PST hours. How will you work well
with the team?

**How to build the answer:** give a clear yes, the exact hours, how you will
keep in touch, then when you can start.

**Model answer**

- **Hours:** I work in UTC+1 and can work PST hours. Until 1 November, US
  Pacific time is UTC minus 7, so 9am to 5pm there is 5pm to 1am for me. After
  1 November it is 6pm to 2am.
- **Updates:** a short written update at the end of each day, saying what I
  did, what is next and what is blocking me.
- **Questions:** I ask early in the shared hours rather than waiting a day.
- **Start:** I can start immediately.

---

## Before the real test

- Have 3 free hours in one block.
- Charge your laptop, and check your internet, camera and microphone (for the
  video answers).
- Read each question to the end, including the ChallengeToken line.
- Get a simple working answer in first, then improve it.
- Never change the last line of the starter code.
- Stay on the test tab and type your own code.
- Do it alone, as Meriti asked.
