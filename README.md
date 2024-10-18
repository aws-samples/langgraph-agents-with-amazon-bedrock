# LangGraph Agents with Amazon Bedrock

This repository contains a workshop adapted from the course [AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) 
created by [Harrison Chase](https://www.linkedin.com/in/harrison-chase-961287118) (Co-Founder and CEO of [LangChain](https://www.langchain.com/)) and [Rotem Weiss](https://www.linkedin.com/in/rotem-weiss) (Co-founder and CEO of [Tavily](https://tavily.com/)), and hosted on [DeepLearning.AI](https://www.deeplearning.ai/).
The original content is used with the consent of the authors.

This workshop is also avalailable in AWS Workshop Studio [here](https://catalog.us-east-1.prod.workshops.aws/workshops/9bc28f51-d7c3-468b-ba41-72667f3273f1/en-US).

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

Let's get started with the setup of the environment.

## Setup your virtual environment

This instructions are meant to be used locally with [AWS authentication](https://docs.aws.amazon.com/cli/v1/userguide/cli-authentication-short-term.html), as well as within an [Amazon SageMaker JupyterLab](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated-jl.html) or [Amazon SageMaker Code Editor](https://docs.aws.amazon.com/sagemaker/latest/dg/code-editor.html) instance.

The course requires `Python >=3.10` (to install, visit this link: https://www.python.org/downloads/)

### 1. Download the repository

```
git clone https://github.com/aws-samples/langgraph-agents-with-amazon-bedrock.git
```

### 2. Install OS dependencies (Ubuntu/Debian)

```
sudo apt update
sudo apt-get install graphviz graphviz-dev python3-dev
pip install pipx
pipx install poetry
pipx ensurepath
source ~/.bashrc
```

Installation commands for other OS can be found here: https://pygraphviz.github.io/documentation/stable/install.html

### 3. Create a virtual environment and install python dependencies

```
cd langgraph-agents-with-amazon-bedrock
export POETRY_VIRTUALENVS_PATH="$PWD/.venv"
export INITIAL_WORKING_DIRECTORY=$(pwd)
poetry shell
```

```
cd $INITIAL_WORKING_DIRECTORY
poetry install
```

### 4. Add the kernel to the Jupyter Notebook server
The newly created python environment needs to be added to the list of available kernels of the Jupyter Notebook server.
This is possible from within the poetry environment with the command:
```
poetry run python -m ipykernel install --user --name agents-dev-env
```
The kernel might not appear right away in the list, in that case a refresh of the list will be needed.

### 5. Create and set your Tavily API key

Head over to https://app.tavily.com/home and create an API KEY for free. 

### 6. Setup the local environment variables

Create a personal copy of the temporary environment file [env.tmp](env.tmp) with the name `.env`, which is already added to the [.gitignore](.gitignore) to avoid committing personal information.
```
cp env.tmp .env
```
You can edit the preferred region to use Amazon Bedrock inside the `.env` file, if needed (the default is `us-east-1`).

### 7. Store the Tavily API key
You have two options to store the Tavily API key: 

1. Copy the Tavily API key inside the `.env` file. This option will be always checked first.

2. [Create a new secret in AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/create_secret.html) with the name "TAVILY_API_KEY", retrieve the secret `arn` by clicking on it, and [add an inline policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html#add-policies-console) with the [permission to read the secret](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access_examples.html#auth-and-access_examples_read) to your [SageMaker execution role](https://docs.aws.amazon.com/sagemaker/latest/dg/domain-user-profile-view-describe.html) replacing the copied `arn` in the example below.
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

# Additional resources

- [Amazon Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)
- [LangChain documentation](https://python.langchain.com/v0.2/docs/introduction/)
- [LangGraph github repository](https://github.com/langchain-ai/langgraph)
- [LangSmith Prompt hub](https://smith.langchain.com/hub)
