
# Overall Tasks
- Write Functions to check for errors at keypoints before and after processing
- [ ] Create function and logic to split a credit memo that is greater than maximum single invoice
- [x] Create validators
- [x] Create no credit workflow

# Create Functions
- [x] Force column dtype conversion

# 02 Jun 
- [ ] Force clean all non-numericals (start and end only) for "PO#" field from both df 
    - [ ] correct PO pattern = 4 Digit string with no trailling alphabets
    - [ ] Start trimming from right upto 8 digits
    - [ ] Text input to string to pandas df input form (for CR file)