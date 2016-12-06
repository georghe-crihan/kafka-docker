#!/bin/bash

python3.5 -c 'import setuptools' 2>/dev/null
if [ ! ${?} ]; then
  sudo curl -L -o /root/setuptools-30.0.0.tar.gz https://pypi.python.org/packages/66/6d/dad0d39ce1cfa98ef3634463926e7324e342c956aecb066968e2e3696300/setuptools-30.0.0.tar.gz
  ( cd /root; sudo tar -xvzf setuptools-30.0.0.tar.gz; cd setuptools-30.0.0; sudo /usr/local/bin/python3.5 setup.py install )
fi

yum install zlib-devel openssl-devel

#curl -L -o /root/pip-9.0.1.tar.gz https://pypi.python.org/packages/11/b6/abcb525026a4be042b486df43905d6893fb04f05aac21c32c638e939e447/pip-9.0.1.tar.gz

#curl -L -o /root/requests-2.12.3.tar.gz https://pypi.python.org/packages/d9/03/155b3e67fe35fe5b6f4227a8d9e96a14fda828b18199800d161bcefc1359/requests-2.12.3.tar.gz
#curl -L -o /root/six-1.10.0.tar.gz https://pypi.python.org/packages/b3/b2/238e2590826bfdd113244a40d9d3eb26918bd798fc187e2360a8367068db/six-1.10.0.tar.gz
#curl -L -o /root/websocket-0.2.1.tar.gz https://pypi.python.org/packages/f2/6d/a60d620ea575c885510c574909d2e3ed62129b121fa2df00ca1c81024c87/websocket-0.2.1.tar.gz

#curl -L -o /root/docker-pycreds-0.2.1.tar.gz https://pypi.python.org/packages/95/2e/3c99b8707a397153bc78870eb140c580628d7897276960da25d8a83c4719/docker-pycreds-0.2.1.tar.gz

#curl -L -o /root/websocket-client-0.39.0.tar.gz https://pypi.python.org/packages/c9/61/ca78ba8e931bd148725434298196c6a4d032e29268fd36c478ffed318a2c/websocket_client-0.39.0.tar.gz

pip install --index-url=http://pypi.python.org/simple/ --trusted-host pypi.python.org docker-py 

python -c 'import kafka.errors' 2> /dev/null
if [ ! ${?} ]; then
  sudo curl -L -o /root/kafka-python-1.3.1.tar.gz https://github.com/dpkp/kafka-python/archive/1.3.1.tar.gz
  ( cd /root; sudo tar -xvzf kafka-python-1.3.1.tar.gz; cd kafka-python-1.3.1; sudo python setup.py install )
fi

python -c 'import kazoo.client' 2> /dev/null
if [ ! ${?} ]; then
 sudo curl -L -o /root/kazoo-2.2.1.tar.gz https://pypi.python.org/packages/60/5c/210aa291f9b5be2d0424d512a04dea2f06db816f27289ad1080e267129ec/kazoo-2.2.1.tar.gz
  ( cd /root; sudo tar -xvzf kazoo-2.2.1.tar.gz; cd kazoo-2.2.1; sudo python setup.py install )
fi

if false; then 
  sudo mkdir /root/src
  sudo curl -L -o /root/src/Python-3.5.2.tgz https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
  cd /root/src; tar -xzf Python-3.5.2.tgz
  cd Python-3.5.2
  ./configure
  sudo make altinstall
fi

/usr/bin/env python3.5 -c 'import docker' 2> /dev/null
if [ ${?} ]; then
  sudo curl -L -o /root/docker-py-1.10.6.tar.gz https://pypi.python.org/packages/fa/2d/906afc44a833901fc6fed1a89c228e5c88fbfc6bd2f3d2f0497fdfb9c525/docker-py-1.10.6.tar.gz
  ( cd /root; sudo tar -xvzf docker-py-1.10.6.tar.gz; cd docker-py-1.10.6; sudo /usr/local/bin/python3.5 setup.py install )
fi

