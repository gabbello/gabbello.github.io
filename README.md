# gabbello.github.io

This repository contains scripts to fetch and publish EPG files.

Usage
-----

- `fetch_pluto.py`: downloads https://nocords.xyz/pluto/epg.xml and writes `pluto.xml` in the repository root.
- `download_epg.py`: (existing) downloads the main EPG and produces `epg_all.xml.gz`.
- `run_all.sh`: runs both scripts concurrently.

Run locally:

```bash
chmod +x run_all.sh
./run_all.sh
```

CI
--

The GitHub Actions workflow `.github/workflows/update_epg.yml` was updated to run both scripts and commit `pluto.xml` alongside `epg_all.xml.gz`.

