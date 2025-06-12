import os
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from api.search.search_handler import SearchHandler
from api.enrich.audit_processor import AuditProcessor

from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import AgentThreadCreationOptions, ThreadMessageOptions, ListSortOrder
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint = os.environ["AZURE_AI_PROJECT_CONNECTION_STRING"],
    credential = DefaultAzureCredential()
)

search_handler = SearchHandler()
audit_processor = AuditProcessor()

class ChatHandler:
    def __init__(self) -> None:
        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
        )

    def get_chat_response(self, input_text):

        search_response = search_handler.get_query_response(input_text)
        audit_text = audit_processor.get_audit_text()
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful assistant to The London Fire Brigade that is responsible for reviewing uploaded audit documents. An audit document is a review of fire safety compliance according to the Regulatory Reform (Fire Safety) Order 2005. Your task is to read the audit and advise on the following: 
                    - Are any key items missing from the audit? 
                    - Are certain audit comments documented under the incorrect section according to the RRO 2005?
                    - Is the language used in the audit clear and well written english? 
                    - Are there any comments that are ephemeral or not relevant to the audit?
                    - Are there any other issues with the audit that would require the attention of a manager or senior auditor? 
                    """,
                ),
                (
                    "human", 
                    """{input}. 
                    This is the information from the audit: {audit_text}.

                    Respond using only information from the following sources: 
                    - Information from the Regulatory Reform Order 2005, which is available online
                    - The relevant internal documentaion and guidelines: {information}
                    """),
            ]
        )

        chain = prompt | self.llm
        response = chain.invoke(
            {
                "input": input_text,
                "information": search_response,
                "audit_text": audit_text
            }
        )

        return response
    
class AgentChatHandler:
    def __init__(self) -> None:
            self.agents_client = project_client.agents

            self.agent = self.agents_client.get_agent(
                agent_id=os.environ["AZURE_AI_AGENT_ID"]
            )

            print(f"Fetched agent, ID: {self.agent.id}")

    def get_agentic_chat_response(self, input_text):

        search_response = search_handler.get_query_response(input_text)
        audit_text = audit_processor.get_audit_text()
        prompt_text = f"""
        {input_text}
        This is the information from the audit document: {audit_text}

        ## Requirements:
        Respond using only information from the following sources: 
         - Information from the Regulatory Reform Order 2005, which is available online
         - The relevant internal documentaion and guidelines: {search_response}

        ## Guidelines:
        - Always respond in a clear structure that mimics that of the audit document.
        - Use Emoji's to help indicate differnent sections and types of feedback you are providing. 
        - Always respond with valid markdown that will be rendered through a web app. 
        """
        run = self.agents_client.create_thread_and_process_run(
            agent_id = self.agent.id,
            thread = AgentThreadCreationOptions(
                messages= [
                    ThreadMessageOptions(
                        role="user", content=prompt_text
                    )
                ]
            )
        )

        if run.status == "failed":
            print(f"Run failed with error: {run.last_error}")

        messages = self.agents_client.messages.list(thread_id = run.thread_id, order=ListSortOrder.ASCENDING)
        for msg in messages:
             if msg.text_messages:
                  last_text = msg.text_messages[-1]
                  print(f"{msg.role}: {last_text.text.value}")

        return last_text.text.value