import os
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from api.enrich.doc_processor import DocumentProcessor
from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import AgentThreadCreationOptions, ThreadMessageOptions, ListSortOrder
from azure.identity import DefaultAzureCredential

#from api.search.search_handler import SearchHandler
#search_handler = SearchHandler()

project_client = AIProjectClient(
    endpoint = os.environ["AZURE_AI_PROJECT_CONNECTION_STRING"],
    credential = DefaultAzureCredential()
)

class ChatHandler:
    def __init__(self) -> None:
        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
        )

    def get_agentic_chat_response(self, input_text):

        #search_response = search_handler.get_query_response(input_text)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a redaction agent that will identify any personally identifiable information (PII) or comercially sensitive information in the input text and redact it. 
                    You should process a input text in reasonable chunks and return the redacted text only, with no additional information or commentary.
                    You will return your response in a JSON object that contains the following attributes:
                    - 'category': The category that you have assigned to the complaint.
                    - 'confidence': A number between 0 and 1 that represents how confident you are in your categorisation.
                    - 'response': A string that contains the response that you would like to send to the customer.

                    Only return the JSON object. Do not include any additional information.                
                    """,
                ),
                ("human", "{input}. Respond using only the information in the following complaints procedures: {information}"),
            ]
        )

        chain = prompt | self.llm
        response = chain.invoke(
            {
                "input": input_text,
                #"information": search_response
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

    def get_agentic_chat_response(self, file):
        text = file["text"]
        prompt_text = f""" 
        Redact this data: {text}
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
                  #print(f"{msg.role}: {last_text.text.value}")

        return last_text.text.value