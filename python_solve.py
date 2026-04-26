import pandas as pd
df = pd.read_excel('daily_repayments.xlsx')

df['payment_date'] = pd.to_datetime(df['payment_date'], dayfirst=True, errors='coerce')

#------------------------------------------------------------------------------import pandas as pd
df = pd.read_excel('clients.xlsx')

df['last_updated'] = pd.to_datetime(df['last_updated'])
df = (
    df.sort_values('last_updated', ascending=False)
    .drop_duplicates(subset='client_id', keep='first').reset_index(drop=True)
)

#--------------------------------------------------------------------------
today = pd.Timestamp.today().normalize()
unpaid = df[df['paid'] == False].copy()
unpaid['due_date'] = pd.to_datetime(unpaid['due_date'])
dpd = (
  unpaid.groupby('client_id')['due_date']
  .min()
  .reset_index()
)
dpd['dpd'] = (today - dpd['due_date']).dt.days

#----------------------------------------------------------------------------
''' interest_rate' column stored as strings like '18%' and '21.5%'. 
Convert this column to a usable float (as a decimal, e.g. 0.18).'''

df['interest_rate'] = (
  df['interest_rate']
  .str.replace('%', '', regex=False)
  .astype(float) / 100
)