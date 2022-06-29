import streamlit as st
import datetime
import logging
from utils import helpers
from validations import logic

timestamp = datetime.datetime.now().strftime('%b-%d-%H%M%S')
logging.basicConfig(filename=f'debug/app_debug_{timestamp}.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')










def main():
    
    def callback():
        st.balloons()


    CRPATH =  st.file_uploader("Choose Customer Remitance csv file: ")
    NSPATH =   st.file_uploader("Choose Netsuite csv file: ") 
    DATEINPUT = st.date_input("Input Required date in mm/dd/YYYY format:", datetime.datetime.now())

    crin, crcm, nsin, nscm, CONST_payment_ref, CONST_payment_amt, CONST_count_of_credits_original = helpers.getData(CRPATH, NSPATH)
    # logging.debug(f"{CONST_payment_amt=} | {CONST_payment_ref=} | {CONST_count_of_credits_original=}")

    crnsINp, crnsCMp = helpers.get_processed(crin, nsin, crcm, nscm, CONST_payment_ref, CONST_payment_amt)




    if CONST_count_of_credits_original > 0:
        print("✅ : Credits found")
        print("✅ : processing data...")
        ccc = helpers.apply_credit(crnsINp, crnsCMp)
        credits_data = helpers.prep_cosmetic_credit_sheet(ccc, CONST_payment_ref)

        # Download CREDIT CSV
        # helpers.save_csv('credits.csv', credits_data)




        ccc = helpers.process_discount_again(ccc, CONST_payment_ref, CONST_payment_amt)

        if logic.check_invoice_application_sum(ccc, CONST_payment_amt)[1]:
            payments_data = helpers.prep_cosmetic_payment_sheet(ccc, DATEINPUT)
            helpers.save_csv('payments.csv', payments_data)
            logging.debug("Credits found, Data Saved Successfully")

    else:
        print("No credits found")
        print("processing data...")
        if logic.check_invoice_application_sum(crnsINp, CONST_payment_amt):
            payments_data = helpers.prep_cosmetic_payment_sheet(crnsINp, DATEINPUT)
            helpers.save_csv('payments.csv', payments_data)
            logging.debug("No credits found, Data Saved Successfully")

    # ccc = helpers.process_discount_again(crnsINp, CONST_payment_ref, CONST_payment_amt)


    if CONST_count_of_credits_original > 0:
        st.download_button(
            label="Download data as CSV",
            data=credits_data,
            file_name='credits.csv',
            mime='text/csv',
            on_click=callback,
            key='callback'
        )

    st.download_button(
        label="Download data as CSV",
        data=payments_data,
        file_name='payments.csv',
        mime='text/csv',
        on_click=callback,
        key='callback'
    )





# st.set_page_config(page_icon="✂️", page_title="Netsuite Data Processing Utility")

# st.image(
#     "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/285/scissors_2702-fe0f.png",
#     width=100,
# )

# st.title("Netsuite Data Processing Utility")
# c29, c30, c31 = st.columns([1, 6, 1])



# Study from here : https://github.com/streamlit/example-app-csv-wrangler/blob/f527846a39385fb234d1445ae34aa03bd9b840bd/app.py#L64







# if __name__ == '__main__':
#     try:
#         main()
#     except Exception as e:
#         logging.debug(e)
