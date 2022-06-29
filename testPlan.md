Tests:
- cr file with no credit entry -> print no credit entry, continue
- ns file with no matching credit entry -> print no credit entry in file , exit
- cr file has small `amount paid`vs ns file `amount remain` -> discount err , exit 
- cr cm amount != ns cm amount of same po -> Credit memo mismatch err , exit
