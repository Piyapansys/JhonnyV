#!/bin/bash
# Adding Microsoft's package repository
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-prod.list
apt-get update

# Install the ODBC driver
apt-get install -y msodbcsql18
