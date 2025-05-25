Remote server
Public preview
Stripe also hosts a remote MCP server, available at https://mcp.stripe.com. To interact with the remote server, you need to pass your Stripe API key as a bearer token in the request header. We recommend using restricted API keys to limit access to the functionality your agent requires.

Command Line



curl https://mcp.stripe.com/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <apikey>" \
  -d '{
      "jsonrpc": "2.0",
      "method": "tools/call",
      "params": {
        "name": "create_customer",
        "arguments": {"name": "Jenny Rosen", "email": "jenny.rosen@example.com" }
      },
      "id": 1
  }'
This remote server currently only supports bearer token authentication. To avoid phising attacks verify you only use trusted MCP clients and double check the URL used is the official https://mcp.stripe.com server.