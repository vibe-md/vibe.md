---
name: deploy-frontend-domain
description: Connects a custom domain (your own web address, such as my-site.com) to a website that is already online. Explains DNS records in plain words, checks the domain's current DNS before any change, adds the domain on the host, guides the user through the exact records the host shows (www versus the bare domain), warns about email (MX) records and costs, waits for DNS to spread, checks HTTPS, and verifies the address works. Asks before every DNS or host change and never buys a domain. Use when the user says "connect my domain", "use my own domain", "point my GoDaddy domain to Vercel", "my domain shows an error", "תחבר לי את הדומיין", or "איך שמים דומיין משלי על האתר?". Not for a first deploy (use deploy-frontend-launch), not for email hosting setup, and not for backend servers.
license: MIT
compatibility: Needs network access, a site already deployed on a supported host (Vercel, Netlify, Cloudflare Pages, or GitHub Pages), and a domain the user already owns with access to its DNS settings at their registrar or DNS provider, which the user logs in to themselves. Uses read-only DNS lookups (dig, nslookup, or Resolve-DnsName) and curl to check the result.
metadata:
  collection: vibe.md
  group: deploy
---

# Deploy: connect a custom domain

Read [the shared deploy contract](../DEPLOY.md) and
[the frontend track guide](../FRONTEND.md) first, and follow them. Changing a
domain is one of the four things that always need the user's yes. For the host's
own steps, read the "Custom domains" section of its guide:
[Vercel](../VERCEL.md), [Netlify](../NETLIFY.md),
[Cloudflare Pages](../CLOUDFLARE-PAGES.md), or
[GitHub Pages](../GITHUB-PAGES.md).

## Purpose

Point the user's own domain at their live site, with HTTPS, without breaking
anything else the domain is used for (email most of all). DNS mistakes are easy
to make and slow to undo, so this skill looks before it changes anything,
changes one thing at a time, and explains each step.

## When to Use

- The site is online at the host's address and the user wants their own domain.
- A domain was connected but shows an error, a certificate warning, or the old
  site.
- The user wants both `my-site.com` and `www.my-site.com` to work.
- Examples: "Connect my domain", "Use my own domain instead of vercel.app",
  "Point my GoDaddy domain to Netlify", "תחבר לי את הדומיין", "איך שמים דומיין
  משלי על האתר?".

Do not use this skill:

- before the site is online. Run `deploy-frontend-launch` first.
- to buy a domain. Buying costs money; explain where domains are bought and let
  the user do it themselves, then come back.
- to set up email for the domain. Only protect the existing email records.

## Prerequisites

- A site already live on a supported host.
- A domain the user owns, and access to where its DNS is managed (often the
  company they bought it from). The user logs in there themselves.

## Plain words to use

| Word | Plain meaning |
| --- | --- |
| DNS | The internet's address book: it tells browsers which computers a domain points to. |
| DNS record | One line in that address book. |
| `A` / `AAAA` record | Points a name at a numeric internet address (IPv4 / IPv6). |
| `CNAME` record | Points a name at another name, such as `my-site.netlify.app`. |
| `MX` record | Says where the domain's email goes. Do not touch it unless the user asks. |
| `TXT` record | A text note, often used to prove you own the domain. |
| Nameservers | The company that holds the domain's address book. Changing them moves all records at once. |
| Apex or bare domain | `my-site.com`, without `www`. |
| Propagation | The time it takes for DNS changes to reach everyone, from minutes to a day or two. |

## Instructions

1. **Confirm the basics.** Which domain, which host the site is on, and the
   address of the working site there. Ask whether the domain is already used
   for anything: email (very common), another site, or a service. Say plainly
   that this changes where the domain points, and that buying or renewing a
   domain is not part of this skill.

2. **Look before changing anything.** Run read-only lookups and keep the
   results (they are public information, so it is fine to show them):
   - who holds the records: `dig +short NS <domain>`
   - the current records for the bare domain and for `www`:
     `dig +short A <domain>`, `dig +short AAAA <domain>`,
     `dig +short CNAME www.<domain>`, `dig +short MX <domain>`,
     `dig +short TXT <domain>`.
   If `dig` is missing, use `nslookup -type=<TYPE> <name>`, or
   `Resolve-DnsName <name> -Type <TYPE>` on Windows. Tell the user what you see:
   where the DNS is managed, whether email is set up (MX records), and whether
   the domain already points somewhere.

3. **Choose the shape with the user.** Recommend that both `my-site.com` and
   `www.my-site.com` work, with one redirecting to the other (hosts set this up
   when both are added). Explain the two ways DNS can be done, using the
   platform guide:
   - **Add records at the current DNS provider** (usually safest: email and
     other records stay where they are).
   - **Move the nameservers to the host** (Netlify DNS, or Cloudflare, which
     requires it for a bare domain on Cloudflare Pages). This moves **all**
     records. Every existing record, especially MX and TXT, must be copied over
     first, or email stops. Recommend it only when the platform guide says it is
     needed or the user prefers it. Before a nameserver move:
     - `dig` cannot list every record (for example `mail.`, `_dmarc`, DKIM,
       SRV, or CAA records), so ask the user to open the full list of records in
       their current DNS provider's dashboard (many can export it), and compare
       it with what the new host imported before switching.
     - Check DNSSEC with `dig +short DS <domain>`. If it prints anything, the
       domain uses DNSSEC: the user must turn it off at the registrar and wait
       before moving nameservers, or the whole domain, email included, can stop
       working. It can be turned on again at the new provider afterwards.
     - Suggest lowering the records' TTL (how long others remember them) a day
       ahead, so a mistake can be undone faster.

4. **Check costs and plans live.** Adding a custom domain is free on many free
   plans, but not always, and some features cost extra. Read the host's current
   pages from its platform guide before saying it is free. Never buy, renew, or
   upgrade anything; if a step asks for payment, stop and tell the user.

5. **Add the domain on the host first.** Ask before doing it. Follow the
   platform guide (dashboard, or the host's documented command if the guide
   lists one). The host then shows the exact records it wants. Use those exact
   values; never use addresses from memory. On GitHub Pages, verify the domain
   in the user's GitHub settings **before** adding it to the repository, to stop
   others from claiming it.

6. **The user changes the DNS records.** Give numbered steps for their DNS
   provider: which record type, which name (`@` usually means the bare domain),
   which value, and what to remove if a conflicting old record exists. Ask
   before each change, and one change at a time. Never add a wildcard record
   (`*.my-site.com`) unless the user asks and the host's docs say it is safe.
   Never touch MX records. Before removing any old record, write down its value
   so it can be put back.

7. **Wait for DNS, and say so.** Re-run the lookups from step 2 until they show
   the new values. Explain that this can take from minutes to a day or two, and
   that different people may see the old and new site during that time. Do not
   keep changing records while waiting; a second change restarts the wait.

8. **Check HTTPS.** Hosts create the certificate (the padlock) by themselves
   once DNS points at them, which can take a little while. On GitHub Pages, turn
   on **Enforce HTTPS** when it becomes available. Check with
   `curl -sS -I https://<domain>` and `curl -sS -I https://www.<domain>`.

9. **Verify.** As in [DEPLOY.md](../DEPLOY.md), section 4: the domain loads the
   user's site over HTTPS with a success status, `www` and the bare domain both
   work (one may redirect to the other), `http://` redirects to `https://`, and
   a main inner page loads directly. If MX records existed, confirm with
   `dig +short MX <domain>` that they are unchanged. If the site uses an outside
   service that restricts which addresses may call it (for example Supabase or
   Firebase authentication redirect URLs, or a Stripe domain list), remind the
   user to add the new domain there too.

10. **When a domain is removed later**, or the site or project is deleted,
    remove or change the DNS records that point at the old host first. A record
    left pointing at a shared host address can let someone else take over the
    domain.

11. **Report.** The domain, what now points where, what was changed (and the old
    values, in case it needs undoing), HTTPS status, what you checked, and
    anything still waiting for DNS.

## Examples

**User:** "Connect my domain bakery-tlv.com to my Netlify site."

**Agent:** Looks up the domain: DNS at the registrar, MX records for Google
Workspace email, no website yet. Explains that keeping DNS at the registrar
protects the email. Gets a yes, and the user adds the domain in Netlify's Domain
management. Netlify shows the records; the agent gives the user numbered steps to
add them at the registrar, one at a time, with a yes for each. It re-checks with
`dig` until both names point at Netlify, confirms HTTPS on both, that the MX
records are unchanged, and that `/menu` loads directly, then reports.

**User:** "תחבר לי את הדומיין שלי לאתר ב-GitHub Pages"

**Agent:** Answers in Hebrew. Reads GitHub's current custom-domain page, gets a
yes, and has the user add the domain under Settings, Pages. Explains the four
`A` records for the bare domain and the `CNAME` for `www`, in the values from
GitHub's page, and asks before each change. Waits for DNS, turns on Enforce
HTTPS when offered, and reminds the user to set the site's base path back to `/`,
since the site now lives at the domain root.

**User:** "Buy me a domain and connect it."

**Agent:** Explains that buying a domain costs money and needs the user's own
payment, so the user buys it themselves, and offers to connect it afterwards.
