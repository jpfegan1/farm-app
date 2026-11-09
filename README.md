# Farm App

Farm records web app for an Irish dairy/beef farm: paddock map, herd, milk, breeding & calving, grass planner, photos, tasks and compliance record-keeping (a record-keeping aid, not an official register).

* Static single-page app (`index.html`), hosted on GitHub Pages.
* Accounts and data: Supabase (email + password auth, Postgres with row-level security so each user only sees their own rows, private Storage bucket `photos` with one folder per user).
* Works with poor signal: per-user local cache + queued writes that sync when back online; `sw.js` caches the app shell for offline start.
* The key in `index.html` is Supabase's *publishable* key, which is designed to be public; data access is enforced by RLS policies.
