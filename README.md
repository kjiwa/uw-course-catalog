# UW Course Catalog

This script extracts courses from the UW course catalog and exports them to CSV. The CSV has the following format:

```
Campus,Department,Code,Name,Credits,Areas of Knowledge,Prerequisites
Bothell,B AACT,501,Accounting Theory,4,,
Bothell,B BIO,232,"Embryos, Genes and Reproductive Technology",5,"I&S,NW",
Seattle,A A,101,Air and Space Vehicles,5,NW,
Seattle,PHARM,592,Pharmacy Practice IV: Design and Analysis of Medical Studies,3,,"PHARM 584,PHARM 585,PHARM 586"
Tacoma,T ACCT,210,Financial Accounting I: Users Approach to Accounting,5,,
Tacoma,TWRT,391,Advanced Technical Communication,5,VLPA,TWRT 291
```

As a table, this file has the appearance:

| Campus | Department | Code | Name | Credits | Areas of Knowledge | Prerequisites |
| ------ | ---- | ---- | ------- | ------------------ | ------------- |
| Bothell | B AACT | 501 | Accounting Theory | 4 | | |
| Bothell | B BIO | 232 | Embryos, Genes and Reproductive Technology | 5 | I&S,NW | |
| Seattle | A A | 101 | Air and Space Vehicles | 5 | NW | |
| Seattle | PHARM | 592 | Pharmacy Practice IV: Design and Analysis of Medical Studies | 3 | | PHARM 584,PHARM 585,PHARM 586 |
| Tacoma | T ACCT | 210 | Financial Accounting I: Users Approach to Accounting | 5 | | |
| Tacoma | TWRT | 391 | Advanced Technical Communication | 5 | VLPA | TWRT 291 |

The [output](uwcourses.csv) has been uploaded for those not able or not interested in running the script.
