---
name: google-search-console
description: Gets a website into Google Search with Google Search Console. Verifies that the user owns the site (a DNS record for the whole domain, or a file or meta tag for one address), makes sure the site has a sitemap and a robots.txt that does not block Google, submits the sitemap, and explains "not indexed" reports in plain words with the smallest fix for each, such as a stray noindex tag, a wrong canonical link or a page that redirects. Asks before DNS changes and code changes. Use when the user says "my site isn't on Google", "add my site to Google Search Console", "submit my sitemap", "verify my domain with Google", "Discovered - currently not indexed", "Crawled - currently not indexed", "האתר שלי לא מופיע בגוגל", or "תגיש את ה-sitemap לגוגל". Not for paid ads, not for writing page titles and content to rank better, and not for connecting a domain to a host (use deploy-frontend-domain).
license: MIT
compatibility: Needs read and write access to the project, a Google account, and the site already online at its final address. Domain verification needs access to the domain's DNS settings. The user does the Search Console steps; the agent explains and checks.
metadata:
  collection: vibe.md
  group: google
---

# Google: Search Console, sitemap and indexing

Read [the shared google contract](../GOOGLE.md) first, and follow it.

## Purpose

Google finds most sites on its own, but slowly, and it does not say why a page
is missing unless you ask. Search Console is Google's free tool for site owners:
it proves you own the site, takes your list of pages (the sitemap), and reports
which pages are in Google and why others are not. This skill sets it up and
fixes the common reasons pages are left out.

## When to Use

- The site is online but does not show up in Google, or only some pages do.
- The user wants to verify their site with Google or submit a sitemap.
- Search Console shows "not indexed" reasons the user does not understand.
- Examples: "My site isn't on Google", "Add my site to Search Console", "Submit
  my sitemap", "Discovered - currently not indexed", "האתר שלי לא מופיע בגוגל",
  "תגיש את ה-sitemap לגוגל".

Do not use this skill:

- before the site is online at its final address. Use `deploy-frontend-launch`
  first.
- to connect a domain to a host. Use `deploy-frontend-domain`. This skill only
  adds a TXT record for verification, under the same DNS rules.
- to rewrite titles and content to rank higher, or for paid ads.

## Prerequisites

- The site is live at its final address with HTTPS.
- For domain verification: access to where the domain's DNS is managed (the
  registrar, Cloudflare, or the host).
- Search Console has no charge.

## Instructions

1. **Check the basics on the live site first.** Open, from the live address:
   - `/robots.txt`: it must not say `Disallow: /` for all user agents. It should
     list the sitemap (`Sitemap: https://my-site.com/sitemap.xml`).
   - `/sitemap.xml` (or what robots.txt names): it loads and lists the real
     pages with the live domain, not `localhost` or a preview address.
   - The home page's HTML: no `<meta name="robots" content="noindex">` and no
     `X-Robots-Tag: noindex` header (check with `curl -sI`). The
     `<link rel="canonical">` points at the page's own live address.
   Report what is missing in plain words.

2. **Add what is missing, with a yes.** Use the framework's own way:
   - Next.js App Router: `app/sitemap.ts` and `app/robots.ts`.
     Docs: <https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap>.
   - Astro: `@astrojs/sitemap`. Vite or plain sites: a generated
     `sitemap.xml` in the public folder.
   - Set the base address from one setting (for example `SITE_URL`), so
     previews never put their own address in the sitemap.
   Then ask separately before putting it live, since that changes the live
   site; with a yes, hand off to `deploy-frontend-update`, and recheck step 1.

3. **Choose how to verify.** Explain the two kinds of property:

   | Kind | Covers | Verify by | Pick when |
   | --- | --- | --- | --- |
   | **Domain** | every address under the domain (`www`, no `www`, `http`, `https`, subdomains) | a TXT record in DNS | the user owns the domain and can edit DNS. Recommended. |
   | **URL prefix** | only addresses starting with one exact prefix | an HTML file, a meta tag, or Google Analytics | no DNS access, or a site on a shared address such as `*.vercel.app` or `*.github.io` |

   Official guide: <https://support.google.com/webmasters/answer/34592>.

4. **Verify.** The user adds the property at
   <https://search.google.com/search-console> and Google shows the record, file
   or tag.
   - **Domain (TXT record):** follow `deploy-frontend-domain`'s rules: look at
     the current DNS first, add a record, never change or remove existing ones,
     and ask before the change. The user adds the TXT record at their DNS
     provider. Check it with `dig +short TXT my-site.com` (or
     `nslookup -type=TXT my-site.com`) until the `google-site-verification=`
     value appears. The value is not a secret. DNS can take minutes to hours.
   - **Meta tag:** with a yes, add it to the home page's `<head>` through the
     framework's metadata (in Next.js, `metadata.verification.google`). With a
     separate yes, deploy, and check the live HTML contains it.
   - **HTML file:** with a yes, put it in the public folder. With a separate
     yes, deploy, and open it at the live address.
   Then the user presses **Verify**. Ask them to read back the result.
   Leave the record, tag or file in place; removing it loses verification.

5. **Submit the sitemap.** In the property's **Sitemaps** page, the user enters
   the sitemap address. Ask them to read back the status. "Success" with a
   number of pages found is the goal; "Couldn't fetch" usually means the address
   is wrong, blocked in robots.txt, or not live yet.

6. **Explain the indexing report.** Ask the user to open **Pages** (page
   indexing) and read you the reasons with their counts, or use the **URL
   Inspection** tool on one address. Explain each reason and its fix:

   | Reason | Plain meaning | Usual fix |
   | --- | --- | --- |
   | Discovered - currently not indexed | Google knows the page but has not visited it yet | Wait; make sure it is in the sitemap and linked from other pages |
   | Crawled - currently not indexed | Google visited and chose not to add it for now | Often thin or duplicate content; improve the page, it is not a technical error |
   | Excluded by 'noindex' tag | The page asks not to be indexed | Remove the noindex if the page should be in Google |
   | Blocked by robots.txt | robots.txt forbids it | Change robots.txt |
   | Alternate page with proper canonical tag | Another address is the main one | Usually fine (for example `www` versus no `www`) |
   | Duplicate without user-selected canonical | Several addresses show the same page | Add a canonical link, redirect one address to the other |
   | Page with redirect | The address redirects | Fine for old addresses; list only final addresses in the sitemap |
   | Not found (404) | The address does not exist | Fix the link or the sitemap |
   | Server error (5xx) | The site failed when Google visited | `deploy-frontend-fix` |

   Docs: <https://support.google.com/webmasters/answer/7440203>.

7. **Ask for indexing only for important pages.** After a fix, the user can use
   URL Inspection and **Request indexing** for a few key pages. Explain that it
   asks Google to visit, and does not promise the page will be added or how
   fast. Indexing usually takes days.

8. **Report** what is verified, the sitemap status, the fixes made, and what
   the user should check again in a week.

## Examples

**User:** "My site bakery-tlv.com isn't on Google."

**Agent:** Checks the live site: robots.txt is fine, but there is no sitemap and
the home page has a `noindex` tag left over from a template. With a yes, removes
it, adds `app/sitemap.ts` and `app/robots.ts`, and hands off to
`deploy-frontend-update`. Then helps the user add a Domain property, and, under
the DNS rules, a TXT record; checks it with `dig` until it appears. The user
verifies and submits the sitemap, and reads back "Success, 12 pages".

**User:** "האתר שלי לא מופיע בגוגל, הוא על vercel.app"

**Agent:** Answers in Hebrew. Explains a Domain property is not possible on a
shared `vercel.app` address, and uses a URL prefix property with the meta tag.
Adds the tag after a yes, deploys, checks the live HTML, and the user verifies.

**User:** "Search Console says 'Crawled - currently not indexed' for my blog
posts."

**Agent:** Explains this is Google's choice, not a technical error. Uses URL
Inspection on one post with the user to rule out noindex and canonical
problems, then suggests what makes the posts more useful to readers.
