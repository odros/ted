# The decompressor function uses tarfile library is used to decompress the retrieved XML files
# The function retruns a variable that contains the directory path to all the retrieved XML files
def decompress(fname):

    import tarfile
    
    try:
        # check file format
        if fname.endswith("tar.gz"):

            tar = tarfile.open(fname, "r:gz")
            # store folder name
            folder_name  = tar.getnames()[0]
            # store all directory path to the retrieved XML files
            file_names = tar.getnames()[1:]
            tar.extractall('./') 
            tar.close()
            print("File was decompressed successfully.")
            
            # return of variable 'file_names'
            return file_names
    except:
        print("No file for decompression.")
