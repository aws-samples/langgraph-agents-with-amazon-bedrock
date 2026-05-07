# LangGraph Agents with Amazon Bedrock

This repository contains a workshop adapted from the course [AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) 
created by [Harrison Chase](https://www.linkedin.com/in/harrison-chase-961287118) (Co-Founder and CEO of [LangChain](https://www.langchain.com/)) and [Rotem Weiss](https://www.linkedin.com/in/rotem-weiss) (Co-founder and CEO of [Tavily](https://tavily.com/)), and hosted on [DeepLearning.AI](https://www.deeplearning.ai/).
The original content is used with the consent of the authors.

This workshop is also available in AWS Workshop Studio [here](https://catalog.us-east-1.prod.workshops.aws/workshops/9bc28f51-d7c3-468b-ba41-72667f3273f1/en-US).

Make sure to read and follow this README before you go through the material to ensure a smooth experience.

## Outline

The workshop:
- explores the latest advancements in AI agents and agentic workflows, leveraging improvements in function calling LLMs and specialized tools like agentic search
- utilizes LangChain's updated support for agentic workflows and introduces LangGraph, an extension for building complex agent behaviors
- provides insights into key design patterns in agentic workflows including *planning, tool use, reflection, multi-agent communication, memory*

The material is divided in six Jupyter Notebooks Labs that will help you understand the LangGraph framework, its underlying concepts, and how to use it with Amazon Bedrock:

- Lab 1: [Building a ReAct Agent from Scratch](Lab_1/)
    - Build a basic ReAct agent from scratch using Python and an LLM, implementing a loop of reasoning and acting to solve tasks through tool usage and observation
- Lab 2: [LangGraph Components](Lab_2/)
    - Introduction to LangGraph, a tool for implementing agents with cyclic graphs, demonstrating how to create a more structured and controllable agent using components like nodes, edges, and state management
- Lab 3: [Agentic Search Tools](Lab_3/)
    - Introduction to Agentic search tools, enhancing AI agents' capabilities by providing structured, relevant data from dynamic sources, improving accuracy and reducing hallucinations
- Lab 4: [Persistence and Streaming](Lab_4/)
    - Persistence and streaming are crucial for long-running agent tasks, enabling state preservation, resumption of conversations, and real-time visibility into agent actions and outputs
- Lab 5: [Human in the Loop](Lab_5/)
    - Advanced human-in-the-loop interaction patterns in LangGraph, including adding breaks, modifying states, time travel, and manual state updates for better control and interaction with AI agents
- Lab 6: [Essay Writer](Lab_6/)
    - Build an AI essay writer using a multi-step process involving planning, research, writing, reflection, and revision, implemented as a graph of interconnected agents

If this is your first time working with LangGraph, we recommend to refer to the [original course](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) for detailed video explanations.

## Models used

The labs call two Anthropic models on Amazon Bedrock via **US geographic cross-region inference (CRIS)** profiles:

- **Claude Haiku 4.5** — `us.anthropic.claude-haiku-4-5-20251001-v1:0` — used as the default across Labs 2, 4, 5, and 6.
- **Claude Sonnet 4.6** — `us.anthropic.claude-sonnet-4-6` — used in Lab 1 and as the "upgrade" model demonstrated in Lab 2.

CRIS routes requests within the US geography for higher throughput and resilience. When called from `us-east-1`, `us-east-2`, or `us-west-2`, Bedrock may route to any of those three Regions. You must enable model access for **both models** in **all three Regions** the profile can route to, otherwise invocations will fail with an access-denied error when a request happens to land on a Region where the model isn't enabled for your account.

## Where LangGraph fits among AWS agent options

LangGraph is one of several ways to build agents on AWS. This workshop focuses on LangGraph because of its flexible graph-based control flow, but it's worth knowing where it sits relative to the AWS-native options:

- **[Strands Agents](https://strandsagents.com/)** — an AWS-released open-source SDK that takes a model-first approach: you give it a prompt and a list of tools, and the model decides how to plan and call them. Strands is a lighter-weight alternative to LangGraph for agents that don't need explicit graph control flow. Both work well on Bedrock.
- **[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)** — a fully managed, **framework-agnostic** runtime for deploying agents built with *any* framework (LangGraph, Strands, CrewAI, LlamaIndex, ...). AgentCore provides serverless hosting, session isolation, long-lived memory, a tool gateway, and observability, without replacing your framework choice. A natural production target for anything you build in this workshop.
- **[Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/)** — the highest-abstraction option: a fully managed agent service where you declare action groups, knowledge bases, and optional guardrails, and AWS handles the orchestration. Best when you want the least code and don't need custom control flow.

In short: use LangGraph (or Strands) when you want the most control over agent behavior, AgentCore when you need to deploy and operate any of them at scale, and Bedrock Agents when a fully-managed, configuration-driven agent is enough.

Let's get started with the setup of the environment.

## Setup your virtual environment

These instructions are meant to be used locally with [AWS authentication](https://docs.aws.amazon.com/cli/v1/userguide/cli-authentication-short-term.html), as well as within an [Amazon SageMaker JupyterLab](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated-jl.html) or [Amazon SageMaker Code Editor](https://docs.aws.amazon.com/sagemaker/latest/dg/code-editor.html) instance.

The workshop requires `Python >=3.10` (Python 3.13 recommended) and uses [`uv`](https://docs.astral.sh/uv/) for environment and dependency management.

### 1. Download the repository

```
git clone https://github.com/aws-samples/langgraph-agents-with-amazon-bedrock.git
cd langgraph-agents-with-amazon-bedrock
```

### 2. Install OS dependencies

The notebooks render graph diagrams via [`pygraphviz`](https://pygraphviz.github.io/), which needs the `graphviz` system library.

- **macOS:** `brew install graphviz`
- **Ubuntu/Debian:** `sudo apt-get update && sudo apt-get install -y graphviz graphviz-dev`
- **Other:** see [the pygraphviz install guide](https://pygraphviz.github.io/documentation/stable/install.html).

### 3. Install `uv`

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Other installation options are documented [here](https://docs.astral.sh/uv/getting-started/installation/).

### 4. Create the virtual environment and install dependencies

From the repo root:

```
uv sync
```

`uv` will read `pyproject.toml` and `uv.lock`, install a pinned Python 3.13 interpreter if needed, create `.venv/` in the repo root, and install all dependencies.

> **macOS note:** if `pygraphviz` fails to build and you installed `graphviz` via Homebrew, prefix the command with the include/lib paths:
> ```
> CFLAGS="-I$(brew --prefix graphviz)/include" LDFLAGS="-L$(brew --prefix graphviz)/lib" uv sync
> ```

### 5. Register the Jupyter kernel

The new Python environment needs to be registered so that Jupyter can select it:

```
uv run python -m ipykernel install --user --name agents-dev-env
```

The kernel may not appear right away in the kernel picker — refresh the list if needed.

### 6. Create and set your Tavily API key

Head over to https://app.tavily.com/home and create a free API key.

### 7. Setup the local environment variables

Create a personal copy of the temporary environment file [env.tmp](env.tmp) with the name `.env`, which is already listed in [.gitignore](.gitignore) to avoid committing personal information.

```
cp env.tmp .env
```

You can edit the preferred region inside `.env` if needed. The default is `us-east-1`, which is one of the supported source regions for the US cross-region inference profiles used by this workshop.

### 8. Store the Tavily API key

You have two options to store the Tavily API key:

1. Copy the Tavily API key inside the `.env` file. This option is always checked first.

2. [Create a new secret in AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/create_secret.html) with the name `TAVILY_API_KEY`, retrieve the secret `arn` by clicking on it, and [add an inline policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html#add-policies-console) with [permission to read the secret](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access_examples.html#auth-and-access_examples_read) to your [SageMaker execution role](https://docs.aws.amazon.com/sagemaker/latest/dg/domain-user-profile-view-describe.html) — replace the copied `arn` in the example below.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "secretsmanager:GetSecretValue",
            "Resource": "arn:aws:secretsmanager:<Region>:<AccountId>:secret:SecretName-6RandomCharacters"
        }
    ]
}
```

You are all set! Make sure to select the freshly created `agents-dev-env` kernel for each notebook.

## Running without a Tavily key

If you don't want to create a Tavily account, the workshop has a built-in DuckDuckGo fallback for the subset of labs where the agent just needs *some* web search tool.

| Lab | Runs without Tavily? | Notes |
|-----|----------------------|-------|
| 1 — ReAct from scratch | Yes | Doesn't use Tavily. |
| 2 — LangGraph components | Yes, with a one-line edit | Replace `tool = TavilySearch(max_results=4)` with `tool = utils.get_search_tool(max_results=4)`. |
| 3 — Agentic search tools | No | The whole point of the lab is comparing Tavily's structured agentic results against a plain DuckDuckGo search. |
| 4 — Persistence & streaming | Yes, with a one-line edit | Same swap as Lab 2. |
| 5 — Human in the loop | Yes, with a one-line edit | Same swap as Lab 2. Note: the hardcoded tool-call name strings assume Tavily's tool name `tavily_search`; if you use the fallback, change them to `duckduckgo_results_json`. |
| 6 — Essay writer | No | Uses `TavilyClient.search()` directly and relies on Tavily's structured results. |

`utils.get_search_tool()` returns a Tavily-backed tool if `TAVILY_API_KEY` is set (in `.env` or Secrets Manager) and a DuckDuckGo-backed tool otherwise. Both are LangChain `BaseTool` instances and can be wired into a LangGraph agent identically.

# Additional resources

- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [Strands Agents](https://strandsagents.com/) — open-source, model-first agents SDK
- [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) — framework-agnostic managed runtime for agents
- [Amazon Bedrock Agents](https://aws.amazon.com/bedrock/agents/) — fully managed, configuration-driven agents
- [LangChain documentation](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph GitHub repository](https://github.com/langchain-ai/langgraph)
- [LangSmith Prompt hub](https://smith.langchain.com/hub)

