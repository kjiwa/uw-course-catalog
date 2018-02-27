# University of Washington Course Catalog

This script extracts courses from the University of Washington course catalog and exports them to CSV. The script works by searching for department links for each campus from the following web pages:

* Bothell: http://www.washington.edu/students/crscatb/
* Seattle: http://www.washington.edu/students/crscat/
* Tacoma: http://www.washington.edu/students/crscatt/

Each department web page is analyzed with a DOM parser and regular expressions for course codes, names, credits, areas of knowledge, and prerequisites.

The ```--campus``` and ```--department_link``` command line flags may be used to limit the data extracted by the script. Use the ```--help``` flag for more details.

The CSV has the following format:

* Campus
* Department
* Course Code
* Course Name
* Credits
* Areas of Knowledge
* Prerequisites

For example, the raw CSV may have data such as the following:

```
Campus,Department,Code,Name,Credits,Areas of Knowledge,Prerequisites
Bothell,B AACT,501,Accounting Theory,4,,,
Bothell,B BIO,232,"Embryos, Genes and Reproductive Technology",5,"I&S,NW",,
Seattle,A A,101,Air and Space Vehicles,5,NW,,
Seattle,E E,235,Continuous Time Linear Systems,5,,"AMATH 351,CSE 142,CSE 143,MATH 136,MATH 307,PHYS 122","A,W,Sp"
Seattle,PHARM,592,Pharmacy Practice IV: Design and Analysis of Medical Studies,3,,"PHARM 584,PHARM 585,PHARM 586",A
Tacoma,T ACCT,210,Financial Accounting I: Users Approach to Accounting,5,,,A
Tacoma,TWRT,391,Advanced Technical Communication,5,VLPA,TWRT 291,
```

As a table, this data has this appearance:

| Campus | Department | Code | Name | Credits | Areas of Knowledge | Prerequisites | Offered |
| ------ | ---------- | ---- | ---- | ------- | ------------------ | ------------- | ------- |
| Bothell | B AACT | 501 | Accounting Theory | 4 | | | |
| Bothell | B BIO | 232 | Embryos, Genes and Reproductive Technology | 5 | I&S,NW | | |
| Seattle | A A | 101 | Air and Space Vehicles | 5 | NW | | |
| Seattle | E E | 235 | Continuous Time Linear Systems | 5 | | AMATH 351,CSE 142,CSE 143,MATH 136,MATH 307,PHYS 122 | A,W,Sp |
| Seattle | PHARM | 592 | Pharmacy Practice IV: Design and Analysis of Medical Studies | 3 | | PHARM 584,PHARM 585,PHARM 586 | |
| Tacoma | T ACCT | 210 | Financial Accounting I: Users Approach to Accounting | 5 | | | A |
| Tacoma | TWRT | 391 | Advanced Technical Communication | 5 | VLPA | TWRT 291 | |

The [output](uwcourses.csv) has been uploaded for those not able or willing to run the script.
