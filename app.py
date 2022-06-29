import os
import datetime
import logging
from utils import helpers
from validations import logic

timestamp = datetime.datetime.now().strftime('%b-%d-%H%M%S')
logging.basicConfig(filename=f'debug/app_debug_{timestamp}.log', 
                    level=logging.DEBUG, 
                    format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

def mainApp():

    CRPATH =  os.path.abspath( input("Drop Customer Remitance csv file: ") ) # "c:/Users/admin/lab/alex/etl_drones/v3/data/CM_cinc.csv" #
    NSPATH =  os.path.abspath( input("Drop Netsuite csv file: ") )#  "c:/Users/admin/lab/alex/etl_drones/v3/data/CM_cinn.csv" # 
    DATEINPUT = input(str("Input Required date in mm/dd/YYYY format: "))

    crin, crcm, nsin, nscm, CONST_payment_ref, \
    CONST_payment_amt, CONST_count_of_credits_original, \
    CONST_payment_dt, CONST_payment_typ = helpers.getData(CRPATH, NSPATH) 
    # logging.debug(f"{CONST_payment_amt=} | {CONST_payment_ref=} | {CONST_count_of_credits_original=}")

    crnsINp, crnsCMp = helpers.get_processed(crin, nsin, crcm, nscm, CONST_payment_ref, CONST_payment_amt)




    if CONST_count_of_credits_original > 0:
        print("✅ : Credits found")
        print("✅ : processing data...")
        ccc = helpers.apply_credit(crnsINp, crnsCMp)
        credits_data = helpers.prep_cosmetic_credit_sheet(ccc, CONST_payment_ref)
        helpers.save_csv('credits.csv', credits_data)
        ccc = helpers.process_discount_again(ccc, CONST_payment_ref, CONST_payment_amt)

        if logic.check_invoice_application_sum(ccc, CONST_payment_amt)[1]:
            payments_data = helpers.prep_cosmetic_payment_sheet(ccc, CONST_payment_dt)
            helpers.save_csv('payments.csv', payments_data)
            logging.debug("Credits found, Data Saved Successfully")

    else:
        print("No credits found")
        print("processing data...")
        if logic.check_invoice_application_sum(crnsINp, CONST_payment_amt):
            payments_data = helpers.prep_cosmetic_payment_sheet(crnsINp, CONST_payment_dt)
            helpers.save_csv('payments.csv', payments_data)
            logging.debug("No credits found, Data Saved Successfully")

    # ccc = helpers.process_discount_again(crnsINp, CONST_payment_ref, CONST_payment_amt)



if __name__ == '__main__':
    try:
        mainApp()
    except Exception as e:
        logging.debug(e)
