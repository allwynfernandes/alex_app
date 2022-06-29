import time
import sys
import pandas as pd
df = None

# logic for discound boundry tolerance check:

def withinTolerance(da:float, dl:float=20 ):
    '''
    dl: discount limit ; da: discount actual
    '''
    return (dl-dl*.2 <= da <= dl+dl*.2)#


def creditWork(cr):
    credit_dict = cr.query("`Amount Paid`<0").set_index('PO#').to_dict()['Amount Paid']
    sum(list(credit_dict.values()))


def add_a_b(a, b):

  return a + b


df["col_added"] = df.apply(lambda x: add_a_b(x["col_1"], x["col_2"]), axis = 1)

df['someCol'].apply(add_a_b, args=(5,))

def checkDiscount(df, errMessages):
    if 'No' in df['WitinTolerence'].to_list():
        print(errMessages['D0'])
        time.sleep(5)
        sys.exit(errMessages['D0'])



### === WITH CREDIT | Credit Sheet Calc
def apply_credit(crnsINp, crnsCMp):
    '''
    If all amounts in credit memo sheet are less than maximum of invoice amount then
    apply credit from top to bottom 
    '''
    crnsINcomp = crnsINp.copy(deep=True)
    CONST_MAX_INV = crnsINp.sort_values(by='Amount Paid', ascending=False)['Amount Paid'].max()

    if all(abs(y) < CONST_MAX_INV for y in crnsCMp['Amount'].to_list() ):
        for index, row in crnsCMp[['Internal ID', 'Amount', 'Document Number']].iterrows():
            # adding credit to invoice (meaning deducting the amount since the amt is a negative number)
            crnsINcomp.at[index, 'Credit After Application'] = crnsINcomp.at[index, 'Invoice Application'] + row['Amount'] 
            crnsINcomp.at[index, 'Credit Memo'] = row['Document Number']
            crnsINcomp.at[index, 'Credit Internal'] = row['Internal ID']
            crnsINcomp.at[index, 'Invoice Application'] = abs(row['Amount'])
            crnsINcomp.at[index, 'Credit Amount'] = abs(row['Amount'])
        # Out of for loop
        return crnsINcomp 
    
    else:
        return "Credit is greater than INV maximum"

    return crnsINcomp





### ==== NO CREDIT | Payment Sheet Calc =====
def payment_sheet_processing(crin, nsin):
    pm = (pd.merge(crin, nsin, how='left', left_on='PO#', right_on='po_clean', suffixes=('_cr', '_ns'))
    .get(['Date', 'Customer Internal ID', 'Internal ID', 'PO#', 'Amount Remaining', 'Amount Paid'])
    .assign(**{'Discount Amount':lambda x: abs(x['Amount Paid'] - x['Amount Remaining']),
                'Discount Percent':lambda x:  (x['Discount Amount'] / x['Amount Remaining']).round(2).mul(100), 
                'WithinTolerence':lambda x: x['Discount Percent'].apply(withinTolerance, args=(2,)).map({True:'Yes', False:'No'}) # within tolerance of +- 20%  of 2 %
            }).sort_values(by='Amount Paid', ascending=False)
        
    )
    return pm

def create_payment_sheet_data(CONST_payment_ref, CONST_payment_amt, pm):
    pmc = pm.assign(**{'Payment #':f"ACH {CONST_payment_ref}",
                'Payment Amount': CONST_payment_amt,
                'External ID':f"PAACH {CONST_payment_ref}",
                'Memo':f"ACH {CONST_payment_ref}",
                'Match': lambda x: x['Amount Paid'] + x['Discount Amount']
                    }
            ).get(['Date', 'Customer Internal ID', 'Payment #', 'Internal ID', 'Payment Amount', 'Amount Paid', 'Discount Amount', 'External ID', 'Memo', 'Match'])

    return pmc
### === WITH CREDIT | Payment Sheet Calc ===



### ==== Payment Sheet Validation ===
def validate_payment_process(pm, pmc, CONST_payment_amt):
    CONST_SUM_AMOUNT_REMAINING =  pm['Amount Remaining'].sum().round(2)
    CONST_SUM_INVOICE_APPLICATION = pmc['Amount Paid'].sum() .round(2)
    CONST_SUM_DISCOUNT_AMOUNT = pmc['Discount Amount'].sum().round(2)
    CONST_SUM_MATCH_AMOUNT = pmc['Match'].sum().round(2)
    
    
    
    print(f"{CONST_SUM_AMOUNT_REMAINING=}",'\n'
          f"{CONST_SUM_INVOICE_APPLICATION=}",'\n' 
          f"{CONST_SUM_DISCOUNT_AMOUNT=}", '\n'
          f"{CONST_SUM_MATCH_AMOUNT=}", '\n'
          f"{CONST_payment_amt=}", 
          
         )    

    assert int(CONST_SUM_INVOICE_APPLICATION.round()) == int(CONST_payment_amt),  'ERROR: Sum of Invoice Application does not equal Payment amount, Exiting program...'
    assert (CONST_SUM_AMOUNT_REMAINING - CONST_SUM_INVOICE_APPLICATION).round(2) == CONST_SUM_DISCOUNT_AMOUNT , 'ERROR: Discount sum not equal to Amount Remaining - Amount Paid (ie. Invoice Application), Exiting Application'
    assert ( CONST_SUM_MATCH_AMOUNT.round() == CONST_SUM_AMOUNT_REMAINING.round() ), 'ERROR: Sum of Invoice Application + Discount does not equal sum Amount Remaning, Exiting program...'
    assert (CONST_SUM_INVOICE_APPLICATION + CONST_SUM_DISCOUNT_AMOUNT == CONST_SUM_MATCH_AMOUNT), 'ERROR: Match Amount'