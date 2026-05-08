FROM python:3.10 AS pyodbc

WORKDIR /app

# OpenSSL config
COPY openssl.cnf /etc/ssl/openssl.cnf

# pyodbc
RUN apt-get update
RUN apt-get install g++ unixodbc-dev -y
RUN pip install --user pyodbc
RUN pip install --user openpyxl

# mssql
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 \
    && echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> /etc/bash.bashrc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (cache optimization)
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose FastAPI port
EXPOSE 5008

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5008"]