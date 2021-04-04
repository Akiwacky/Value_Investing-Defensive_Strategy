import pandas as pd
import requests
import os

bs = "BALANCE_SHEET"
income_s = "INCOME_STATEMENT"


class FetchFinancialData:
    def __init__(self, symbol, current_price):
        self.symbol = symbol
        self.current_price = current_price
        self.API_KEY = f"{os.environ.get('API_KEY')}"
        self.balance_sheet = {}
        self.income_statement = {}
        self.eps = {}
        self.eps_end_of_three_yr_avg = 0
        self.req_five_benchmark = 1.33
        self.req_six_benchmark = 22.5
        self.req_seven_benchmark = 15

    def fetch_role(self, role):
        """
        Retrieves a dataframe of the symbol's annual function for the last five years
        :param role: Financial function you are looking to retrieve - BalanceSheet, IncomeStatement, CashFlow
        :param symbol: The stock ticker
        """
        params = {
            "function": role,
            "symbol": self.symbol,
            "apikey": self.API_KEY
        }
        response = requests.get("https://www.alphavantage.co/query?", params=params)
        df = pd.DataFrame(response.json()['annualReports']).T
        # Sort Data
        header = df.iloc[0]
        df = df.iloc[2:]
        df.columns = header
        df = df.replace('None', '0')
        df = round(df.astype(float) / 1000000,0)
        # Save Data
        if role == "BALANCE_SHEET":
            self.balance_sheet = df
        else:
            self.income_statement = df

    def financial_condition(self):

        self.fetch_role(bs)

        # Requirement 2
        current_assets = self.balance_sheet.loc['totalCurrentAssets'][0]
        current_liabilities = self.balance_sheet.loc['totalCurrentLiabilities'][0]
        long_term_debt = self.balance_sheet.loc['longTermDebt'][0]
        net_current_assets = current_assets - current_liabilities

        if current_assets >= current_liabilities * 2:
            print("PASSED: Current Assets Twice Current Liabilities")
            if long_term_debt <= net_current_assets:
                print("PASSED: Net Current Assets Less than Long Term Debt")
                self.net_income_strength()
            else:
                print("FAILED: Net Current Assets Not Less than Long Term Debt")
        else:
            print("FAILED: Current Assets Not Twice Current Liabilities")

    def net_income_strength(self):

        self.fetch_role(income_s)

        # Requirement 4
        net_income = [income for income in self.income_statement.loc['netIncome'] if income < 0]
        if not net_income:
            print("PASSED: No Earnings Loss in the Past 5 Years")
            self.eps_calculation()
        else:
            print("FAILED: Earnings Loss in the Past 5 Years")

    def eps_calculation(self):
        """
        Retrieves EPS for the past 10 years
        :return:
        """
        params = {
            "function": "EARNINGS",
            "symbol": self.symbol,
            "apikey": self.API_KEY
        }
        response = requests.get("https://www.alphavantage.co/query?", params=params)
        df = pd.DataFrame(response.json()['annualEarnings'][1:11])
        df.set_index('fiscalDateEnding')
        self.eps = df

        # Requirement 5
        beg_3_yr = [float(eps) for eps in df['reportedEPS'][-3:]]
        beg_3_yr_avg = sum(beg_3_yr) / len(beg_3_yr)
        end_3_yr = [float(eps) for eps in df['reportedEPS'][:3]]
        end_3_yr_avg = sum(end_3_yr) / len(end_3_yr)
        self.eps_end_of_three_yr_avg = end_3_yr_avg

        if beg_3_yr_avg * self.req_five_benchmark <= end_3_yr_avg:
            print("PASSED: EPS Growth at least One-Third in the Past 10 Years")
            self.book_value_ratio()
        else:
            print("FAILED: EPS Growth less than One-Third in the Past 10 Years")

    def book_value_ratio(self):
        # Requirement 6
        total_tangible_assets = self.balance_sheet.loc['totalAssets'][0] - \
                                 self.balance_sheet.loc['intangibleAssets'][0]

        total_liabilities = self.balance_sheet.loc['totalLiabilities'][0]
        no_os_shares = self.balance_sheet.loc['commonStockSharesOutstanding'][0]

        book_value_per_share = (total_tangible_assets - total_liabilities) / no_os_shares

        if self.current_price <= book_value_per_share * 1.5:
            print("PASSED: Current Price Not More than 1.5 times Book Value")

            current_eps = float(self.eps['reportedEPS'][1])
            pe_ratio = self.current_price / current_eps
            if pe_ratio * book_value_per_share <= self.req_six_benchmark:
                print("PASSED: P/E Times Book Value Does not Exceed 22.5", True)
                self.moderate_pe_ratio()
            else:
                print("PASSED: P/E Times Book Value Exceeds 22.5")
        else:
            print("FAILED: Current Price More than 1.5 times Book Value")

    def moderate_pe_ratio(self):
        # Requirement 7
        mod_pe_ratio = self.current_price / self.eps_end_of_three_yr_avg
        if mod_pe_ratio <= self.req_seven_benchmark:
            print("PASSED: Price No More than 15 times Average Earnings")
            print(f"{self.symbol} PASSES TEST")
        else:
            print("FAILED: Price More than 15 times Average Earnings")
