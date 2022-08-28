""" A host had its SSL Cert expired. In this snipped we try to download a binary file and if it fails because of a SSL Cert Verification error - re-try without cert checks.
"""
import ssl
import urllib.request, urllib.parse, urllib.error
import logging

logging.basicConfig(
    filename=STATUS_LOG,  # set to whatever appropriate path
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

""" Download a binary file and return full path to its local copy.
"""


def download(base_url, file, dest_dir, ssl_checks=True):
    res = None
    src_url = base_url + str(file)
    dest_fpname = os.path.join(dest_dir, file)
    ctx = ssl.create_default_context()
    if ssl_checks == False:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    try:
        # urllib.request.urlopen takes SSL context which we use to disable SSL check
        with urllib.request.urlopen(src_url, context=ctx) as web_file:
            # writing to a local file just for example
            with open(dest_fpname, "wb") as local_file:
                local_file.write(web_file.read())
        res = dest_fpname

    except urllib.error.URLError as e:
        # We are hunting for ssl.SSLCertVerificationError, it is invisible to "except"
        # It actually comes as an argument of urllib.error.URLError
        logging.debug(f"Got subexception: {type(e.args[0])}")
        if (type(e.args[0]) == ssl.SSLCertVerificationError) and (ssl_checks == True):
            logging.warning(
                f"urlopen failed for {src_url}: {repr(e)}. Trying ssl_checks=False"
            )
            res = download(base_url, file, dest_dir, ssl_checks=False)
        else:
            logging.error(f"Failed to download with URLError for {src_url}: {repr(e)}")
    except IOError as e:
        logging.error(f"Failed to download {src_url}: {repr(e)}")
    return res

 
