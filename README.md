# RETAIL DATA ENGINEER PIPELINE 

```bash
pipenv shell
```

```bash
exit
```

```bash
Name:     retail_pipeline
Host:     postgres       
Port:     5432
Database: retail_pipeline
Username: postgres
Password: root
```

```bash
# Daily run (only loads today)
python load.py

# Backfill run (loads all missing dates)
python load.py --backfill
```

