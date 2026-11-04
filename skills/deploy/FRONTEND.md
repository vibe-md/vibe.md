# Deploy track: Frontend

This guide is for the frontend track: the part of a project that runs in the
visitor's browser, which means the pages, buttons, and styles people see. Follow
[DEPLOY.md](DEPLOY.md) at all times. This file adds what is specific to
websites.

## What this track covers

In scope:

- Plain static sites: HTML, CSS, and JavaScript files with no build step.
- Single-page apps built with React, Vue, or Svelte using Vite, or Create React
  App.
- Next.js, Astro, SvelteKit, Nuxt, Gatsby, and similar frameworks, including the
  small server parts they deploy together with the site on the host (for example
  Next.js API routes, route handlers, and server actions on Vercel).
- Sites that call an outside service, such as Supabase, Firebase, Stripe, or an
  AI API, through environment variables.

Out of scope for now (planned for later tracks):

- **A separate backend server** that has to run on its own, for example an
  Express, Fastify, NestJS, Flask, Django, or FastAPI app that starts with
  something like `app.listen(...)` or `uvicorn`. Planned for the Backend track.
- **A database the project has to create or run itself**, for example a local
  PostgreSQL or MySQL server, a `docker-compose.yml` with a database, migrations
  that must run against a new database, or a SQLite file the app writes to (it
  will not keep its data on most frontend hosts). Planned for the Database track.

A hosted service the site only calls (Supabase, Firebase, a hosted API) is in
scope: the site only needs the right environment variables.

Never this package: Docker images, VPS servers, Kubernetes.

## Detecting the framework

Read `package.json` (dependencies and the `scripts` section) and look for the
config files below. If there is no `package.json` but there is an `index.html`,
it is a plain static site.

| Framework | How to recognise it | Build command | Output folder |
| --- | --- | --- | --- |
| Plain static | `index.html`, no `package.json` | none | the folder with `index.html` |
| Vite (React, Vue, Svelte) | `vite` dependency, `vite.config.*` | `vite build` (usually `npm run build`) | `dist/` |
| Create React App | `react-scripts` dependency | `react-scripts build` | `build/` |
| Next.js | `next` dependency, `next.config.*` | `next build` | `.next/` (the host handles it); with `output: 'export'` in the config, a static `out/` |
| Astro | `astro` dependency, `astro.config.*` | `astro build` | `dist/`; with `output: 'server'` and an adapter, the host runs part of it |
| SvelteKit | `@sveltejs/kit` dependency, `svelte.config.*` | `vite build` | depends on the adapter in `svelte.config.*` |
| Nuxt | `nuxt` dependency, `nuxt.config.*` | `nuxt build` or `nuxt generate` | `.output/` (`.output/public/` for `generate`) |
| Gatsby | `gatsby` dependency | `gatsby build` | `public/` |

Always prefer what the project itself says: the `build` script in
`package.json`, and an output folder set in the framework's config file, win
over this table.

### Package manager

The lock file tells you which package manager the project uses. Use the same
one, or the host and the user's computer may install different versions.

| Lock file | Package manager | Install | Build |
| --- | --- | --- | --- |
| `package-lock.json` | npm | `npm ci` | `npm run build` |
| `pnpm-lock.yaml` | pnpm | `pnpm install --frozen-lockfile` | `pnpm run build` |
| `yarn.lock` | Yarn | `yarn install --frozen-lockfile` (Yarn 1) or `yarn install --immutable` (Yarn 2+) | `yarn build` |
| `bun.lock` or `bun.lockb` | Bun | `bun install --frozen-lockfile` | `bun run build` |

No lock file at all is worth flagging: the host may install newer versions of
packages than the user tested with.

## Public variables and why secrets must never go there

Frontend frameworks copy some environment variables (named settings kept outside
the code) **into the files sent to every visitor's browser**. Anyone can read
them by opening the page's source or developer tools. The framework decides
which ones by the start of the name:

| Prefix | Framework |
| --- | --- |
| `NEXT_PUBLIC_` | Next.js |
| `VITE_` | Vite |
| `PUBLIC_` | Astro, SvelteKit |
| `REACT_APP_` | Create React App |
| `NUXT_PUBLIC_` | Nuxt |
| `GATSBY_` | Gatsby |

In a plain static site, or in any code that runs in the browser, **every**
value in the code is public, whatever its name.

What is fine in a public variable: things designed to be public, such as the
site's own address, a Supabase project URL and its public ("anon" or
"publishable") key, Firebase web config, a Stripe publishable key (starts with
`pk_`), or an analytics ID.

What must never be in a public variable: anything called secret, private,
service role, admin, password, or token; payment secret keys; AI provider API
keys (OpenAI, Anthropic, and others); database connection strings; email-service
keys. If someone can copy it and use it to spend money or read other people's
data, it is a secret.

Signs of a problem to flag (by name only, never the value):

- A public-prefixed name containing `SECRET`, `PRIVATE`, `SERVICE_ROLE`,
  `ADMIN`, `PASSWORD`, `TOKEN`, `DATABASE_URL`, or a paid provider's key name,
  for example `NEXT_PUBLIC_OPENAI_API_KEY` or `VITE_STRIPE_SECRET_KEY`.
- Browser code that calls a paid API directly with a key.

The fix is not renaming the variable. The secret has to move to code that runs on
the server (for example a Next.js route handler or server action, or a hosted
function), or the call has to go through a service designed for browser use.
If the secret was ever deployed or pushed, the user should also replace it with
a new one in the provider's dashboard, because the old one may already be
copied. Explain this plainly and let the user decide; do not rewrite the
architecture without asking.

## Why it "works on my computer" but fails online

Check these first when the build or the live site fails.

1. **File-name case.** Windows and macOS usually treat `Header.jsx` and
   `header.jsx` as the same file. The host runs Linux, where they are different.
   An import of `./components/header` fails online if the file is
   `Header.jsx`. Compare each import with the exact names in `git ls-files`
   (what GitHub has is what the host builds). A file renamed only by case
   sometimes is not renamed in Git at all.
2. **Missing environment variables.** `.env` and `.env.local` files are (and
   should be) kept out of Git, so the host does not have them. Every variable
   the code reads must be set on the host. Variables used during the build
   (most public-prefixed ones; SvelteKit's `$env/dynamic/public` is read when the site runs) must be set before the build, so changing one
   needs a new deploy.
3. **Node.js version.** The host may use a different Node.js version. Look at
   `engines.node` in `package.json`, `.nvmrc`, or `.node-version`, and set the
   same major version on the host.
4. **Wrong output folder or build command.** The host must publish the folder the
   build creates (see the table above). A wrong folder gives an empty site or a
   "not found" page.
5. **Client-side routing 404s.** In a single-page app, `/about` exists only
   inside the JavaScript app. Opening `/about` directly, or refreshing on it,
   asks the host for a file that does not exist and gives a 404. The host
   needs a rule that sends every unknown path to `index.html`. Each platform
   guide shows how. Next.js and Astro handle this themselves on hosts that run
   them, but a static export (Next.js `output: 'export'`), a Nuxt site with
   `ssr: false`, or SvelteKit with `adapter-static` and a fallback page can
   still need a rule.
6. **Dependencies only on the user's computer.** A package installed globally,
   or imported but missing from `package.json`, works locally and fails on the
   host. So does a lock file that is out of date or not committed.
7. **Hard-coded local addresses.** Code that calls `http://localhost:3000` or
   `127.0.0.1` works only on the user's computer. It should read the address
   from an environment variable.
8. **Build warnings treated as errors.** Some hosts and frameworks fail the
   build on lint or type errors that the local dev server only warns about. Run
   the real build command locally, not just the dev server.

## Which platform fits which site

| Site type | Vercel | Netlify | Cloudflare Pages | GitHub Pages |
| --- | --- | --- | --- | --- |
| Plain static HTML | Yes | Yes | Yes | Yes |
| React, Vue, Svelte with Vite (single-page app) | Yes | Yes | Yes | Yes, with a routing workaround |
| Next.js with server features (API routes, server rendering) | Yes, made by the Next.js team | Yes, through its Next.js support | Not in this package: Cloudflare's current path for it runs on Workers, which this package does not cover yet | **No** |
| Next.js static export (`output: 'export'`) | Yes | Yes | Yes | Yes |
| Astro, SvelteKit, Nuxt, Gatsby | Yes | Yes | Yes | Static output only |

- **Vercel**: the best fit for Next.js, and a good default for most sites.
  Guide: [VERCEL.md](VERCEL.md).
- **Netlify**: a similar experience, popular for static sites and forms, with
  its own Next.js support. Guide: [NETLIFY.md](NETLIFY.md).
- **Cloudflare Pages**: fast worldwide, generous with traffic, and a natural fit
  when the domain is already on Cloudflare. Cloudflare now recommends its
  Workers product for new projects and for server-rendered Next.js, which this
  package does not cover yet. Guide: [CLOUDFLARE-PAGES.md](CLOUDFLARE-PAGES.md).
- **GitHub Pages**: free hosting straight from a GitHub repository, for static,
  non-commercial sites only. It cannot run server code or keep a secret, so it
  cannot host server-rendered Next.js. Guide: [GITHUB-PAGES.md](GITHUB-PAGES.md).

Whatever the platform, check its prices and terms live before recommending it
(see [DEPLOY.md](DEPLOY.md)). Do not compare prices from memory.

If the user has no preference, use `deploy-frontend-choose` to compare the four
hosts for this project. If they want a host without a guide here, follow that
host's official documentation, read live, under the rules in
[DEPLOY.md](DEPLOY.md), and tell the user you are not using a vibe.md guide for
it.
