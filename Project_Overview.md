# Project Objectives
# Overview: provide a user either a gui or terminal code with switch options to select a parent folder for the application to recurse through tree to identify folders containing files for processing (primarily PDFs, but can be other file formats).

1. Input methods: Gui and terminal options for the user select a parent folder for processing
2. Data ideentication: provide the user with a list of folders for processing and seek their confirmation before processing. The folder will typically contain files related to an account or policy number or be listed by client name. Assign a GUID to each folder for tracking purposes.   
3. File processing: process identified files (primarily PDFs) within the selected folders. 
    - sample folder tree location: "C:\_sample\tree_test"
4. Json output, that will have eventually be converted to csv
5. Detailed tracking, reporting, exception handling to ID exceptions while continuing to process other files.
6. provide detailed Readme.MD guidance to users