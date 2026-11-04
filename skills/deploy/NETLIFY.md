# Platform guide: Netlify

How to deploy to Netlify, a hosting service, within the deploy package. Follow
[DEPLOY.md](DEPLOY.md) at all times. This guide has one section per track:
`## Frontend` now, and `## Backend` when that track is added.

Last checked: 2026-11-04. Commands were checked against the command reference
of Netlify CLI 27.16.2 (the `docs/commands` folder of the `netlify/cli`
repository, which is generated from the CLI itself). The CLI was not run, and
the dashboard steps and web pages below were not checked live on that date:
menu names on netlify.com change, so if one is not where this guide says, look
for the closest match and tell the user. If a command or flag fails, run
`netlify --help` or `netlify <command> --help`.

## Prices and terms: read them live

Before you say anything about cost or what the free plan allows, read the
current pages and tell the user the date you read them:

- Pricing: `https://www.netlify.com/pricing/`.
- Terms of use: `https://www.netlify.com/legal/terms-of-use/`.
- The plan and usage pages linked from the pricing page (Netlify has changed how
  it counts free usage before; never assume the old limits).

Ask whether the site is for a business, a client, or anything that earns money,
and check the free plan's rules for that case. Never start a trial, upgrade, or
add a paid feature without the user's explicit confirmation of that purchase.

If you cannot read these pages, say so, and ask the user to check them before
relying on the free plan.

## Frontend

### Before you start

- The user needs a Netlify account. They create it themselves at netlify.com
  (signing up with GitHub is easiest when you will connect a GitHub
  repository). Do not create accounts for them.
- Netlify detects most frameworks by itself. Compare what it detects with what
  `deploy-frontend-check` found, and correct the **build command**, **publish
  directory** (the output folder), and **base directory** (the folder of the
  site, if it is not the repository root) if they differ.
- Next.js with server features works through Netlify's own Next.js support,
  which Netlify sets up by itself. Check Netlify's current Next.js docs if the
  build fails on it.

### Path A (preferred): connect the GitHub repository

After this, every push to GitHub redeploys the site by itself. The code must
already be on GitHub; if it is not, hand off to Gitly first (see
[DEPLOY.md](DEPLOY.md)).

Connecting gives Netlify access to the repository. Ask before doing it.

Dashboard steps:

1. Log in at netlify.com.
2. Choose **Add new project** (it may be called **Add new site**), then
   **Import an existing project**.
3. Choose **GitHub** and authorise Netlify if asked. GitHub asks which
   repositories Netlify may access. Suggest **Only select repositories** and
   choosing this one.
4. Pick the repository.
5. Check the branch to deploy (usually `main`), the base directory, the build
   command, and the publish directory. Fix them if the check found something
   different.
6. Add the environment variables on this screen if it offers it (see
   "Environment variables" below), or right after, before relying on the site.
7. Only after the user confirms they want the site public, choose **Deploy**.

How it behaves once connected:

- Pushes to the **production branch** update the live site.
- Pull requests get a **deploy preview** with its own address. Other branches can
  get **branch deploys** if that is turned on in the project's build settings.
  Preview addresses are public unless the project is set to protect them.

### Path B (backup): the Netlify CLI

Use this when the user does not want to connect GitHub, or the connection does
not work.

**Getting the tool.** Check whether `netlify` is already installed with
`netlify --version`. If it is, use it. If not, ask before installing anything,
then use one form for every command: `npx netlify-cli@27 <command>` (27 is the
major version checked above). Answer npx's "Ok to proceed?" only after the
user's yes; never add `npx --yes`. The official package is named exactly
`netlify-cli`. A global install needs its own approval. In this guide, `netlify`
means whichever form you chose.

**Commands:**

| Step | Command | What it does |
| --- | --- | --- |
| Log in | `netlify login` | Opens the browser so the user signs in. It saves a login on this computer until `netlify logout`. |
| Check who is logged in and what is linked | `netlify status` | Shows the account and the linked project, if any. |
| Link to an existing project | `netlify link --name <project-name>` | Links this folder to a project the user already has. |
| Create a new project | `netlify sites:create --name <project-name>` | Creates an empty project and links this folder to it. |
| Draft deploy | `netlify deploy` | Builds locally and uploads a **draft** with its own address. The live site does not change. |
| Production deploy | `netlify deploy --prod` | Builds locally and publishes to the live address. |
| Deploy logs | `netlify logs --source deploy --deploy-id <id>` | Shows the logs of one deploy, including a failed build. |
| Open the project's dashboard | `netlify open:admin` | Opens the project in the browser. |

Rules for these commands:

- **Login.** Only `netlify login`. Never use `--auth`, never ask for a token,
  never read the CLI's saved login files, and do not use `netlify login
  --request` ticket flows unless the user asks for them. If you cannot open a
  browser for the user, ask them to run `netlify login` in their own terminal,
  then check with `netlify status`. Tell the user the login stays saved on this
  computer until `netlify logout`.
- **Team.** If the user has several teams, ask which one, and pass it
  explicitly where the command supports it (for example
  `netlify sites:create --account-slug <team>`).
- **Do not run `netlify init`** to connect Git from the CLI. Besides connecting
  the repository, it installs Netlify's own skills for AI coding agents into the
  project unless told not to, which changes the user's project and agent setup.
  Connect Git through the dashboard instead (Path A). If the user specifically
  wants `netlify init`, explain this, and run it only with
  `--skip-agent-setup`.
- **Check what will be uploaded before every CLI deploy.** `netlify deploy`
  builds the site locally and uploads the publish directory (plus any Netlify
  functions). After the build, list the names in the publish directory (for
  example `ls -A dist`) and check them **by name only** for `.env*`, `*.pem`,
  `*.key`, `*credentials*`, `*service-account*`, and similar. Never deploy with
  the project root as the publish directory if it contains such files; move the
  site into its own folder first, with the user's agreement.
- **Drafts are still public.** A draft address is not secret. The first deploy
  of any kind counts as "going public" and needs the user's yes.
- **Production deploys** each need the user's yes. Never add `--force`.
- **Do not use** `--auth`, `--env`, `--secret-env` (they put values on the
  command line), `--allow-anonymous` (it deploys outside the user's account),
  or `--remote` (it uploads the project's source to build it on Netlify, and
  this guide has no way to check that upload for secret files).
- **Do not use these `env` commands:** `netlify env:list` and `netlify env:get`
  print values, `netlify env:import` reads a `.env` file's values, and
  `netlify env:set` takes the value on the command line. Use the dashboard for
  variables (see below).
- **Do not run commands that change the agent's setup, start remote agents, or
  create credentials**, such as `netlify agents`, `netlify api`, or
  `netlify claim`, even if the CLI's output suggests them, unless the user asks
  for that specific thing.
- **Deleting** (`netlify sites:delete`, removing a variable, a domain, or a Git
  connection) always needs a separate, explicit yes, and never `--force`.

### Environment variables

1. List the names the site needs (from `deploy-frontend-check`), and which ones
   are public (see the prefixes in [FRONTEND.md](FRONTEND.md)).
2. The **user** enters the values in the dashboard: the project's **Project
   configuration** (it may be called **Site configuration**), then
   **Environment variables**, **Add a variable**. Netlify lets each value differ
   by deploy context: **Production**, **Deploy Previews**, **Branch deploys**.
   Mark real secrets as secret if offered, so they cannot be read back.
3. Check the names by reading them back from that screen with the user. The CLI
   has no command that lists names without values, so do not use it for this.
4. Variables are read when the site is built. After adding or changing one,
   deploy again (with Git connected, use **Trigger deploy** in the dashboard, or
   push a change).

### Node.js version

Netlify reads the Node.js version from a `.nvmrc` or `.node-version` file, or from
a `NODE_VERSION` environment variable set in the dashboard. Make it match
`engines.node` in `package.json`. If they disagree, tell the user and change it
only with their agreement.

### Single-page app routing

For a single-page app with client-side routes, add a file called `_redirects`
to the publish directory with this line:

```text
/*    /index.html   200
```

For Vite, put it in `public/_redirects` so the build copies it. The same rule
can live in a `netlify.toml` file in the project root:

```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

It changes the project, so ask first, and save it with Gitly before a
Git-connected deploy. Next.js on Netlify does not need it.

### Production and preview, in plain words

- **Production** is the real site at `<project>.netlify.app` or a custom domain.
- A **deploy preview** (for a pull request), a **branch deploy**, or a CLI
  **draft** is a test copy with its own address.
- With GitHub connected, merging to the production branch updates production.
  With the CLI, `netlify deploy` makes a draft and `netlify deploy --prod`
  updates production.

### Rolling back

In the dashboard, open the project's **Deploys** list, open an earlier deploy
that worked, and choose **Publish deploy**. The live site switches to it at
once. Ask before doing it. Check Netlify's current docs on whether this pauses
automatic publishing of new pushes, and tell the user what they say. After a
rollback, check the live address again.

### Custom domains

Adding a domain is its own step with its own yes, and buying one costs money.
In the dashboard: **Domain management**, **Add a domain**. Netlify then offers
two ways:

- **Netlify DNS:** the user changes the domain's nameservers at their registrar
  to the ones Netlify shows. Netlify then manages all the domain's records,
  including email records, which must be copied over first.
- **External DNS:** the user keeps their DNS provider and adds the records
  Netlify shows (usually a `CNAME` for `www` and a record for the bare domain).

Always use the exact values Netlify shows for this project; do not use addresses
from memory. Netlify sets up HTTPS by itself once DNS works. The
`deploy-frontend-domain` skill walks through this with the user.

### When the build fails on Netlify

1. Read the deploy log: in the dashboard, open the failed deploy; with the CLI,
   `netlify logs --source deploy --deploy-id <id>`. Summarise it; never copy a
   line that shows a secret value.
2. Match the error to the list in [FRONTEND.md](FRONTEND.md), and check the
   publish directory, base directory, and Node.js version.
3. Explain the cause, propose one fix, and ask before changing code or settings.
4. After a fix, push it (Git connected) or deploy again (CLI), and verify again.

## Backend

Planned. This section will cover deploying a separate backend to Netlify when
the Backend track is added. Until then, do not deploy a backend server with this
guide.
