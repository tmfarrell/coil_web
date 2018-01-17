
## coil_web

This is the repository for the web version of [COIL](https://www.broad.io/coil), a method for estimating malarial complexity of infection 
from bi-allelic single nucleotide polymorphism (SNP) barcode data. Read more about COIL in the [published manuscript](https://www.ncbi.nlm.nih.gov/pubmed/25599890).

For the stand-alone/ command-line version, see this [repository](https://github.com/kgalinsky/COIL). 

The frontend of this tool was adapted from this [flask-boilerplate](https://github.com/realpython/flask-boilerplate) repository. It uses a very basic/
barbones setup of Flask, Bootstrap and pure JS for dynamic UI.

### setup 

To setup/ deploy this app on fresh install of Debian/ Ubuntu, install the following system requirements (if you don't have them already): 

```bash
# get Apache
sudo apt-get install apache2
sudo apt-get install apache2-dev

# get python and header files
sudo apt-get install python-2.7
sudo apt-get install libpython-dev
```

To install the python dependencies (again, if you don't have them already), execute: 

```bash
# get pip
wget https://bootstrap.pypa.io/get-pip.py

# install mod_wsgi
sudo pip install mod_wsgi
sudo pip install mod_wsgi-httpd
```

If you'd like to build a `virtualenv` (a wiser option) rather than system installations, do the following: 

```bash
# get virtualenv, and open new env
pip install virtualenv
virualenv coil_web_env
source coil_web_env/bin/activate

# then mod_wsgi
sudo pip install mod_wsgi
sudo pip install mod_wsgi-httpd
```

Then install and deploy `coil_web` to port 80: 

```bash
# get coil_web 
cd /var/www/
git clone http://github.com/tmfarrell/coil_web.git

# install dependencies
cd coil_web
sudo pip install -r requirements.txt
cd ..

# setup server configurations 
sudo mod_wsgi-express setup-server \
     /var/www/coil_web/coil_web.wsgi \
     --port 80 \
     --user www-data --group www-data \
     --server-root=/var/www/coil_web/ \
     --recorder-directory /var/www/coil_web/ \
     --document-root /var/www/coil_web/coil_web/

# deploy on port 80 
sudo ./apachectl start
```    

For more detailed instructions, see these tutorials: 
- [PyPI: mod_wsgi](https://pypi.python.org/pypi/mod_wsgi)
- [Running Flask on macOS with mod_wsgi/wsgi-express](https://davidhamann.de/2017/08/05/running-flask-with-wsgi-on-macos/)
- [Introducing mod_wsgi-express](http://blog.dscpl.com.au/2015/04/introducing-modwsgi-express.html)
- [mod_wsgi documentation](http://modwsgi.readthedocs.io/en/develop/getting-started.html)
