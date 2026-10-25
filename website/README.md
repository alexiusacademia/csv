# csv's website

The page for the csv library, live at https://csv-package.syncster.dev.

Author: Alexius Academia · Started 2026-10-25

A static page: no build step, no dependencies. Netlify (project
`csv-package`, id `711f09a2-58d1-4da8-bede-9d30947e3304`, team syncster.dev)
deploys this folder by itself whenever
`main` is pushed to GitHub.

```
index.html          # the page; its example outputs were printed by running them
styles.css          # chart's website's design, in green
assets/flows.png    # flows.csv read with csv and plotted with chart
assets/share.png    # the picture shown when a link to the site is shared (1200 × 630)
assets/favicon.svg
netlify.toml        # no build; HTML isn't cached
```

To look at it locally: `python3 -m http.server 8080 -d website`, then
http://localhost:8080/.

If an example changes, run it with the library and copy its output in.
