# Mock test: Meriti Inc data science test (Coderbyte)

A practice test built to look like the real one. Do it once, in one sitting,
before you open the real link.

## What we know about the real test

These come from the real test page and from research on how Coderbyte tests work.

- **Time:** 3 hours, one sitting. The timer cannot be paused, and you cannot
  leave and come back.
- **Type:** made from Coderbyte's Data Science template. Video answers are
  switched on, so some questions will ask you to talk on camera.
- **Likely parts:** Python coding challenges, maybe SQL and a data question,
  multiple choice on statistics and ML, and video answers. Coderbyte tests of
  this length usually have up to 5 coding challenges plus questions.
- **Coding screen:** the question and some sample tests are on the left and the
  editor is on the right. Hidden test cases mark your code on a 1 to 10 scale.
- **Names:** coding challenges are called "String Challenge", "Array Challenge",
  "Searching Challenge" or "Math Challenge", each marked Easy, Medium or Hard.
- **Starter code:** the editor gives you something like this. Never change the
  last line.

  ```python
  def StringChallenge(strParam):
      # your code goes here
      return strParam

  # do not change this line
  print(StringChallenge(input()))
  ```

- **The ChallengeToken step:** many challenges end with an extra step that uses
  a short code called a ChallengeToken. Your answer is only right if this step
  is right too. Three styles seen in real tests:
  1. **Intersperse:** mix the output and the token one character at a time.
     Output `base,ball` with token `r1omjb4zabc` becomes `bra1soem,jbba4lzlabc`.
  2. **Wrap:** put `--` on both sides of every output character that appears in
     the token.
  3. **Remove:** delete every output character that appears in the token
     (ignore case). If nothing is left, return `EMPTY`.
- **Rules:** do not paste code from outside the editor, and do not leave the
  tab. Coderbyte flags both. Short comments that explain your thinking are
  welcome.

## How to use this mock

1. Set a timer for 3 hours. Use a plain editor with no AI help, just like the
   real test.
2. Do Parts A to D in order. Do not look at the answer key until the end.
3. Mark yourself with the key. Look again at the topics behind anything you
   missed.

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

### A2. Array Challenge (Easy, 10 min)

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

### A3. Searching Challenge (Medium, 25 min)

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

### A4. Math Challenge (Hard, 20 min)

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

---

## Part B: Data and SQL

### B1. Data Challenge (Medium, 15 min)

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

User 1 has 90.50 and user 3 has 80. User 2 has 200, because their rows with an
empty amount and with `abc` are ignored, so they have one valid transaction.

### B2. SQL: team sizes (Medium, 15 min)

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

### B3. SQL: top customers per month (Medium, 15 min)

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

---

## Part C: Multiple choice (20 questions, 30 min)

**1.** `df` has 10 rows and the default index 0 to 9. How many rows do
`df.loc[0:2]` and `df.iloc[0:2]` return?

- A. 2 and 2
- B. 3 and 2
- C. 2 and 3
- D. 3 and 3

**2.** What does `df.groupby("user")["amount"].transform("sum")` return?

- A. One row per user with their total
- B. A Series the same length as `df`, where each row holds its user's total
- C. A DataFrame with the sum of every column
- D. An error unless you call `reset_index()` first

**3.** `s = pd.Series([1, None, 3])`. What does `s.mean()` return?

- A. `nan`
- B. `2.0`
- C. `1.33`
- D. An error

**4.** `a.shape` is `(3, 1)` and `b.shape` is `(4,)`. What is `(a + b).shape`?

- A. `(3, 4)`
- B. `(4, 3)`
- C. An error
- D. `(3, 1)`

**5.** A test gives a p-value of 0.03. What does this mean?

- A. There is a 3% chance the null hypothesis is true
- B. If the null hypothesis were true, a result at least this extreme would happen 3% of the time
- C. There is a 97% chance the alternative hypothesis is true
- D. The effect is large

**6.** 1% of transactions are fraud. A rule flags 90% of fraud and 5% of
normal transactions. A transaction is flagged. What is the chance it is fraud?

- A. 90%
- B. 50%
- C. About 15%
- D. 5%

**7.** To make a 95% confidence interval for a mean half as wide, you need
about how much data?

- A. 2 times as much
- B. 4 times as much
- C. 8 times as much
- D. Half as much

**8.** What is a Type I error?

- A. Rejecting the null hypothesis when it is true
- B. Not rejecting the null hypothesis when it is false
- C. Using the wrong test
- D. A bug in the data

**9.** A model has 99% training accuracy and 70% validation accuracy. What is
the most likely problem, and a good fix?

- A. Underfitting, so add more features
- B. Overfitting, so add regularisation, get more data or use a simpler model
- C. Data leakage, so train for longer
- D. The learning rate is too low, so raise it

**10.** Which regularisation tends to set some weights to exactly zero?

- A. L1 (Lasso)
- B. L2 (Ridge)
- C. Dropout
- D. Batch normalisation

**11.** 1% of the data is fraud. A model that always predicts "not fraud" gets
99% accuracy. Which metric is better here?

- A. Accuracy
- B. PR AUC (or precision and recall)
- C. R squared
- D. Mean squared error

**12.** A model flags 50 transactions and 40 of them are fraud. There are 100
fraud cases in total. What are precision and recall?

- A. 0.8 and 0.4
- B. 0.4 and 0.8
- C. 0.8 and 0.5
- D. 0.5 and 0.4

**13.** Which of these causes data leakage?

- A. Fitting a `StandardScaler` on the full dataset before the train and test split
- B. Fitting the scaler on the training set, then using it on the test set
- C. Using a stratified split
- D. Setting a random seed

**14.** Which statement about random forests and gradient boosting is true?

- A. Both train their trees one after another
- B. A random forest trains trees independently and averages them. Boosting trains trees one after another, each fixing the errors of the ones before
- C. Boosting averages independent trees. A random forest trains them one after another
- D. Neither uses decision trees

**15.** You are forecasting next month's sales. How should you validate the
model?

- A. Random k-fold cross-validation
- B. Train on earlier dates and test on later dates, for example with a rolling or expanding window
- C. Test on the training data
- D. Shuffle the rows, then split 80/20

**16.** What does semantic segmentation do?

- A. Gives one label to the whole image
- B. Draws boxes around objects
- C. Gives a class to every pixel
- D. Groups similar images together

**17.** A predicted mask has 50 pixels and the true mask has 40. They overlap on
30 pixels. What are the IoU and the Dice score?

- A. 0.5 and 0.667
- B. 0.6 and 0.75
- C. 0.75 and 0.6
- D. 0.667 and 0.5

**18.** Only a few pixels in each training image have labels (point labels).
What is the right way to compute the cross-entropy loss?

- A. Treat every unlabelled pixel as background
- B. Compute the loss only on labelled pixels and divide by the number of labelled pixels
- C. Fill each unlabelled pixel with the nearest label, then train normally
- D. Skip images where fewer than half the pixels are labelled

**19.** What does focal loss change compared with plain cross-entropy?

- A. It gives more weight to easy, well classified examples
- B. It gives less weight to easy examples, so training focuses on hard ones. With gamma set to 0 it is plain cross-entropy
- C. It only works for regression
- D. It removes the need for labels

**20.** You have very little labelled data for an image model. Why start from
an encoder pretrained on ImageNet?

- A. It makes the model smaller
- B. It reuses features already learned from millions of images, so the model needs fewer labels to learn well
- C. It removes the need for a validation set
- D. ImageNet contains satellite images of every place

---

## Part D: Video answers (about 2 minutes each)

Answer out loud and time yourself. Record yourself on your phone if you can,
then watch it back.

**D1.** Walk us through a machine learning system you built. What was the
hardest part, and how did you solve it?

**D2.** You have satellite images where only a few pixels in each image are
labelled. How would you train a segmentation model?

**D3.** This role is remote and works PST hours. How will you work well with
the team?

---

## Answer key

Stop here until you have finished Parts A to D.

### Token helpers

All three ChallengeToken styles, in Python:

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

### A1 answer

```python
def StringChallenge(s):
    ok = (4 <= len(s) <= 25
          and s[0].isalpha()
          and all(c.isalnum() or c == "_" for c in s)
          and not s.endswith("_"))
    return intersperse("true" if ok else "false", "k7m2xq")
```

Hidden tests: `"1abc_def"` gives `fka7lms2exq` because it starts with a number.
`"Code_Land99"` gives `tkr7ume2xq`.

What people get wrong: checking only the length, or forgetting the "cannot end
with an underscore" rule.

### A2 answer

```python
def ArrayChallenge(strArr):
    a = [int(x) for x in strArr[0].split(",")]
    b = set(int(x) for x in strArr[1].split(","))
    common = [x for x in a if x in b]
    out = ",".join(str(x) for x in common) if common else "false"
    return wrap_token_chars(out, "13ab")
```

Hidden tests: `["1, 3, 9, 10, 17, 18", "1, 4, 9, 10"]` gives `--1--,9,--1--0`.
`["4", "4"]` gives `4`.

What people get wrong: comparing the numbers as text, so `" 4"` does not match
`"4"`. `int()` removes the spaces for you. Using a set keeps it fast.

### A3 answer

This is a sliding window. Move the right edge until the window has everything,
then move the left edge in as far as you can, and remember the shortest window.

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

Hidden tests: `["ahffaksfajeeubsne", "jefaa"]` gives `aksfaje`, final
`axk9szfaje`. `["aaffhkksemckelloe", "fhea"]` gives `affhkkse`, final
`axf9fzhkkse`.

A simpler way that also passes at this size (strings up to 50 characters):
try every window length from `len(k)` upward and return the first window that
has all of K's characters. If you get stuck in the real test, write the simple
version first, then improve it.

### A4 answer

The answer is the Catalan number: C(n) = (2n)! / ((n + 1)! n!).

```python
import math

def MathChallenge(num):
    out = str(math.comb(2 * num, num) // (num + 1))
    return remove_token_chars(out, "2x7")
```

If you do not remember the formula, count the arrangements with recursion: add
`(` while you have some left, and add `)` while it would still close an open
bracket.

```python
def count(n):
    total = 0
    def go(opened, closed):
        nonlocal total
        if opened == n and closed == n:
            total += 1
            return
        if opened < n:
            go(opened + 1, closed)
        if closed < opened:
            go(opened, closed + 1)
    go(0, 0)
    return total
```

Hidden tests: 4 gives `14`. 5 gives 42, final `4`. 6 gives 132, final `13`.
10 gives 16796, final `1696`.

### B1 answer

Plain Python (tested):

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

pandas version (not run here, because pandas is not installed in this
workspace):

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

Hidden test 1, where users 4 and 5 tie at 120.25, so the smaller ID wins:

```
user_id,date,amount
4,2026-03-01,120.25
5,2026-03-02,60
4,2026-03-15,0
5,2026-02-20,60.25
6,2026-03-03,n/a
4,2026-02-27,
```

Output: `4:120.25:14`. The 2026-02-27 row has no amount, so its date is
ignored. An amount of 0 is still valid.

Hidden test 2, a tie at 100:

```
user_id,date,amount
8,2026-05-01,100
7,2026-05-04,60
7,2026-05-09,40
```

Output: `7:100.00:5`.

What people get wrong: dropping a row's amount but keeping its date, treating
0 as missing, and forgetting the tie rule.

### B2 answer

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

Tested in SQLite. SQLite prints 26.0, so the test there wraps it in
`CAST(... AS INTEGER)`. MySQL prints 26. Coderbyte shows which SQL version it
uses at the top of the question, so check it first.

### B3 answer

With window functions:

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

In MySQL, use `DATE_FORMAT(order_date, '%Y-%m')` instead of `strftime`. In
PostgreSQL, use `TO_CHAR(order_date, 'YYYY-MM')`.

| month | customer_id | total | rnk |
|---|---|---|---|
| 2026-01 | 10 | 350 | 1 |
| 2026-01 | 11 | 300 | 2 |
| 2026-01 | 12 | 300 | 2 |
| 2026-02 | 13 | 500 | 1 |
| 2026-02 | 10 | 80 | 2 |
| 2026-02 | 11 | 80 | 2 |

If the database has no window functions (old MySQL), a customer's rank is
1 plus the number of customers in the same month with a higher total. Use a
subquery to count them. Both versions were tested and give the table above.

Know the difference: `RANK()` gives 1, 2, 2, 4. `DENSE_RANK()` gives 1, 2, 2, 3.
`ROW_NUMBER()` gives 1, 2, 3, 4 and breaks ties at random.

### Part C answers

| Q | Answer | Why |
|---|---|---|
| 1 | B | `loc` uses labels and includes the end. `iloc` uses positions and leaves out the end. |
| 2 | B | `transform` keeps the original shape. `agg` gives one row per group. |
| 3 | B | pandas skips missing values by default: (1 + 3) / 2 = 2.0. Plain `np.mean` with a `nan` gives `nan`. |
| 4 | A | Broadcasting stretches (3, 1) and (4,) to (3, 4). |
| 5 | B | A p-value is about the data if the null is true. It is not the chance that the null is true. |
| 6 | C | 0.9 x 0.01 / (0.9 x 0.01 + 0.05 x 0.99) = 0.009 / 0.0585 = 0.154, so about 15%. |
| 7 | B | Width shrinks with the square root of n, so half the width needs 4 times the data. |
| 8 | A | Type I is a false alarm. Type II (B) is a miss. |
| 9 | B | A big gap between training and validation means overfitting. |
| 10 | A | L1 pushes weights to exactly 0. L2 makes them small but not 0. |
| 11 | B | With rare positives, accuracy hides the problem. PR AUC looks at the rare class. |
| 12 | A | Precision = 40 / 50 = 0.8. Recall = 40 / 100 = 0.4. |
| 13 | A | The scaler learns the test data's mean and spread before the split. |
| 14 | B | Bagging versus boosting. |
| 15 | B | Random folds let the model see the future. |
| 16 | C | One class per pixel. |
| 17 | A | IoU = 30 / (50 + 40 - 30) = 0.5. Dice = 2 x 30 / (50 + 40) = 0.667. |
| 18 | B | Unlabelled pixels are unknown, not background. Average only over the labelled ones. |
| 19 | B | Focal loss multiplies the loss by (1 - p) to the power gamma, so easy pixels count less. |
| 20 | B | This is transfer learning. Pretrained features make up for having few labels. |

### Part D model answers

These are outlines, not scripts. Say them in your own words. Every fact below
is from your CV.

**D1. A system you built (use the fraud project).**

- **What it does:** it detects fraud from each customer's history of
  transactions. I compared three sequence models (GRU, TCN and a Transformer)
  with a strong LightGBM baseline.
- **How I measured it:** PR AUC, and precision in the top 0.1%, 0.5% and 1% of
  transactions, because a fraud team can only review a few. I used 3 seeds and
  broke results down by attack type.
- **The hardest part:** class imbalance. Focal loss hurt calibration (ECE
  0.0063), and weighted sampling cost 0.042 PR AUC instead. I fixed calibration
  with temperature scaling and isotonic regression, which brought ECE down to
  0.0005.
- **The result:** the sequence models cut expected cost per transaction by 27%.
  I exported the model to ONNX Runtime, which ran 2.9 times faster than
  PyTorch at batch size 1, and served it at 5.1 ms p99 against a 50 ms budget.

**D2. Training with point labels.**

- Start from a pretrained encoder, so a few labels go further.
- Compute the loss only on labelled pixels, divided by the number of labelled
  pixels. Never treat unlabelled pixels as background.
- If some classes are rare, use focal loss or class weights.
- Use augmentation. Flips and rotations are safe for satellite images, which
  have no fixed "up".
- Optionally, add a semi-supervised step: use confident predictions on
  unlabelled pixels as extra labels.
- Measure mean IoU for each class on a small, fully labelled validation set.

**D3. Remote work in PST hours.**

- **Hours:** I work in UTC+1 and can work PST hours. Until 1 November, US
  Pacific time is UTC minus 7, so 9am to 5pm there is 5pm to 1am for me. After
  1 November it is 6pm to 2am.
- **Async work:** a short written update at the end of each day, saying what I
  did, what is next and what is blocking me.
- **Questions:** I ask early in the shared hours rather than waiting a day.
- **Start:** I can start immediately.

## Before the real test

- Have 3 free hours in one block.
- Charge your laptop, and check your internet, camera and microphone (for the
  video answers).
- Read each question to the end, including the ChallengeToken line.
- Get a simple working answer in first, then improve it.
- Never change the last line of the starter code.
- Stay on the test tab and type your own code.
- Do it alone, as Meriti asked.
