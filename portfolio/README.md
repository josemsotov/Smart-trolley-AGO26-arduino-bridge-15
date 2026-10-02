# Smart Golf Trolley portfolio

Static portfolio case study for SOTO-ROBOTICS, led by Jose M Soto V. It is intentionally dependency-free and can be published on any static web host.

The systems-engineering section applies a V-model/MBSE-inspired workflow to the implemented trolley baseline. Its requirements, safety functions and hazard priorities are preliminary engineering artefacts for an R&D prototype; they are not certification, an ISO 26262 assessment or permission for unsupervised operation.

## Preview locally

Open `index.html` directly in a browser, or from this directory run:

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Recommended LinkedIn publishing route

GitHub Pages is preferable to Google Drive for this portfolio. Google Drive stores and shares the files, but it does not serve a folder as a normal public website and should not be used as the LinkedIn destination.

1. Keep the `portfolio` directory in a public GitHub repository.
2. In the repository, open **Settings > Pages**.
3. Select **Deploy from a branch**, choose the publishing branch and select the repository root.
4. Use the resulting `https://<username>.github.io/<repository>/portfolio/` address. Alternatively, copy these four files into a `docs` directory, select `/docs` as the Pages source and use the main Pages address.
5. Add the public address to the **Featured** section of LinkedIn.

Suggested LinkedIn title: **Smart Golf Trolley — Robotics R&D by SOTO-ROBOTICS**

Suggested LinkedIn description: **A multidisciplinary engineering case study covering embedded motor control, ROS 2, perception, electronics, mechanical integration, safety and prototype validation.**

Alternatives such as Netlify, Cloudflare Pages or Google Firebase Hosting can publish the same files without modification.

## Revision traceability

The public page identifies its technical baseline with a Git tag. For the first published release, `portfolio-v1.0.0` points to the exact repository commit containing the portfolio claims, interface documentation and supporting implementation revision. Future material changes should use a new tag rather than moving an existing tag.

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
