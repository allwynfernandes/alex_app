import logging
import datetime
import streamlit as st
timestamp = datetime.datetime.now().strftime('%b-%d-%H%M%S')
# logging.basicConfig(filename=f'logic_debug_{timestamp}.log', 
#                     level=logging.DEBUG, 
#                     format='%(asctime)s - %(message)s',
#                     datefmt='%d-%b-%y %H:%M:%S')

def gm(base):
    return ("✅ : Valid {}".format(base), "❌ : Invalid {}".format(base))


def check_file_template(df, ttype):
    rule = "Template Structure"
    ttable = []
    if ttype=='cr':
        colList= ['PO#',
                'Amount Paid',
                'Payment Reference',
                'Payment Date',
                'Payment Amount',
                'Payment Type',
                'Discount Percent Limit']
    elif ttype=='ns':
        colList=['Internal ID',
                'Date',
                'Type',
                'Document Number',
                'Name',
                'Amount Remaining',
                'Amount',
                'Memo',
                'PO/Check Number',
                'Status',
                'Customer Internal ID']
    for dfCol, tmCol in zip(df.columns, colList):
        ttable.append(dfCol == tmCol)
    if all(ttable)==True:
        print(f"✅ : Valid {rule}, for {ttype}")
        st.success(f"✅ : Valid {rule}, for {ttype}")
    else:
        print(ttable)
        print(f"❌ : Invalid {rule} for {ttype}")
        print(f"File should contain: {colList} \nbut instead contains {str(list(df.columns))}")
        st.error(f"❌ : Invalid {rule} for {ttype}")
        st.error(f"File should contain: {colList} \nbut instead contains {str(list(df.columns))}")



    return all(ttable)==True


def check_invoice_application_sum(ccc, CONST_payment_amt):
    rule = "Invoice Application Sum"
    invTotal = ccc['Invoice Application'].sum().round(2)
    result = CONST_payment_amt == ccc['Invoice Application'].sum().round(2)
    if result:
        print(f"✅ : Valid {rule}, INV total: {invTotal}, Payment amt: {CONST_payment_amt}")
        st.success(f"✅ : Valid {rule}, INV total: {invTotal}, Payment amt: {CONST_payment_amt}")

    else:
        print(f"❌ : Invalid {rule}, INV total: {invTotal}, Payment amt: {CONST_payment_amt}")
        st.error(f"❌ : Invalid {rule}, INV total: {invTotal}, Payment amt: {CONST_payment_amt}")

    return (rule, result)


def check_table_within_tolerance(crnsINp):
    rule = "Table Within Tolerence"
    result = 'No' in crnsINp['WithinTolerence']
    if result:
        print(f"✅ : Valid {rule}")
        st.success(f"✅ : Valid {rule}")

    else:
        print(f"❌ : Invalid {rule}")
        st.error(f"❌ : Invalid {rule}")

    return (rule, result)

# def check_make_credit


def main():
    pass
if __name__ == "__main__":
    main()