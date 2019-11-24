# bitcoin-price-recorder
Automated recording of the minute-to-minute price of Bitcoin to a local database

Program creates a database, connects to Robinhood's web API and a pop3 server (required for Robinhood 2-factor authentication), and retreives and stores the minute-to-minute price of Bitcoin in the created database.

Program requires a pop3 email account accessable by external services, a Robinhood account, and sqlite3.

Program also automatically handles the required refreshing of oauth2 tokens with Robinhood and, without external influences (and limited by disk space), can indefinitely record the price of Bitcoin each and every minute.

Inputs are the following:
- server address of pop3 server
- username for pop3 server
- password for pop3 server
- username for robinhood
- password for robinhood
- file path of database
