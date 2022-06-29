import logging
import datetime
import pandas as pd
from validations import logic
timestamp = datetime.datetime.now().strftime('%b-%d-%H%M%S')
logging.basicConfig(filename=f'app_debug_{timestamp}.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')


f = {0:'data/noCM_cinc.csv', # there is no credit 
    1:'data/noCM_cinn.csv', # there is no credit
    2:'data/CM_cinc.csv',
    3:'data/CM_cinn.csv',
    4:'data/noCM_B_cinc.csv',
    5:'data/noCM_B_cinn.csv'
    }


def withinTolerance(da:float, dl:float=2 ):
    '''
    dl: discount limit ; da: discount actual
    # Alex: On DL50,  Lowerbound::48, Upper: 52
    
    '''
    tolerance= 0.04
#     print(dl-dl*tolerance)
#     print(dl+dl*tolerance)
    return (dl-dl*tolerance <= da <= dl+dl*tolerance)#



# |==> Get empty df 
#====================
def get_empty_df():
    return pd.DataFrame()


# |==> Get df cleaned
#====================
def get_clean(df):
    for col in df.columns:
        df[col] = df[col].astype('string').str.replace(",", "")
    return df


# |==> Get df with correct dtypes
#====================
def force_convert_dtypes(df, tableType):
    if tableType=='cr':
        df = df.astype({'PO#':'string', 'Amount Paid':'float', 'Payment Reference':'string', 'Payment Date':'string',
       'Payment Amount':'float', 'Payment Type':'string', 'Discount Percent Limit':'float'})
    if tableType=='ns':
        df = df.astype({'Internal ID':'string', 'Date':'string', 'Type':'string', 'Document Number':'string', 'Name':'string',
       'Amount Remaining':'float', 'Amount':'float', 'Memo':'string', 'PO/Check Number':'string', 'Status':'string',
       'Customer Internal ID':'string'})
    if tableType=='py':
        df = df.astype({"Date":"string","Customer ID":"string","Payment #":"string","Invoice Internal":"string",
        "Payment Amount":"float","Invoice Application":"float","Discount":"float","External ID":"string","Memo":"string"})

    return df


# |==> Get the data and create constants to be used later
#===========================================
# CRPATH = f[2]
# NSPATH = f[3]


def getData(CRPATH, NSPATH):

    assert (CRPATH and NSPATH), "Incorrect path provided for CR or NS file"
    if (CRPATH and NSPATH):
        crcsv = get_clean(pd.read_csv(CRPATH)).fillna("0")
        nscsv = get_clean(pd.read_csv(NSPATH)).fillna("0")

        crcsv = force_convert_dtypes(crcsv, 'cr')
        nscsv = force_convert_dtypes(nscsv, 'ns')
    else:
        print("Incorrect path provided for CR or NS file")
    assert logic.check_file_template(crcsv, 'cr'), "Invalid CR file"
    assert logic.check_file_template(nscsv, 'ns'), "Invalid NS file"


    cr = crcsv[['PO#', 'Amount Paid']]
    cr['PO#'] = cr['PO#'].str.extract(r'(PO.{12})')


    crin = cr[cr['Amount Paid']>0] # CR records with Invoice
    crcm = cr[cr['Amount Paid']<0]  # CR records with Credit

    ns = nscsv.copy()
    ns['po_clean'] = ns['PO/Check Number'].str.extract(r'(PO.{12})')

    nsin = ns.query("Type=='Invoice'") # NS records with 
    nscm = ns.query("Type=='Credit Memo'") # NS records with Credit Memo

    CONST_payment_ref = str(crcsv.loc[0].get('Payment Reference'))
    CONST_payment_dt = str(crcsv.loc[0].get('Payment Date'))
    CONST_payment_amt = float(crcsv.loc[0].get('Payment Amount'))
    CONST_payment_typ = str(crcsv.loc[0].get('Payment Type'))
    CONST_payment_disc_thresh = float(crcsv.loc[0].get('Discount Percent Limit'))

    CONST_count_of_credits_original  = cr[cr['Amount Paid']<0]['PO#'].count()
    IS_credit_sheet_needed = CONST_count_of_credits_original > 0

    return crin, crcm, nsin, nscm, CONST_payment_ref, CONST_payment_amt, CONST_count_of_credits_original, CONST_payment_dt, CONST_payment_typ

    

# |==> Create filtered processing table for Credit memos and Invoices
#===========================================

def get_processed(crin, nsin, crcm, nscm, CONST_payment_ref, CONST_payment_amt, CONST_payment_typ):
    crnsINp = (pd.merge(crin, nsin, how='left', left_on='PO#', right_on='po_clean', suffixes=('_cr', '_ns'))
    .get(['Date', 'Customer Internal ID', 'Internal ID', 'PO#', 'Amount Remaining', 'Amount Paid', 'Document Number'])
    .assign(**{'Discount Amount':lambda x: abs(x['Amount Paid'] - x['Amount Remaining']),
                'Discount Percent':lambda x:  (x['Discount Amount'] / x['Amount Remaining']).round(2).mul(100), 
                'WithinTolerence':lambda x: x['Discount Percent'].apply(withinTolerance, args=(2,)).map({True:'Yes', False:'No'}), # within tolerance of +- 20%  of 2 %
                'Invoice Application': lambda x: x['Amount Paid'],
                'Payment #': str(CONST_payment_typ)+str(CONST_payment_ref),
                'Payment Amount': CONST_payment_amt,
                'External ID': f"PA{CONST_payment_typ}{CONST_payment_ref}",
                'Memo':f"{CONST_payment_typ} {CONST_payment_ref}"
            }).sort_values(by='Amount Paid', ascending=False).reset_index(drop=True)
        
    )


    crnsCMp = (pd.merge(crcm, nscm, how='left', left_on='PO#', right_on='po_clean', suffixes=('_cr', '_ns'))
    .get(['Date', 'Customer Internal ID', 'Internal ID', 'PO#', 'Amount Remaining', 'Amount Paid', 'Amount', 'Document Number'])
    .assign(**{  'External ID' : f'CAACH{CONST_payment_ref}',
                'absAmount' : lambda x: abs(x['Amount Paid']),
    #               'Discount Amount':lambda x: abs(x['Amount Paid'] - x['Amount Remaining']),
    #             'Discount Percent':lambda x:  (x['Discount Amount'] / x['Amount Remaining']).round(2).mul(100), 
    #             'WithinTolerence':lambda x: x['Discount Percent'].apply(withinTolerance, args=(2,)).map({True:'Yes', False:'No'}) # within tolerance of +- 20%  of 2 %
            })
            .sort_values(by='Amount Paid', ascending=True).reset_index(drop=True)
        
    )

    
    return crnsINp, crnsCMp





# |==> Get child table with credits applied
#===========================================
def apply_credit(crnsINp, crnsCMp):
    '''
    If all amounts in credit memo sheet are less than maximum of invoice amount then
    apply credit from top to bottom 
    '''
    crnsINcomp = crnsINp.copy(deep=True)
    CONST_MAX_INV = crnsINp.sort_values(by='Amount Paid', ascending=False)['Amount Paid'].max()

    if all(abs(y) <= CONST_MAX_INV for y in crnsCMp['Amount'].to_list() ):
        for index, row in crnsCMp[['Internal ID', 'Amount', 'Document Number']].iterrows():
            # adding credit to invoice (meaning deducting the amount since the amt is a negative number)
            crnsINcomp.at[index, 'Invoice Application'] = crnsINcomp.at[index, 'Invoice Application'] + row['Amount'] 
            crnsINcomp.at[index, 'Credit Memo'] = row['Document Number']
            crnsINcomp.at[index, 'Credit Internal'] = row['Internal ID']
#             crnsINcomp.at[index, 'Invoice Application'] = abs(row['Amount'])
            crnsINcomp.at[index, 'Credit Amount'] = abs(row['Amount'])
        # Out of for loop
        return crnsINcomp 
    
    else:
        print("One creidt memo greater than INV max OR No CR ref found in INV")
        return pd.DataFrame() # "Credit is greater than single INV maximum"


def process_discount_again(ccc, CONST_payment_ref, CONST_payment_amt):
    pm = (ccc
    [['Date', 'Customer Internal ID', 'Internal ID', 'PO#', 'Amount Remaining', 'Amount Paid', 'Invoice Application', 'Payment #', 'Payment Amount', 'External ID', 'Memo']]
    .assign(**{'Discount Amount':lambda x: abs(x['Amount Paid'] - x['Amount Remaining']),
                'Discount Percent':lambda x:  (x['Discount Amount'] / x['Amount Remaining']).round(2).mul(100), 
                'WithinTolerence':lambda x: x['Discount Percent'].apply(withinTolerance, args=(2,)).map({True:'Yes', False:'No'}), # within tolerance of +- 20%  of 2 %

            }).sort_values(by='Amount Paid', ascending=False)
        
    )
    return pm



# |==> Get export redy tables for Credit, Payment
#=================================================
def prep_cosmetic_credit_sheet(ccc, CONST_payment_ref):
    df = ccc[['Credit Memo', 'Credit Internal', 'Document Number', 'Internal ID', 'Invoice Application', 'Credit Amount']].assign(**{'External ID':f'CAACH{CONST_payment_ref}'}).dropna()
    df = df.rename(columns={'Document Number':'Invoice Number',
                            'Internal ID':'Applied Invoice'
                           })   # not rounding since int .round(3)
    df = df.astype('string')
    return df

def prep_cosmetic_payment_sheet(df, dateinput):
    df = df.rename(columns={'Customer Internal ID':'Customer ID',
                            'Internal ID': 'Invoice Internal', 
                            'Discount Amount': 'Discount',
                      })
    df = df[['Date', 'Customer ID', 'Payment #', 'Invoice Internal', 'Payment Amount', 'Invoice Application', 'Discount', 'External ID', 'Memo']]
    df['Date'] = dateinput #df.Date.dt.strftime('%m/%d/%Y')
    return df


def save_csv(fileName, data):
    data.to_csv(f"export/{fileName}", index=False) 












def main():
    pass
if __name__ == "__main__":
    main()