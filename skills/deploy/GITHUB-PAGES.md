# Platform guide: GitHub Pages

How to deploy to GitHub Pages, GitHub's free hosting for static sites, within the
deploy package. Follow [DEPLOY.md](DEPLOY.md) at all times. This guide has one
section per track: `## Frontend` now. GitHub Pages cannot run server code, so it
will not get a `## Backend` section.

Last checked: 2026-11-04. Settings and rules were checked against GitHub's own
documentation (the `content/pages` folder of the `github/docs` repository) on
that date. The workflow below was checked against the published `action.yml` of
`actions/configure-pages@v6`, `actions/upload-pages-artifact@v5`, and
`actions/deploy-pages@v5`. The `v7` major tags of `actions/checkout` and
`actions/setup-node` were confirmed to exist; their long-standing inputs used
here were not re-read. It has not been run end to end by the vibe.md
maintainers yet. Menu names on github.com change; if one is not where this guide
says, look for the closest match and tell the user.

## Prices and terms: read them live

GitHub Pages has no paid plan of its own, but it has limits and rules of use.
Before you recommend it, read these pages and tell the user what they say and
the date you read them:

- What GitHub Pages is, and which plans can publish from which repositories:
  `https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages`.
  Publishing from a **private** repository has needed a paid GitHub plan; check
  the current rule. A Pages site is public on the internet even when the
  repository is private (except on some enterprise plans).
- Limits and prohibited uses:
  `https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits`.
  On the date above it said Pages is **not** for running an online business, an
  e-commerce site, or commercial software as a service, and listed size,
  bandwidth, and deployment-time limits.
- GitHub's terms: `https://docs.github.com/en/site-policy`.

Always ask whether the site is for a business, a client, or anything that earns
money, and compare that with the rules you just read. A portfolio, a personal
project, documentation, or a small club site usually fits. A shop does not.

## Frontend

### What GitHub Pages can and cannot host

- **Can:** plain HTML, and any site whose build produces static files: Vite
  apps, Create React App, Astro and Gatsby static output, Next.js with
  `output: 'export'`, Nuxt with `nuxt generate`, SvelteKit with
  `adapter-static`.
- **Cannot:** anything that needs code running on the server: Next.js API
  routes, route handlers, server actions, or server rendering; Astro, SvelteKit,
  or Nuxt in server mode; any secret key the site uses at run time. For those,
  recommend Vercel, Netlify, or Cloudflare Pages instead
  (see `deploy-frontend-choose`).

### The site's address and the base path

- A repository named `<user>.github.io` becomes the site
  `https://<user>.github.io/`.
- Any other repository, for example `my-portfolio`, becomes a **project site**
  at `https://<user>.github.io/my-portfolio/`. Everything lives under
  `/my-portfolio/`, so the build must know that "base path" or every script and
  style link breaks and the page is blank.

Set the base path in the framework's config (ask before changing it, it changes
the project):

| Framework | Setting for a project site named `my-portfolio` |
| --- | --- |
| Vite | `base: '/my-portfolio/'` in `vite.config.*` |
| Create React App | `"homepage": "https://<user>.github.io/my-portfolio"` in `package.json` |
| Astro | `site: 'https://<user>.github.io'` and `base: '/my-portfolio'` in `astro.config.*` |
| Next.js (static export) | `basePath: '/my-portfolio'` next to `output: 'export'` in `next.config.*` |
| SvelteKit | `paths: { base: '/my-portfolio' }` under `kit` in `svelte.config.*` |
| Nuxt (generate) | `app: { baseURL: '/my-portfolio/' }` in `nuxt.config.*` |

With a custom domain, or a `<user>.github.io` repository, the base path is `/`
and none of this is needed.

### Before you start

- The code must be on GitHub. If it is not, hand off to Gitly first
  (`gitly-save`, `gitly-github-connect`, `gitly-sync`), as
  [DEPLOY.md](DEPLOY.md) describes.
- The user needs to be an admin of the repository (it is usually their own).
- There is no separate account, login, or command-line tool. Everything happens
  in the repository's settings and in one workflow file.

### The deploy path: a GitHub Actions workflow

GitHub Pages can publish a branch as it is, but most AI-built sites need a build
step first. The recommended way is a GitHub Actions workflow (an automatic job
GitHub runs on its own computers after each push) that builds the site and
publishes the build folder.

1. **Ask before going public.** Turning on Pages publishes the site to anyone
   with the address. Say so, and wait for a yes.
2. **Turn on Pages with Actions as the source.** The user opens the repository
   on github.com, then **Settings**, then **Pages**. Under **Build and
   deployment**, set **Source** to **GitHub Actions**.
3. **Add the workflow file.** Propose `.github/workflows/deploy-pages.yml`
   (a change to the project, so ask first). For an npm project built with
   `npm run build` into `dist/`:

   ```yaml
   name: Deploy to GitHub Pages

   on:
     push:
       branches: [main]
     workflow_dispatch:

   permissions:
     contents: read
     pages: write
     id-token: write

   concurrency:
     group: pages
     cancel-in-progress: false

   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v7
         - uses: actions/setup-node@v7
           with:
             node-version: 22
             cache: npm
         - run: npm ci
         - run: npm run build
         - uses: actions/configure-pages@v6
         - uses: actions/upload-pages-artifact@v5
           with:
             path: dist

     deploy:
       needs: build
       runs-on: ubuntu-latest
       environment:
         name: github-pages
         url: ${{ steps.deployment.outputs.page_url }}
       steps:
         - id: deployment
           uses: actions/deploy-pages@v5
   ```

   Adapt it to what `deploy-frontend-check` found:
   - the production branch, if it is not `main`;
   - the Node.js major version (`engines.node`, `.nvmrc`, or `.node-version`);
   - the package manager's install and build commands from
     [FRONTEND.md](FRONTEND.md) (for pnpm, Yarn, or Bun, also change `cache:`
     or remove it, and add that tool's setup step if needed);
   - the output folder in `path:` (`dist`, `build`, `out`, `public`, or
     `.output/public`);
   - for a plain HTML site with no build, remove the `setup-node`, `npm ci`,
     and `npm run build` steps and set `path:` to the folder with `index.html`.
4. **Save and push it.** Use `gitly-save`, then `gitly-sync`. The push starts
   the first deploy. Ask before pushing (it publishes the site).
5. **Watch it.** On github.com, open the repository's **Actions** tab and the
   newest "Deploy to GitHub Pages" run. When it finishes, the `deploy` job shows
   the site's address.

After this, every push to the production branch rebuilds and republishes the
site by itself. There are no automatic preview addresses for other branches.

What gets uploaded: `upload-pages-artifact` packs only the folder in `path:`,
and leaves out hidden files and folders (names starting with a dot) unless told
otherwise. Never set `include-hidden-files: true`. Before the first deploy,
list the names in the output folder (for example `ls -A dist`) and make sure no
`.env*`, `*.pem`, `*.key`, or credentials file was copied into it.

### Environment variables

A GitHub Pages site is only static files, so **every value the site uses is
public**: it is baked into the files at build time and anyone can read it. There
is no place for a secret.

- Only public values belong here: a Supabase URL and its public key, Firebase
  web config, an analytics ID. If the site needs a real secret, it cannot use
  GitHub Pages for that part; say so and suggest `deploy-frontend-choose`.
- The user adds each value in the repository: **Settings**, **Secrets and
  variables**, **Actions**, then the **Variables** tab, **New repository
  variable**. Use variables, not secrets, because the values end up public
  anyway and variables are honest about that.
- Pass them to the build step in the workflow by name only, for example:

  ```yaml
         - run: npm run build
           env:
             VITE_SUPABASE_URL: ${{ vars.VITE_SUPABASE_URL }}
             VITE_SUPABASE_ANON_KEY: ${{ vars.VITE_SUPABASE_ANON_KEY }}
  ```

- Changing a value needs a new build: re-run the workflow (Actions tab, the
  workflow, **Run workflow**) or push a change.

### Node.js version

Set `node-version:` in the workflow to the major version the project needs
(`engines.node`, `.nvmrc`, or `.node-version`). The `setup-node` action can also
read the file with `node-version-file: .nvmrc` instead.

### Single-page app routing

GitHub Pages has no rewrite rules, so opening `/about` directly in a single-page
app gives GitHub's 404 page. Two options, explain both and let the user choose:

1. **Copy `index.html` to `404.html`** in the build output, for example by adding
   `&& cp dist/index.html dist/404.html` to the build step. GitHub serves
   `404.html` for unknown paths, so the app loads and handles the route. The
   address works in a browser, but the server still answers with status 404.
   Most visitors never notice, but search engines may not index those pages,
   and a `curl` check shows 404 even though the page renders.
2. **Use hash-based routing** (`/#/about`) in the router. Every address loads
   `index.html` with status 200, at the cost of a `#` in the address.

Framework sites that build every page as its own file (Astro, Gatsby, a Next.js
static export, `nuxt generate`) usually do not need either.

### Production and preview

GitHub Pages has one live site per repository. Each push to the production
branch replaces it. There are no preview addresses for other branches; to check a
change before it goes live, build and run it locally
(`npm run build` then `npm run preview` for Vite), or use another host for
previews.

### Rolling back

There is no "promote an older deployment" button. Two safe options:

1. **Re-run the last good workflow run.** In the **Actions** tab, open the run
   of the last version that worked, and choose **Re-run all jobs**. A re-run uses
   the same commit as the original run, so it rebuilds and republishes that
   version. The next push to the production branch publishes the newest code
   again, so fix the problem before pushing.
2. **Undo the change in Git** (for example with Gitly's `gitly-restore`), then
   push. This keeps the fix in the history and is the durable option.

Ask before either one: both change the live site.

### Custom domains

Adding a domain is its own step with its own yes, and buying one costs money.
The steps below follow GitHub's documentation on the date above:

- **Add the domain in GitHub first:** **Settings**, **Pages**, **Custom domain**,
  type the domain, **Save**. With the Actions workflow, no `CNAME` file is needed.
- **A `www` or other subdomain** (`www.example.com`): at the domain's DNS
  provider, add a `CNAME` record pointing to `<user>.github.io` (without the
  repository name).
- **The bare domain** (`example.com`, the "apex"): add `A` records to GitHub's
  addresses, which GitHub's docs listed as `185.199.108.153`, `185.199.109.153`,
  `185.199.110.153`, and `185.199.111.153` (and `AAAA` records for IPv6). Read the
  current list on GitHub's "Managing a custom domain" page before using them.
- GitHub recommends setting up both `example.com` and `www.example.com`.
- **Never use a wildcard record** such as `*.example.com`: GitHub warns it lets
  others take over subdomains.
- **Verify the domain** in the user's GitHub account settings (Pages,
  verified domains) to stop someone else claiming it.
- After DNS works, tick **Enforce HTTPS** on the Pages settings screen. The
  certificate can take a while to appear.

The `deploy-frontend-domain` skill walks through this with the user.

### When the build or deploy fails

1. Open the failed run in the **Actions** tab and the step that failed. Read
   its log. Summarise it; never copy a line that shows a secret value.
2. Common GitHub Pages causes, on top of the list in
   [FRONTEND.md](FRONTEND.md):
   - **Pages source is not set to GitHub Actions**, or Pages is not enabled:
     the deploy job fails or nothing is published.
   - **Wrong `path:`** in `upload-pages-artifact`: an empty site or a 404.
   - **Blank page with errors loading scripts**: the base path is missing (see
     above).
   - **The `deploy` job waits or is rejected**: the `github-pages` environment
     only allows certain branches. Check **Settings**, **Environments**,
     **github-pages**, and the deployment branch rules.
   - **Permissions error in the deploy job**: the workflow is missing
     `pages: write` or `id-token: write`.
3. Explain the cause, propose one fix, and ask before changing files or
   settings. Save and push the fix with Gitly, and check the new run.

## Backend

Not supported. GitHub Pages only serves static files and cannot run a backend
server.
