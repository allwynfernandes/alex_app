import streamlit as st
import datetime
import logging
from utils import main_logic



timestamp = datetime.datetime.now().strftime('%b-%d-%H%M%S')
logging.basicConfig(filename=f'debug/webapp_debug_{timestamp}.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')



def main():

    st.set_page_config(page_icon="🛠️", page_title="NS Data Processing Utility")


    with st.form("my_form"):
        st.write("🛠️ Alex's Netsuite Data Processing Utility")
        CRPATH =  st.file_uploader("Choose Customer Remitance csv file: ")
        NSPATH =   st.file_uploader("Choose Netsuite csv file: ") 
        # Every form must have a submit button.
        st.info("Press 'Submit' to run the app")
        submitted = st.form_submit_button("Submit")

    if submitted:
        tb_credit, tb_payments = main_logic.run_logic(CRPATH=CRPATH, NSPATH=NSPATH)



        st.success('Done!') 
        st.write("Credit Table")
        st.table(tb_credit)
        st.write("Payment Table")
        st.table(tb_payments)


        st.download_button(
        "Press to Download Credits Table",
        tb_credit.to_csv(index=False).encode('utf-8'),
        "credits.csv",
        "text/csv",
        key='download-csv'
        )

        st.download_button(
        "Press to Download Payments Table",
        tb_payments.to_csv(index=False).encode('utf-8'),
        "payments.csv",
        "text/csv",
        key='download-csv'
        )




if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.debug(e)
        st.exception(e)
