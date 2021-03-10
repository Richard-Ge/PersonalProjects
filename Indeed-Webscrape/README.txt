This code works, but needs some cleaning up/additional functionality. I plan to connect it to a MySQL server with pyodbc, but I haven't found an inexpensive, non-enterprise hosting service yet. Also could use some NLP for the keyword search function.

TODO: 

- Have one window for console outputs (e.g. progress, 3/15 scraped), one for summary output, one for job words

- Have inputs for user, way to quit/stop running (on exit?)

- Find a way to verify results? print page text to different document, compare the two? 

- TEST INDEED FOR: max character limit in jobs? will jobs that have a key be updated, while keeping the key?

- Periodically check, & save new jobs so they won't disappear!

- Otherwise, there will be anti-recency bias, and more urgently filled jobs will not show up. Job keys are perfect for a SQL/MongoDB database, as well as employer lists/foreign keys!

- Try using an API (RESTful? ODBC?) to connect Python and HTML/SQL

- Calculate upload date & time from the age!

- Non-enterprise: subscribe to a virtual instance, install MySql on it, just update it a few times a day (need to optimize for best update times: (early) morning? afternoon/evening?
