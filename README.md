## Usage
pip install requirements.txt use a virtual environment etc etc

At some point, I will develop a user interface to make it easier to run things as the calculations become more complicated. For now, budgeting trajectories are run in-file, and the setup is simple. You enter your income and expenses, and then define the parameters of the simulation, which I call a "budget sheet". The budget sheet consists of a start date, end date, and your income/expenses, and it computes how much money you will have for each day during the specified time period. This is what the process looks like:
<ol>
  <li>Define income and expenses uses the eponymous classes, e.g.</li>

```python
income1 = Income("Work", 1000, "weekly", "2024 09 01")
expense1 = Expense("Rent", 1200, "monthly", "2024 09 01")
```
<ol><li>Note: the second argument is the monetary value and the third argument is the frequency at which that monetary value is paid to you. Currently supported frequencies are monthly, biweekly (every two weeks), and weekly. The third argument is when you want this item to begin payouts/expenses in the budget sheet. The optional fourth argument is when you want the item to conclude payouts/expenses; if not specified, it concludes at the latest possible time before the budget sheet end date.</li>
  <li>Also note the syntax for dates: "yyyy mm dd".</li>
</ol>
</li>
<li>Pass items into a budget sheet object as a list (order is not important) and specify start and end dates, e.g.</li>

```python
budget_sheet = BudgetSheet([income1, expense1], "2024 09 01", "2024 12 31")
```

<li>Create the budget sheet (when income and expenses will occur, and what your balance will be at that time) by calling `create_budget_sheet` on the budget sheet object: 

```python
budget_sheet.create_budget_sheet()
```
</li>

<li>To create a graph of balance over time, create a GenerateTrajectory object and call `plot_trajectory`. This is where you specifiy your starting account balance, as the second argument. The other arguments are things I was playing around with including that I may or may not keep, so don't worry about them.</li>

```python
GenerateTrajectory(budget_sheet, 5000).plot_trajectory()
```
</ol>
