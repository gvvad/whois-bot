#!/bin/bash
echo "Enter server IP for 'server FQDN' field"
openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem
cat private.key cert.pem > key_cert.pem
