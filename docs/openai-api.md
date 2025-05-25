Open AI Responses API and MCP

24.46 KB •438 lines
•
Formatting may be inconsistent from source

New tools and features in the Responses API
Introducing remote MCP server support, image generation, Code Interpreter, and more in the Responses API for developers and enterprises.


Listen to article
7:04
Share
Today, we’re adding new built-in tools to the Responses API—our core API primitive for building agentic applications. This includes support for all remote Model Context Protocol (MCP) servers⁠(opens in a new window), as well as tools like image generation⁠(opens in a new window), Code Interpreter⁠(opens in a new window), and improvements to file search⁠(opens in a new window). These tools are available across our GPT‑4o series, GPT‑4.1 series, and OpenAI o-series reasoning models. o3 and o4-mini can now call tools and functions directly within their chain-of-thought in the Responses API, producing answers that are more contextually rich and relevant. Using o3 and o4-mini with the Responses API preserves reasoning tokens across requests and tool calls, improving model intelligence and reducing the cost and latency for developers.

We’re also introducing new features in the Responses API that improve reliability, visibility, and privacy for enterprises and developers. These include background mode⁠(opens in a new window) to handle long-running tasks asynchronously and more reliably, support for reasoning summaries⁠(opens in a new window), and support for encrypted reasoning items⁠(opens in a new window). 

Since releasing the Responses API in March 2025 with tools like web search, file search, and computer use, hundreds of thousands of developers have used the API to process trillions of tokens across our models. Customers have used the API to build a variety of agentic applications, including Zencoder⁠(opens in a new window)’s coding agent, Revi⁠(opens in a new window)’s market intelligence agent for private equity and investment banking, and MagicSchool AI⁠(opens in a new window)'s education assistant—all of which use web search to pull relevant, up-to-date information into their app. Now developers can build agents that are even more useful and reliable with access to the new tools and features released today.

New remote MCP server support
We’re adding support for remote MCP servers⁠(opens in a new window) in the Responses API, building on the release of MCP support in the Agents SDK⁠(opens in a new window). MCP is an open protocol that standardizes how applications provide context to LLMs. By supporting MCP servers in the Responses API, developers will be able to connect our models to tools hosted on any MCP server with just a few lines of code. Here are some examples showing how developers can use remote MCP servers with the Responses API today:

Shopify
Twilio
Stripe
DeepWiki (Devin)
Python

1
response = client.responses.create(
2
  model="gpt-4.1",
3
  tools=[{
4
    "type": "mcp",
5
    "server_label": "shopify",
6
    "server_url": "https://pitchskin.com/api/mcp",
7
  }],
8
  input="Add the Blemish Toner Pads to my cart"
9
)
The Blemish Toner Pads have been added to your cart! You can proceed to checkout here:


Pitch. Skin checkout page showing express options (Shop Pay, PayPal, G Pay), contact and delivery form fields, and an order summary for one ‘Blemish Toner Pads 200 mL (120 pads)’ priced at AUD $49.
Python

1
response = client.responses.create(
2
  model="gpt-4o",
3
  tools=[
4
    { "type": "web_search_preview" },
5
    {
6
      "type": "mcp",
7
      "server_label": "twilio",
8
      "server_url": "https://<function-domain>.twil.io/mcp",
9
      "headers": { "x-twilio-signature": "..." }
10
    }
11
  ],
12
  input="Get the latest soccer news and text a short summary to +1 555 555 5555"
13
)
I found the latest soccer news, summarized it, and texted the update to +1 555 555 5555.


iPhone Messages chat titled ‘Soccer News’ showing a single grey bubble with headlines: ‘Transfers open; Spurs eye first trophy in Europa League; Bayern may sell Boey; Reus rescues LA Galaxy in El Tráfico draw.
Python

1
response = client.responses.create(
2
  model="o3",
3
  tools=[
4
    {
5
      "type": "mcp",
6
      "server_label": "stripe",
7
      "server_url": "https://mcp.stripe.com",
8
      "headers": { "Authorization": "Bearer <api-key>" }
9
    }
10
  ],
11
  input="user_291471 used 700 minutes of storage at $0.30/minute. Generate a payment link for this."
12
)
Here is the payment link for user_29471's storage usage (700 minutes at $0.30/min, total $210). You can share this link with the user for payment.


Hypernian checkout: $210 storage charge with Link, card, or Cash App Pay options and a ‘Pay’ button.
Python

1
response = client.responses.create(
2
  model="gpt-4.1-mini",
3
  tools=[{
4
    "type": "mcp",
5
    "server_label": "deepwiki",
6
    "server_url": "https://mcp.deepwiki.com/mcp"
7
  }],
8
  input="give me 5 interesting facts on modelcontextprotocol/python-sdk -- keep it short!" 
9
)
Here are 5 interesting facts about the modelcontextprotocol/python-sdk:

1. The MCP SDK implements a standardized client-server architecture for exposing context to Large Language Models (LLMs) using well-defined protocols and transports like SSE, WebSocket, and STDIO.

2. It provides two main server implementations: FastMCP (high-level with decorator-based API) and a low-level Server for complete protocol control.

3. MCP defines three core primitives: Resources (data exposure), Tools (functions), and Prompts (interactive templates).

4. The SDK includes automatic function metadata extraction and validation using Pydantic models, ensuring robust and strongly typed function calls.

5. During initialization, MCP servers declare capabilities like resource subscription and prompt management, enabling clients to adapt dynamically for security and feature negotiation.


Popular remote MCP servers include Cloudflare⁠(opens in a new window), HubSpot⁠(opens in a new window), Intercom⁠(opens in a new window), PayPal⁠(opens in a new window), Plaid⁠(opens in a new window), Shopify⁠(opens in a new window), Stripe⁠(opens in a new window), Square⁠(opens in a new window), Twilio⁠(opens in a new window), Zapier⁠(opens in a new window), and more. We expect the ecosystem of remote MCP servers to grow quickly in the coming months, making it easier for developers to build powerful agents that can connect to the tools and data sources their users already rely on. In order to best support the ecosystem and contribute to this developing standard, OpenAI has also joined the steering committee for MCP.

To learn how to spin up your own remote MCP server, check out this guide from Cloudflare⁠(opens in a new window). To learn how to use the MCP tool in the Responses API, check out this guide⁠(opens in a new window) in our API Cookbook.

Updates to image generation, Code Interpreter, and file search
With built-in tools in the Responses API, developers can easily create more capable agents with just a single API call. By calling multiple tools while reasoning, models now achieve significantly higher tool calling performance on industry-standard benchmarks like Humanity’s Last Exam (source). Today, we’re adding new tools including:

Image generation: In addition to using the Images API⁠(opens in a new window), developers can now access our latest image generation model—gpt-image-1—as a tool within the Responses API. This tool supports real-time streaming—allowing developers to see previews of the image as it’s being generated—and multi-turn edits—allowing developers to prompt the model to granularly refine these images step-by-step. Learn more⁠(opens in a new window).
Code Interpreter: Developers can now use the Code Interpreter⁠(opens in a new window) tool within the Responses API. This tool is useful for data analysis, solving complex math and coding problems, and helping the models deeply understand and manipulate images (e.g., thinking with images). The ability for models like o3 and o4-mini to use the Code Interpreter tool within their chain-of-thought has resulted in improved performance across several benchmarks including Humanity’s Last Exam (source). Learn more⁠(opens in a new window).
File search: Developers can now access the file search⁠(opens in a new window) tool in our reasoning models. File search enables developers to pull relevant chunks of their documents into the model’s context based on the user query. We’re also introducing updates to the file search tool that allow developers to perform searches across multiple vector stores and support attribute filtering with arrays. Learn more⁠(opens in a new window).


New features in the Responses API
In addition to the new tools, we’re also adding support for new features in the Responses API, including:

Background mode: As seen in agentic products like Codex, deep research, and Operator, reasoning models can take several minutes to solve complex problems. Developers can now use background mode to build similar experiences on models like o3 without worrying about timeouts or other connectivity issues—background mode kicks off these tasks asynchronously. Developers can either poll these objects to check for completion, or start streaming events whenever their application needs to catch up on the latest state. Learn more⁠(opens in a new window).
Python

1
response = client.responses.create(
2
  model="o3",
3
  input="Write me an extremely long story.",
4
  reasoning={ "effort": "high" },
5
  background=True
6
)
Reasoning summaries: The Responses API can now generate concise, natural-language summaries of the model’s internal chain-of-thought, similar to what you see in ChatGPT. This makes it easier for developers to debug, audit, and build better end-user experiences. Reasoning summaries are available at no additional cost. Learn more⁠(opens in a new window).
Python

1
response = client.responses.create(
2
    model="o4-mini",
3
    tools=[
4
        {
5
            "type": "code_interpreter",
6
            "container": {"type": "auto"}
7
        }
8
    ],
9
    instructions=(
10
        "You are a personal math tutor. "
11
        "When asked a math question, run code to answer the question."
12
    ),
13
    input="I need to solve the equation `3x + 11 = 14`. Can you help me?",
14
    reasoning={"summary": "auto"}
15
)
Encrypted reasoning items: Customers eligible for Zero Data Retention (ZDR)⁠(opens in a new window) can now reuse reasoning items across API requests—without any reasoning items being stored on OpenAI’s servers. For models like o3 and o4-mini, reusing reasoning items between function calls boosts intelligence, reduces token usage, and increases cache hit rates, resulting in lower costs and latency. Learn more⁠(opens in a new window).
Python

1
response = client.responses.create(
2
  model="o3",
3
  input="Implement a simple web server in Rust from scratch.",
4
  store=False,
5
  include=["reasoning.encrypted_content"]
6
)
Pricing and availability
All of these tools and features are now available in the Responses API, supported in our GPT‑4o series, GPT‑4.1 series, and our OpenAI o-series reasoning models (o1, o3, o3‑mini, and o4-mini). Image generation is only supported on o3 of our reasoning model series. 

Pricing for existing tools remains the same. Image generation costs $5.00/1M text input tokens, $10.00 / 1M image input tokens, and $40.00 / 1M image output tokens, with 75% off cached input tokens. Code Interpreter costs $0.03 per container. File search costs $0.10/GB of vector storage per day and $2.50/1k tool calls. There is no additional cost to call the remote MCP server tool—you are simply billed for output tokens from the API. Learn more about pricing⁠(opens in a new window) in our docs. 

We’re excited to see what you build!

Remote MCP
Allow models to use remote MCP servers to perform tasks.
Model Context Protocol (MCP) is an open protocol that standardizes how applications provide tools and context to LLMs. The MCP tool in the Responses API allows developers to give the model access to tools hosted on Remote MCP servers. These are MCP servers maintained by developers and organizations across the internet that expose these tools to MCP clients, like the Responses API.

Calling a remote MCP server with the Responses API is straightforward. For example, here's how you can use the DeepWiki MCP server to ask questions about nearly any public GitHub repository.

A Responses API request with MCP tools enabled
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-4.1",
    tools=[
        {
            "type": "mcp",
            "server_label": "deepwiki",
            "server_url": "https://mcp.deepwiki.com/mcp",
            "require_approval": "never",
        },
    ],
    input="What transport protocols are supported in the 2025-03-26 version of the MCP spec?",
)

print(resp.output_text)
It is very important that developers trust any remote MCP server they use with the Responses API. A malicious server can exfiltrate sensitive data from anything that enters the model's context. Carefully review the Risks and Safety section below before using this tool.

The MCP ecosystem
We are still in the early days of the MCP ecosystem. Some popular remote MCP servers today include Cloudflare, Hubspot, Intercom, Paypal, Pipedream, Plaid, Shopify, Stripe, Square, Twilio and Zapier. We expect many more servers—and registries making it easy to discover these servers—to launch in the coming months. The MCP protocol itself is also early, and we expect to add many more updates to our MCP tool as the protocol evolves.

How it works
The MCP tool works only in the Responses API, and is available across all our new models (gpt-4o, gpt-4.1, and our reasoning models). When you're using the MCP tool, you only pay for tokens used when importing tool definitions or making tool calls—there are no additional fees involved.

Step 1: Getting the list of tools from the MCP server
The first thing the Responses API does when you attach a remote MCP server to the tools array, is attempt to get a list of tools from the server. The Responses API supports remote MCP servers that support either the Streamable HTTP or the HTTP/SSE transport protocol.

If successful in retrieving the list of tools, a new mcp_list_tools output item will be visible in the Response object that is created for each MCP server. The tools property of this object will show the tools that were successfully imported.

{
  "id": "mcpl_682d4379df088191886b70f4ec39f90403937d5f622d7a90",
  "type": "mcp_list_tools",
  "server_label": "deepwiki",
  "tools": [
    {
      "name": "read_wiki_structure",
      "input_schema": {
        "type": "object",
        "properties": {
          "repoName": {
            "type": "string",
            "description": "GitHub repository: owner/repo (e.g. \"facebook/react\")"
          }
        },
        "required": [
          "repoName"
        ],
        "additionalProperties": false,
        "annotations": null,
        "description": "",
        "$schema": "http://json-schema.org/draft-07/schema#"
      }
    },
    // ... other tools
  ]
}
As long as the mcp_list_tools item is present in the context of the model, we will not attempt to pull a refreshed list of tools from an MCP server. We recommend you keep this item in the model's context as part of every conversation or workflow execution to optimize for latency.

Filtering tools
Some MCP servers can have dozens of tools, and exposing many tools to the model can result in high cost and latency. If you're only interested in a subset of tools an MCP server exposes, you can use the allowed_tools parameter to only import those tools.

Constrain allowed tools
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-4.1",
    tools=[{
        "type": "mcp",
        "server_label": "deepwiki",
        "server_url": "https://mcp.deepwiki.com/mcp",
        "require_approval": "never",
        "allowed_tools": ["ask_question"],
    }],
    input="What transport protocols does the 2025-03-26 version of the MCP spec (modelcontextprotocol/modelcontextprotocol) support?",
)

print(resp.output_text)
Step 2: Calling tools
Once the model has access to these tool definitions, it may choose to call them depending on what's in the model's context. When the model decides to call an MCP tool, we make an request to the remote MCP server to call the tool, take it's output and put that into the model's context. This creates an mcp_call item which looks like this:

{
  "id": "mcp_682d437d90a88191bf88cd03aae0c3e503937d5f622d7a90",
  "type": "mcp_call",
  "approval_request_id": null,
  "arguments": "{\"repoName\":\"modelcontextprotocol/modelcontextprotocol\",\"question\":\"What transport protocols does the 2025-03-26 version of the MCP spec support?\"}",
  "error": null,
  "name": "ask_question",
  "output": "The 2025-03-26 version of the Model Context Protocol (MCP) specification supports two standard transport mechanisms: `stdio` and `Streamable HTTP` ...",
  "server_label": "deepwiki"
}
As you can see, this includes both the arguments the model decided to use for this tool call, and the output that the remote MCP server returned. All models can choose to make multiple (MCP) tool calls in the Responses API, and so, you may see several of these items generated in a single Response API request.

Failed tool calls will populate the error field of this item with MCP protocol errors, MCP tool execution errors, or general connectivity errors. The MCP errors are documented in the MCP spec here.

Approvals
By default, OpenAI will request your approval before any data is shared with a remote MCP server. Approvals help you maintain control and visibility over what data is being sent to an MCP server. We highly recommend that you carefully review (and optionally, log) all data being shared with a remote MCP server. A request for an approval to make an MCP tool call creates a mcp_approval_request item in the Response's output that looks like this:

{
  "id": "mcpr_682d498e3bd4819196a0ce1664f8e77b04ad1e533afccbfa",
  "type": "mcp_approval_request",
  "arguments": "{\"repoName\":\"modelcontextprotocol/modelcontextprotocol\",\"question\":\"What transport protocols are supported in the 2025-03-26 version of the MCP spec?\"}",
  "name": "ask_question",
  "server_label": "deepwiki"
}
You can then respond to this by creating a new Response object and appending an mcp_approval_response item to it.

Approving the use of tools in an API request
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-4.1",
    tools=[{
        "type": "mcp",
        "server_label": "deepwiki",
        "server_url": "https://mcp.deepwiki.com/mcp",
    }],
    previous_response_id="resp_682d498bdefc81918b4a6aa477bfafd904ad1e533afccbfa",
    input=[{
        "type": "mcp_approval_response",
        "approve": True,
        "approval_request_id": "mcpr_682d498e3bd4819196a0ce1664f8e77b04ad1e533afccbfa"
    }],
)

print(resp.output_text)
Here we're using the previous_response_id parameter to chain this new Response, with the previous Response that generated the approval request. But you can also pass back the outputs from one response, as inputs into another for maximum control over what enter's the model's context.

If and when you feel comfortable trusting a remote MCP server, you can choose to skip the approvals for reduced latency. To do this, you can set the require_approval parameter of the MCP tool to an object listing just the tools you'd like to skip approvals for like shown below, or set it to the value 'never' to skip approvals for all tools in that remote MCP server.

Never require approval for some tools
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-4.1",
    tools=[
        {
            "type": "mcp",
            "server_label": "deepwiki",
            "server_url": "https://mcp.deepwiki.com/mcp",
            "require_approval": {
                "never": {
                    "tool_names": ["ask_question", "read_wiki_structure"]
                }
            }
        },
    ],
    input="What transport protocols does the 2025-03-26 version of the MCP spec (modelcontextprotocol/modelcontextprotocol) support?",
)

print(resp.output_text)
Authentication
Unlike the DeepWiki MCP server, most other MCP servers require authentication. The MCP tool in the Responses API gives you the ability to flexibly specify headers that should be included in any request made to a remote MCP server. These headers can be used to share API keys, oAuth access tokens, or any other authentication scheme the remote MCP server implements.

The most common header used by remote MCP servers is the Authorization header. This is what passing this header looks like:

Use Stripe MCP tool
from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-4.1",
    input="Create a payment link for $20",
    tools=[
        {
            "type": "mcp",
            "server_label": "stripe",
            "server_url": "https://mcp.stripe.com",
            "headers": {
                "Authorization": "Bearer $STRIPE_API_KEY"
            }
        }
    ]
)

print(resp.output_text)
To prevent the leakage of sensitive keys, the Responses API does not store the values of any string you provide in the headers object. These values will also not be visible in the Response object created. Additionally, because some remote MCP servers generate authenticated URLs, we also discard the path portion of the server_url in our responses (i.e. example.com/mcp becomes example.com). Because of this, you must send the full path of the MCP server_url and any relevant headers in every Responses API creation request you make.

Risks and safety
The MCP tool permits you to connect OpenAI to services that have not been verified by OpenAI and allows OpenAI to access, send and receive data, and take action in these services. All MCP servers are third-party services that are subject to their own terms and conditions.

If you come across a malicious MCP server, please report it to security@openai.com.

Connecting to trusted servers
Pick official servers hosted by the service providers themselves (e.g. we recommend connecting to the Stripe server hosted by Stripe themselves on mcp.stripe.com, instead of a Stripe MCP server hosted by a third party). Because there aren't too many official remote MCP servers today, you may be tempted to use a MCP server hosted by an organization that doesn't operate that server and simply proxies request to that service via your API. If you must do this, be extra careful in doing your due diligence on these "aggregators", and carefully review how they use your data.

Log and review data being shared with third party MCP servers.
Because MCP servers define their own tool definitions, they may request for data that you may not always be comfortable sharing with the host of that MCP server. Because of this, the MCP tool in the Responses API defaults to requiring approvals of each MCP tool call being made. When developing your application, review the type of data being shared with these MCP servers carefully and robustly. Once you gain confidence in your trust of this MCP server, you can skip these approvals for more performant execution.

We also recommend logging any data sent to MCP servers. If you're using the Responses API with store=true, these data are already logged via the API for 30 days unless Zero Data Retention is enabled for your organization. You may also want to log these data in your own systems and perform periodic reviews on this to ensure data is being shared per your expectations.

Malicious MCP servers may include hidden instructions (prompt injections) designed to make OpenAI models behave unexpectedly. While OpenAI has implemented built-in safeguards to help detect and block these threats, it's essential to carefully review inputs and outputs, and ensure connections are established only with trusted servers.

MCP servers may update tool behavior unexpectedly, potentially leading to unintended or malicious behavior.

Implications on Zero Data Retention and Data Residency
The MCP tool is compatible with Zero Data Retention and Data Residency, but it's important to note that MCP servers are third-party services, and data sent to an MCP server is subject to their data retention and data residency policies.

In other words, if you're an organization with Data Residency in Europe, OpenAI will limit inference and storage of Customer Content to take place in Europe up until the point communication or data is sent to the MCP server. It is your responsibility to ensure that the MCP server also adheres to any Zero Data Retention or Data Residency requirements you may have. Learn more about Zero Data Retention and Data Residency here.