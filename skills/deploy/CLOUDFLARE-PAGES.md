# Platform guide: Cloudflare Pages

How to deploy to Cloudflare Pages, a hosting service, within the deploy package.
Follow [DEPLOY.md](DEPLOY.md) at all times. This guide has one section per
track: `## Frontend` now.

Last checked: 2026-11-04. Commands were checked against the source of Wrangler
4.157.0 (the `packages/wrangler/src/pages` folder of the
`cloudflare/workers-sdk` repository), and the behaviour notes against
Cloudflare's documentation repository (`cloudflare/cloudflare-docs`, the
`pages/configuration` pages) on that date. Wrangler was not run, and the
dashboard and web pages were not checked live: menu names change, so if one is
not where this guide says, look for the closest match and tell the user. If a
command or flag fails, run `wrangler pages --help` or
`wrangler pages <command> --help`.

## Pages and Workers: an important difference

Cloudflare has two products that can host a website: **Pages** (this guide) and
**Workers** with static assets. Cloudflare recommends Workers for new projects,
and its tools increasingly steer there:

- The dashboard may offer to create a Worker instead of a Pages project.
- **Wrangler hands new static Pages projects to Workers when a coding agent
  runs it.** If an agent runs `wrangler pages project create` or
  `wrangler pages deploy` for a project that does not exist yet, Wrangler may
  deploy it to Workers instead, without asking.

This guide covers Pages only. So: **create the Pages project in the dashboard**,
and use Wrangler only to deploy to a Pages project that already exists. If
Wrangler's output says it is deploying to Workers, stop, tell the user, and do
not add `--force` to override it without their explicit yes. Workers hosting is
not covered by this package yet.

Next.js with server features: Cloudflare's current recommended path for it runs
on Workers, not Pages. For server-rendered Next.js, recommend Vercel or Netlify
in this version.

## Prices and terms: read them live

Before you say anything about cost or what the free plan allows, read the
current pages and tell the user the date you read them:

- Plans: `https://www.cloudflare.com/plans/developer-platform/`.
- Pages limits: `https://developers.cloudflare.com/pages/platform/limits/`.
- Terms: `https://www.cloudflare.com/website-terms/`.

These addresses may have moved; if one does not load, search cloudflare.com for
the page instead of guessing. Ask whether the site is for a business, a client,
or anything that earns money, and check the rules for that case. Never start a
paid plan or add a paid feature without the user's explicit confirmation.

## Frontend

### Before you start

- The user needs a Cloudflare account. They create it themselves at
  cloudflare.com. Do not create accounts for them.
- Pages builds most frameworks with a **framework preset**. Compare it with what
  `deploy-frontend-check` found, and set the **build command**, **build output
  directory**, and **root directory** (the site's folder, if it is not the
  repository root) to match.

### Path A (preferred): connect the GitHub repository

After this, every push to GitHub redeploys the site by itself. The code must
already be on GitHub; if it is not, hand off to Gitly first (see
[DEPLOY.md](DEPLOY.md)).

Connecting gives Cloudflare access to the repository. Ask before doing it.

Dashboard steps:

1. Log in at dash.cloudflare.com.
2. Open **Workers & Pages**, choose **Create**, and pick the **Pages** option
   that imports an existing Git repository. If the screen offers only a Worker,
   stop and tell the user (see "Pages and Workers" above).
3. Connect GitHub if asked. GitHub asks which repositories Cloudflare may
   access. Suggest **Only select repositories** and choosing this one.
4. Pick the repository, the production branch (usually `main`), the framework
   preset, the build command, and the build output directory.
5. Add the environment variables (see below) before the first build if the
   screen offers it.
6. Only after the user confirms they want the site public, choose **Save and
   Deploy**.

How it behaves once connected:

- Pushes to the **production branch** update the live site at
  `<project>.pages.dev`.
- Pushes to other branches get **preview deployments** with their own
  addresses, public by default.

### Path B (backup): Wrangler, for an existing Pages project

Use this only when the Pages project already exists (create it in the dashboard
first, with **Direct Upload** instead of Git if the user does not want GitHub).

**Getting the tool.** Check whether `wrangler` is already installed with
`wrangler --version`. If not, ask before installing anything, then use one form
for every command: `npx wrangler@4 <command>`. Answer npx's "Ok to proceed?"
only after the user's yes; never add `npx --yes`. The official package is named
exactly `wrangler`. In this guide, `wrangler` means whichever form you chose.

**Commands:**

| Step | Command | What it does |
| --- | --- | --- |
| Log in | `wrangler login` | Opens the browser so the user signs in. It saves a login on this computer until `wrangler logout`. |
| Check who is logged in | `wrangler whoami` | Shows the account. |
| List projects | `wrangler pages project list` | Shows the user's Pages projects. Confirm the project exists. |
| Deploy | `wrangler pages deploy <output-folder> --project-name <name> --branch <branch>` | Uploads the built folder. With the production branch it updates the live site; with any other branch it makes a preview. |
| List deployments | `wrangler pages deployment list --project-name <name>` | Shows recent deployments and their addresses. |
| Add a runtime secret | `wrangler pages secret put <NAME> --project-name <name>` | Asks for the value with hidden typing. For the user's own terminal only. |
| List runtime secret names | `wrangler pages secret list --project-name <name>` | Shows names only ("Value Encrypted"). |

Rules for these commands:

- **Login.** Only `wrangler login`. Never use an API token, never ask for one,
  and never read Wrangler's saved login files. If you cannot open a browser for
  the user, ask them to run `wrangler login` in their own terminal, then check
  with `wrangler whoami`. Tell the user the login stays saved on this computer
  until `wrangler logout`.
- **Build first, then deploy only the output folder.** `wrangler pages deploy`
  uploads the folder it is given. Run the build, then list the names in the
  output folder (for example `ls -A dist`) and check them **by name only** for
  `.env*`, `.dev.vars`, `*.pem`, `*.key`, `*credentials*`, and similar. Never
  deploy the project root.
- **Always pass `--project-name` and `--branch` explicitly**, after asking the
  user, so nothing is chosen for them. Passing the production branch publishes
  to the live site; get the user's yes for each production deploy.
- **Do not use** `--force` (it skips the Workers hand-off described above), or
  `wrangler pages secret bulk` (it reads values from a file).
- **Do not create projects with Wrangler** (`wrangler pages project create`);
  use the dashboard.
- **Deleting** (`wrangler pages project delete`,
  `wrangler pages deployment delete`, `wrangler pages secret delete`) always
  needs a separate, explicit yes.

### Environment variables

Cloudflare Pages has two kinds, and it matters which one the site needs:

- **Build-time variables** are read while the site is built. Public variables
  (`VITE_`, `NEXT_PUBLIC_`, `PUBLIC_`, and so on, see
  [FRONTEND.md](FRONTEND.md)) are always this kind. The user adds them in the
  dashboard: the project's **Settings**, **Variables and Secrets**, for
  **Production** and **Preview** separately. They take effect on the next build.
- **Runtime secrets** are only for Pages Functions (server code in a
  `functions/` folder). The user adds them in the same dashboard screen as
  encrypted values, or in their own terminal with
  `wrangler pages secret put <NAME> --project-name <name>`. Never type the value
  for them and never put it on a command line.

Check the names with the user on the dashboard screen, or with
`wrangler pages secret list` for runtime secrets. Report names only.

### Node.js version

The build system reads the Node.js version from a `.nvmrc` or `.node-version`
file, or from a `NODE_VERSION` variable in the project's settings. Make it match
`engines.node`. Cloudflare moves projects to newer build images over time
(older images are being retired during 2026 and 2027), which can change the
default version, so setting it explicitly avoids surprises.

### Single-page app routing

If the build output has **no top-level `404.html`**, Pages treats the site as a
single-page app and serves the home page for any path that is not a file, so
`/about` works without extra setup. If the output does have a `404.html`, Pages
shows it for unknown paths instead; a single-page app then needs a `_redirects`
file in the output folder:

```text
/*    /index.html   200
```

Adding it changes the project, so ask first.

### Production and preview, in plain words

- **Production** is the real site at `<project>.pages.dev` or a custom domain.
- A **preview** is a test copy at its own address for another branch (or, with
  Wrangler, any `--branch` that is not the production branch).

### Rolling back

In the dashboard, open the project's **Deployments**, find the earlier
production deployment that worked, open its menu (the three dots), and choose
**Rollback to this deployment**. It switches the live site at once. Only
successful production deployments can be rollback targets, not previews. Ask
before doing it, and check the live address afterwards.

### Custom domains

Adding a domain is its own step with its own yes, and buying one costs money.
Always add the domain in the Pages project first (**Custom domains**, **Set up a
custom domain**), then change DNS:

- **A subdomain** such as `www.example.com` or `shop.example.com`: if the domain's
  DNS is not on Cloudflare, add a `CNAME` record at the DNS provider pointing to
  `<project>.pages.dev`. Adding the record before adding the domain in the
  project gives a 522 error.
- **The bare domain** (`example.com`): Cloudflare requires the domain to be a
  zone on the same Cloudflare account, which means changing the domain's
  nameservers to Cloudflare's. That moves all the domain's DNS records to
  Cloudflare, including email (MX) records, which must be copied first.

Cloudflare sets up HTTPS by itself once DNS works. The `deploy-frontend-domain`
skill walks through this with the user.

### When the build fails on Cloudflare Pages

1. Open the failed deployment in the dashboard and read its build log.
   Summarise it; never copy a line that shows a secret value.
2. Match the error to the list in [FRONTEND.md](FRONTEND.md). On Cloudflare also
   check the build output directory, the root directory, and the Node.js
   version.
3. Explain the cause, propose one fix, and ask before changing code or settings.
4. After a fix, push it (Git connected) or deploy again (Wrangler), and verify
   again.

## Backend

Not covered. Server code on Cloudflare runs on Workers, which this package does
not cover yet.
