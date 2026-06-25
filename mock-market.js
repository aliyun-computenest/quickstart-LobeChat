const http = require('http');

const port = Number(process.env.MOCK_MARKET_PORT || 3999);

const emptyPage = (query = {}) => {
  const page = Number(query.page || 1);
  const pageSize = Number(query.pageSize || 20);

  return {
    currentPage: page,
    hasNextPage: false,
    hasPreviousPage: false,
    items: [],
    page,
    pageSize,
    total: 0,
    totalCount: 0,
    totalPages: 0,
  };
};

const sendJson = (res, status, body) => {
  res.writeHead(status, {
    'Access-Control-Allow-Origin': '*',
    'Cache-Control': 'no-store',
    'Content-Type': 'application/json; charset=utf-8',
  });
  res.end(JSON.stringify(body));
};

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || '127.0.0.1'}`);
  const query = Object.fromEntries(url.searchParams.entries());

  if (req.method === 'OPTIONS') return sendJson(res, 204, {});
  if (url.pathname === '/health') return sendJson(res, 200, { ok: true });

  if (url.pathname.startsWith('/api/v1/plugins')) {
    return sendJson(res, 200, emptyPage(query));
  }

  if (url.pathname.includes('/categories') || url.pathname.includes('/identifiers')) {
    return sendJson(res, 200, []);
  }

  if (url.pathname.startsWith('/api/v1/')) {
    return sendJson(res, 200, emptyPage(query));
  }

  return sendJson(res, 200, emptyPage(query));
});

server.listen(port, '127.0.0.1', () => {
  console.log(`[mock-market] listening on 127.0.0.1:${port}`);
});
