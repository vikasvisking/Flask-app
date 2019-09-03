Upload .au domains names CSV file to database

### Requirements:

* python 3+
* mysql-connector

```
usage: domains-csv.py [-h] [-v] [--database DATABASE] [--file FILE]
                      [--url URL]

Upload CSV to MySQL

optional arguments:
  -h, --help           show this help message and exit
  -v                   enable verbosity
  --database DATABASE  database to use
  --file FILE          local file to use
  --url URL            url to download file from
```
### Full download of domains https://ausdomainledger.net/au-domains-latest.csv.gz
### For testing use the smaller sample file in this repository


Hi Priyankush,

I would like you to do the following:

1. Use the domains-csv.py code to import the data into a MySQL database. (Please intergrate this into the test app)
2. Create a basic front end CRUD application in Flask that can access and display the data. (You can use any flask extention you want, but must include a requirements.txt.)
3. Use any opensource Bootstrap theme you like for the front end.
4. Allow a user to create and save searches on this data. 
5. You will need to create another MySQL table to store the user searches and results. (Your script must create the table etc)
6. For each search the user creates there are Three fields: SearchID, Search and ResultsData.  
7. For the search field the user must be able to enter: %WORDSEARCH% which is the same as Like%...% in Mysql. (ie Wildcard search)
8. These searches get saved in the new MySQL table.
9. The user can also delete searches.
10. This is a test of your abilities 
11. Thats it.

No login or security is required for this test, just single user as above.
