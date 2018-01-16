
## coil_web

This is the repository for the web version of [COIL](https://www.broad.io/coil), a method for estimating malarial complexity of infection 
from bi-allelic single nucleotide polymorphism (SNP) barcode data. Read more about COIL in the [published manuscript](https://www.ncbi.nlm.nih.gov/pubmed/25599890).

For the stand-alone/ command-line version, see this [repository](https://github.com/kgalinsky/COIL). 

The frontend of this tool was adapted from this [flask-boilerplate](https://github.com/realpython/flask-boilerplate) repository. It uses a very basic/
barbones setup of Flask, Bootstrap and pure JS for dynamic UI.

### setup 

To setup/ deploy this app on Debian/ Ubuntu, execute: 

```bash
# get Apache
sudo apt-get install apache2
sudo apt-get install apache2-dev

# get python header files
sudo apt-get install libpython-dev

# get pip
wget https://bootstrap.pypa.io/get-pip.py

# install mod_wsgi
sudo pip install mod_wsgi
sudo pip install mod_wsgi-httpd

# get coil_web 
cd /var/www/
git clone http://github.com/tmfarrell/coil_web.git

# install dependencies
cd coil_web
sudo pip install -r requirements.txt
cd ..

# setup server configurations 
sudo mod_wsgi-express setup-server /var/www/coil_web/coil_web.wsgi --port 80 \
  --user www-data --group www-data --server-root=/var/www/coil_web/ \
  --recorder-directory /var/www/coil_web/ --document-root /var/www/coil_web/coil_web/

# deploy on port 80 
sudo ./apachectl start
```    