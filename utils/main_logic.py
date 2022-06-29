import datetime
import logging
from . import helpers
from validations import logic
import streamlit as st

def run_logic(CRPATH, NSPATH):

    crin, crcm, nsin, nscm, CONST_payment_ref, \
    CONST_payment_amt, CONST_count_of_credits_original, \
    CONST_payment_dt, CONST_payment_typ = helpers.getData(CRPATH, NSPATH) 
    # logging.debug(f"{CONST_payment_amt=} | {CONST_payment_ref=} | {CONST_count_of_credits_original=}")

    crnsINp, crnsCMp = helpers.get_processed(crin, nsin, crcm, nscm, CONST_payment_ref, CONST_payment_amt, CONST_payment_typ)




    if CONST_count_of_credits_original > 0:
        print("✅ : Credits found")
        print("✅ : processing data...")
        st.success("✅ : Credits found")
        st.success("✅ : processing data...")

        ccc = helpers.apply_credit(crnsINp, crnsCMp)
        credits_data = helpers.prep_cosmetic_credit_sheet(ccc, CONST_payment_ref)

        # Download CREDIT CSV
        # helpers.save_csv('credits.csv', credits_data)




        ccc = helpers.process_discount_again(ccc, CONST_payment_ref, CONST_payment_amt)

        if logic.check_invoice_application_sum(ccc, CONST_payment_amt)[1]:
            payments_data = helpers.prep_cosmetic_payment_sheet(ccc, CONST_payment_dt)
            # helpers.save_csv('payments.csv', payments_data)
            logging.debug("Credits found, Data Saved Successfully")

    else:
        print("No credits found")
        print("processing data...")
        st.info("No credits found")
        st.info("processing data...")

        if logic.check_invoice_application_sum(crnsINp, CONST_payment_amt):
            payments_data = helpers.prep_cosmetic_payment_sheet(crnsINp, CONST_payment_dt)
            # helpers.save_csv('payments.csv', payments_data)
            logging.debug("No credits found, Data Saved Successfully")
    
    payments_data = helpers.force_convert_dtypes(payments_data, 'py')
    if (CONST_count_of_credits_original > 0):
        return credits_data, payments_data
    else:
        return helpers.pd.DataFrame(), payments_data




def main():
    pass
if __name__ == "__main__":
    main()