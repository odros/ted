## Retrieve XML for given date

def retrieve(date):

   # Cast date to string
   date = str(date)
   
   ## Determine if requested date is within valid range
   
   # Import required library
   from datetime import datetime
   
   # Define range of valid dates
   start = datetime.strptime("20110101", "%Y%m%d")
   end = datetime.now()
   
   # Parse date into 'datetime' format
   parsed_date = datetime.strptime(date, "%Y%m%d")
   
   # Break if date is out of range
   if not start <= parsed_date <= end:
       print("Requested date is out of range.")
   else:     
      try:
         # Parse year and month
         year = date[0:4]
         month = date[4:6]
           
         # Connect to server
         from ftplib import FTP
         ftp = FTP("ted.europa.eu")
         ftp.login("guest", "guest")
      
         # Navigate to directory containing passed date
         ftp.cwd("daily-packages/" + year + "/" + month)
         
         # Retrieve directory contents for given year/month combination  
         file_names = ftp.nlst()
         
         # Determine if a file for the given date exists in directory
         if any(date in s for s in file_names):
            
            # Determine filename using a list comprehension
            file_name = [file_name for file_name in file_names if file_name.startswith(date)][0]
            
            # Retrieve file
            ftp.retrbinary("RETR " + file_name, open(file_name, 'wb').write)
            # Possible improvement for next iteration: add some feedback on status of download.
            
            # Alert user of successful download
            print("File was downloaded successfully.")
            
            
            # Close connection
            ftp.quit()
            return file_name
         
         else:
            print("No file exists for the requested date.")
            ftp.quit()
      
      # Catch file transfer issues
      except:
         print("Something went wrong with the file transfer.")
      
