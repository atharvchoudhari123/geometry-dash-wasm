// Vercel serverless proxy for Geometry Dash online requests.
// Public route: /__proxy?url=<encoded Boomlings URL>
const ALLOWED_HOSTS = new Set(["www.boomlings.com", "boomlings.com"]);

module.exports = async function handler(req, res) {
  const origin = req.headers.origin;
  const host = req.headers.host;
  if (origin) {
    try {
      if (new URL(origin).host !== host) {
        res.status(403).send("forbidden");
        return;
      }
    } catch {
      res.status(403).send("forbidden");
      return;
    }
  }

  if (req.method !== "GET" && req.method !== "POST") {
    res.setHeader("Allow", "GET, POST");
    res.status(405).send("method not allowed");
    return;
  }

  let target;
  try {
    target = new URL(typeof req.query.url === "string" ? req.query.url : "");
  } catch {
    res.status(400).send("bad url");
    return;
  }

  if (!["http:", "https:"].includes(target.protocol) ||
      !ALLOWED_HOSTS.has(target.hostname) ||
      target.username || target.password) {
    res.status(403).send("host not allowed");
    return;
  }

  let body;
  if (req.method === "POST") {
    const chunks = [];
    for await (const chunk of req) chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
    body = Buffer.concat(chunks);
  }

  try {
    const upstream = await fetch(target.toString(), {
      method: req.method,
      headers: {
        "User-Agent": "",
        ...(body ? { "Content-Type": "application/x-www-form-urlencoded" } : {})
      },
      body,
      redirect: "follow"
    });

    const data = Buffer.from(await upstream.arrayBuffer());
    res.statusCode = upstream.status;
    res.setHeader("Content-Type", upstream.headers.get("content-type") || "text/plain");
    res.setHeader("Cache-Control", "no-store");
    res.setHeader("Content-Length", String(data.length));
    res.end(data);
  } catch (error) {
    res.status(502).send("upstream error");
  }
};

module.exports.config = { api: { bodyParser: false } };
