Autogen Framework System with Multi-Agent Workflow

This project implements a travel agent system using multiple AI agents to handle various tasks such as refunding flights, refunding car rides, and answering general queries. The agents are powered by Azure OpenAI's chat models, and they communicate via handoffs to complete tasks.

Requirements

1.Python 3.7+

2.Azure OpenAI API: You must have access to an Azure OpenAI instance to use this code.

3.Libraries:asyncio,requests,logging,autogen-agentchat

1.Setup Install Required Libraries: Install the required libraries by running: pip install autogen-agentchat requests

2.Azure Configuration Ensure that the Azure OpenAI configuration is set up. Modify the following variables in the code with your Azure details:

-azure_deployment,model,api_version,azure_endpoint,api_key

3. Running the Script

Run the system with the following command:

python your_script.py
