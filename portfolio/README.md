# Smart Golf Trolley portfolio

Static portfolio case study for Jose M Soto V. It is intentionally dependency-free and can be published on any static web host.

## Preview locally

Open `index.html` directly in a browser, or from this directory run:

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Recommended LinkedIn publishing route

GitHub Pages is preferable to Google Drive for this portfolio. Google Drive stores and shares the files, but it does not serve a folder as a normal public website.

1. Keep the `portfolio` directory in a public GitHub repository.
2. In the repository, open **Settings > Pages**.
3. Select **Deploy from a branch**, choose the branch and `/portfolio` source if available.
4. If GitHub only offers the repository root or `/docs`, copy these four files into a `docs` directory and select `/docs`.
5. Add the resulting `https://...github.io/...` address to the **Featured** section of LinkedIn.

Alternatives such as Netlify, Cloudflare Pages or Google Firebase Hosting can publish the same files without modification.

## Before publishing

- Add genuine project photographs when available. The page currently reserves three labelled positions:
  1. A full view of the complete off-the-shelf trolley and robotic conversion.
  2. Close-ups of the custom 3D-printed mounts, brackets or enclosures.
  3. Electronics packaging, cable routing and service access.
- The current hero uses an original inline technical illustration and the gallery uses deliberate technical placeholders, so no stock image is presented as the real trolley.
- When the photographs are ready, optimise them as WebP images at roughly 1600 px wide for the overview and 1000 px wide for close-ups. Add meaningful `alt` text that explains the engineering detail visible in each image.
- Check that `josemsotov@gmail.com` is the preferred public contact.
- Test the final public URL on a phone and desktop.
- Do not publish private network addresses, credentials or source files containing deployment secrets.
