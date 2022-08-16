# This function extracts information of interest from XML files and stores them in a CSV file.
# The function is based on the lxml library combines with absolute xpath expression. 
# Absolute paths are requiring more code compared to relative path expression.
# However, an absolute path is faster in identifying elements than a relative path
# Considering that the function has to scrape a few 1000 XML files, the performance gain is significant.
# The extractor function ist test for XML file back to 06.07.2018 (20180705)

# The function needs a variable that contains the directory path to XML files.
# Second, a file path for the output file is required.
def extract(file_names,destination):

    from lxml import etree
    
    try:

        # The 'no_header' variable is set to True outside the following iteration. 
        # (Required for the writing in the end)
        no_header = True

        # The scarper is iterating over all XML files of the given variable 'file_names'
        for xml in file_names:

            # The 'root' variable stores the root element for the tree of the XML file
            root = etree.parse(xml).getroot()

            # The 'NMSP' variable is created with the namespace function | see function namespace()
            # The variable contains namespaces for tagname notations within xpath expressions.
            # The use of tagname notations for long namespaces offers shorter code.
            NMSP = namespace(root)

            # IF stantment checks if the xml is a Contract award notice | see function doc_typ()
            # Only contract award notices of interest. If the XML file contains a different notice, the iteration is done
            if doc_typ(root,NMSP):

                # The 'FORM_SECTION' is a sub tree of fhe XML root. The sub tree is stored in the 'form_sec' variable
                try:
                    form_sec = root.xpath('ted:FORM_SECTION/ted:F03_2014[@CATEGORY = "ORIGINAL"]', namespaces=NMSP)[0]
                
                # In case the sub tree does not exsist, the continue statement passes the rest so that the next iteration can start
                except: continue


                # The 'ADDRESS_CONTRACTING_BODY' is a sub tree from the previously created 'form_sec' tree. Is is stores in 'body_sec'
                body_sec = form_sec.xpath('ted:CONTRACTING_BODY/ted:ADDRESS_CONTRACTING_BODY', namespaces=NMSP)[0]
                
                # extraction of the contractee
                contractee = body_sec.findtext('ted:OFFICIALNAME', namespaces=NMSP)
                
                # extraction of the NUTS code (Nomenclature of Territorial Units for Statistics - refering to a geographic region)
                nuts = body_sec.xpath('n20xx:NUTS/@CODE', namespaces=NMSP)[0] # NUTS
                
                # extraction of the country (of the contractee)
                country = body_sec.xpath('ted:COUNTRY/@VALUE', namespaces=NMSP)[0]
                
                # extraction of the document ID 
                id = root.get('DOC_ID', default=None) 

                # extraction of the CPV Code (Common Procurement Vocabulary - subject matter of public contracts)
                cpv = form_sec.xpath('ted:OBJECT_CONTRACT/ted:CPV_MAIN/ted:CPV_CODE/@CODE', namespaces=NMSP)[0] 
                
                # extraction of the type (SERVICES; SUPPLIES; WORKS)
                type = form_sec.xpath('ted:OBJECT_CONTRACT/ted:TYPE_CONTRACT/@CTYPE', namespaces=NMSP)[0]


                # Since one contract award notice can contain many lots (items / subcontracts ) there are further sub section for each lot
                # To access and scrape information of each lot another iteration over each sub section is required
                # The number of sub section is varying. The findall() function can catch all of them.
                for item in form_sec.findall('ted:AWARD_CONTRACT', namespaces=NMSP): 
                    
                    # Often infomation like the contract value is missing. To prevent ectracting incomplete data,
                    # the try: / except: combined with 'continue' will skip to the next interation in such a case.
                    try:
                        # value_path is a function which stands for the xpath that leads to contract value 
                        value_path = etree.XPath("ted:AWARDED_CONTRACT/ted:VALUES/ted:VAL_TOTAL", namespaces=NMSP)
                        
                        # extraction of the contract value
                        value = value_path(item)[0].text
                        
                        # extraction of the currency of the value
                        currency = value_path(item)[0].attrib['CURRENCY']
                        
                        # extraction of the contractor
                        contractor = item.findtext('ted:AWARDED_CONTRACT/ted:CONTRACTORS/ted:CONTRACTOR/ted:ADDRESS_CONTRACTOR/ted:OFFICIALNAME', namespaces=NMSP) # extract contractor

                        # After extraction the information, the data is written to a CSV file
                        try:
                            # CSV file will be created. Each set of data for one contract (lot) will be appended as one row
                            with open(destination, 'a') as file:
                                
                                # A header will be written to the top of the file, once. The while loop will stay false for all follwing interations
                                while no_header:
                                    file.write(f'{"ID"},{"Contractee"},{"Contractor"},{"CPV"},{"Type"},{"Country"},{"Nuts"},{"Value"},{"Currency"}\n')
                                    no_header = False
                                
                                # All the extracted information will be written as one row to the CSV File
                                # Commas are removed fom variable to not corrupt the CSV format
                                file.write(f'{id},{contractee.replace(",", "")},{contractor.replace(",", "")},{cpv},{type},{country},{nuts},{float(value)},{currency}\n') # store everything in a CSV File

                        except:
                            pass

                    except: continue
    except:
        pass





################### namespace function

# Since namespaces vary over month / years between the XML files, fixed namespaces would offer very limited functionality 
# The function looks up the the namespaces of the root of XML file and returns a dictionary that ready to use in
# a "{namespace}tagname" notation for XPath operations inside the scraper function. 

# the function needs the root of an XML file 
def namespace(root): 

    # the "none" vriable takes the default namespace
    none = root.nsmap[None]
    
    # the "version" variable will store the key for the third namesspace of the XML file.
    # the third namesspace is of relevance, because it is required to access the standard geocode (NUTS) 
    # the key will likely be n2016 or n2020
    version = list(root.nsmap)[3]
    
    # the "n20xx" variable will store the third namesspace of the XML file.
    n20xx = root.nsmap[version]

    # returns a dictionary with namespace ready for a tagname notation
    return {"ted": none, "n20xx": n20xx}





################### doc_typ function

# doc_typ function scrapes the document type code. 
# Only documents with code 7 ( 7 = Contract award notice) are if interest. 
# The function returns True if the code is 7 (meaning the XML file is Contract award notice)

# the function needs the root of an XML file and an namespace object
def doc_typ(root,NMSP):
    from lxml import etree

    # Document_type is a function which stands for the xpath that leads to the document type code
    document_type = etree.XPath('ted:CODED_DATA_SECTION/ted:CODIF_DATA/ted:TD_DOCUMENT_TYPE/@CODE', namespaces=NMSP)
    
    # The Document_type is applied on the root and compared with 7 (Contract award notice)
    return document_type(root) == ['7']


