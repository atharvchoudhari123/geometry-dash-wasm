# Deployment

This branch adds deployment configuration for Replit, Heroku, and Vercel.
The original GitHub Pages branch is unchanged.

## Replit

1. Import this GitHub repository and select the `deploy-ready` branch.
2. Run `python3 server.py` for development.
3. Use Replit Deployments to publish the app. The `.replit` deployment configuration runs the Python server.

The server reads the `PORT` environment variable and binds to `0.0.0.0`.

## Heroku

This project uses only the Python standard library; no third-party packages are required.

1. Create a Heroku app and connect this repository.
2. Select the `deploy-ready` branch.
3. Deploy. Heroku uses the included `Procfile`:
   `web: python server.py $PORT`.

The Python server provides both the static game files and the same-origin `/__proxy` endpoint used by the account features.

## Vercel

1. Import this GitHub repository into Vercel.
2. Select the `deploy-ready` branch.
3. Leave the project root at the repository root. No build command is needed.
4. Deploy.

Static game files are served by Vercel. The `api/proxy.py` function handles `/__proxy` GET/POST requests through the rewrite in `vercel.json`.

## Important notes

- This is a WebAssembly game and downloads large game assets in the browser. First load can take a while.
- Keep `gd_assets.js`, `gd_assets.json`, the asset chunks, and the `payload/` directory together. Do not deploy only `index.html`.
- The proxy only allows requests to `boomlings.com` and `www.boomlings.com`.
- The Vercel function has a 30-second maximum duration. If the upstream Geometry Dash service takes longer, the request may time out.
- The online/account endpoints depend on the upstream Geometry Dash services being available. Hosting configuration cannot guarantee those services will accept requests.
