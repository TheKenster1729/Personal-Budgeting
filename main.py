import datetime
import numpy as np
import pandas as pd
from math import floor
from dateutil import relativedelta, rrule
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# <---APPLICATION STRUCTURE--->#
"""
"""

class Item:
    def __init__(self, name, category, amount, interval, start_date, end_date = None):
        self.name = name
        self.category = category
        self.amount = amount
        self.interval = interval

        # converting start and end dates to datetime objects
        year_start, month_start, day_start = start_date.split(" ")
        self.start_date = pd.Timestamp(year = int(year_start), month = int(month_start), day = int(day_start))
        if end_date:
            year_end, month_end, day_end = end_date.split(" ")
            self.end_date = pd.Timestamp(year = int(year_end), month = int(month_end), day = int(day_end))
        else: # set end date to maximum possible, actual end date will be set by the budget sheet
            self.end_date = pd.Timestamp(year = datetime.MAXYEAR, month = 12, day = 31)

class Expense(Item):
    def __init__(self, name, amount, interval, start_date, end_date = None):
        super().__init__(name, "Expense", amount, interval, start_date, end_date = end_date)

class Income(Item):
    def __init__(self, name, amount, interval, start_date, end_date = None):
        super().__init__(name, "Income", amount, interval, start_date, end_date = end_date)

class BudgetSheet:
    def __init__(self, items, start_date, end_date):
        self.items = items
        self.start_date = start_date
        self.end_date = end_date

    def create_budget_sheet(self):
        year_start, month_start, day_start = self.start_date.split(" ")
        year_end, month_end, day_end = self.end_date.split(" ")

        self.timestamp_start_date = pd.Timestamp(year = int(year_start), month = int(month_start), day = int(day_start)) # datetime.date(int(year_start), int(month_start), int(day_start))
        self.timestamp_end_date = pd.Timestamp(year = int(year_end), month = int(month_end), day = int(day_end)) # datetime.date(int(year_end), int(month_end), int(day_end))

        self.budget_sheet_df = pd.DataFrame(columns = ["Date", "Type", "Amount", "Interval"])
        for item in self.items:
            if not item.interval: # one time purchase
                item_df = pd.DataFrame(data = [[item.start_date, item.category, item.amount, item.interval]], columns = ["Date", "Type", "Amount", "Interval"],
                                        index = [item.name])
            else: # recurring purchase
                item_df = self.unpack_interval_event(item)

            if item.category == "Expense": # make expenses negative
                item_df["Amount"] = item_df["Amount"].apply(lambda x: -1*x)

            self.budget_sheet_df = pd.concat([self.budget_sheet_df, item_df])

        return self.budget_sheet_df

    def unpack_interval_event(self, item):
        
        weekdays = {0: rrule.MO, 1: rrule.TU, 2: rrule.WE, 3: rrule.TH, 4: rrule.FR, 5: rrule.SA, 6: rrule.SU}

        start_month = self.timestamp_start_date.month
        start_year = self.timestamp_start_date.year

        item_day = item.start_date.day
        item_weekday = weekdays[item.start_date.weekday()]

        # end date is the item end date if it is before the end of the budget sheet, budget sheet end date otherwise
        end_date_for_item = item.end_date if item.end_date <= self.timestamp_end_date else self.timestamp_end_date

        # for monthly recurrence
        if item.interval == "monthly":
            next_item_occurence_guess = pd.Timestamp(year = start_year, month = start_month, day = item_day)
            if next_item_occurence_guess >= self.timestamp_start_date: # this means the item occurs in the month of the start of the budget sheet
                item_budgetsheet_start = next_item_occurence_guess
            else: # item start date for this budget sheet is next month
                item_budgetsheet_start = next_item_occurence_guess.replace(month = next_item_occurence_guess.month + 1)

            unpacked_items_dates = rrule.rrule(freq = rrule.MONTHLY, dtstart = item_budgetsheet_start, wkst = rrule.MO, until = end_date_for_item)

        # for biweekly occurence
        if item.interval == "biweekly":
            item_budgetsheet_start = self.timestamp_start_date + relativedelta.relativedelta(weekday = item_weekday)
            unpacked_items_dates = rrule.rrule(freq = rrule.WEEKLY, interval = 2, dtstart = item_budgetsheet_start,
                                               wkst = rrule.MO, until = end_date_for_item)
            
        # weekly occurence
        if item.interval == "weekly":
            item_budgetsheet_start = self.timestamp_start_date + relativedelta.relativedelta(weekday = item_weekday)
            unpacked_items_dates = rrule.rrule(freq = rrule.WEEKLY, interval = 1, dtstart = item_budgetsheet_start,
                                               wkst = rrule.MO, until = end_date_for_item)

        unpacked_items_df = pd.DataFrame([[i, item.category, item.amount, item.interval] for i in unpacked_items_dates],
                                         index = [item.name for i in range(len(list(unpacked_items_dates)))],
                                         columns = ["Date", "Type", "Amount", "Interval"])
        
        return unpacked_items_df

class GenerateTrajectory:
    def __init__(self, budget_sheet, starting_account_balance, food_level = 0, amenities_level = 0, savings_level = 0,
                 trajectory_interval = 1):
        self.start_date = budget_sheet.timestamp_start_date
        self.end_date = budget_sheet.timestamp_end_date
        self.starting_balance = starting_account_balance
        self.food_level = food_level
        self.amenities_level = amenities_level
        self.savings_level = savings_level

        # adding in starting balance as an income and ordering by date
        starting_balance_df = pd.DataFrame([[self.start_date, "Income", self.starting_balance, None]], 
                                 index = ["Starting Balance"],
                                 columns = ["Date", "Type", "Amount", "Interval"])
        self.budget_sheet_df = pd.concat([budget_sheet.budget_sheet_df, starting_balance_df]).sort_values(by = "Date")

    def create_food_budget_sheet(self, food_level):
        pass

    def run_trajectory(self):
        agg_budget_sheet_amounts = self.budget_sheet_df["Amount"].cumsum()
        self.budget_sheet_df["Agg"] = agg_budget_sheet_amounts
        print(self.budget_sheet_df)
    
    def plot_trajectory(self):
        self.run_trajectory()

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x = self.budget_sheet_df["Date"], y = self.budget_sheet_df["Agg"])
        )

        fig.show()

rent = Expense("Rent", 1200, "monthly", "2024 09 01")
food = Expense("Food", 200, "monthly", "2024 09 01")
work = Income("Work", 1000, "weekly", "2024 09 03")
other_expenses = Expense("Other", 200, "monthly", "2024 09 01")

if __name__ == "__main__":
    sheet1 = BudgetSheet([rent, food, work, other_expenses], "2024 09 01", "2024 12 31")
    sheet1.create_budget_sheet()
    GenerateTrajectory(sheet1, 5000).plot_trajectory()