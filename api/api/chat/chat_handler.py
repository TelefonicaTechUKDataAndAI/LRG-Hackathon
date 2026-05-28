import os
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from api.enrich.doc_processor import DocumentProcessor
from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import AgentThreadCreationOptions, ThreadMessageOptions, ListSortOrder
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint = os.environ["AZURE_AI_PROJECT_CONNECTION_STRING"],
    credential = DefaultAzureCredential()
)

# class ChatHandler:
#     def __init__(self) -> None:
#         self.llm = AzureChatOpenAI(
#             azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
#         )

#     def get_agentic_chat_response(self, input_text):

#         search_response = search_handler.get_query_response(input_text)
#         prompt = ChatPromptTemplate.from_messages(
#             [
#                 (
#                     "system",
#                     """
#                     You are a redaction agent that will identify any personally identifiable information (PII) or comercially sensitive information in the input text and redact it. 
#                     You should process a input text in reasonable chunks and return the redacted text only, with no additional information or commentary.
#                     You will return your response in a JSON object that contains the following attributes:
#                     - 'category': The category that you have assigned to the complaint.
#                     - 'confidence': A number between 0 and 1 that represents how confident you are in your categorisation.
#                     - 'response': A string that contains the response that you would like to send to the customer.

#                     Only return the JSON object. Do not include any additional information.                
#                     """,
#                 ),
#                 ("human", "{input}. Respond using only the information in the following complaints procedures: {information}"),
#             ]
#         )

#         chain = prompt | self.llm
#         response = chain.invoke(
#             {
#                 "input": input_text,
#                 "information": search_response
#             }
#         )

#         return response

class AgentChatHandler:
    def __init__(self) -> None:
        self.openai = project_client.get_openai_client()

        self.agent_id = os.environ["AZURE_AI_AGENT_NAME"]
        self.agent_version = os.environ["AZURE_AI_AGENT_VERSION"]
        self.kpi_agent_id = os.environ["AZURE_KPI_AGENT_NAME"]
        self.kpi_agent_version = os.environ["AZURE_KPI_AGENT_VERSION"]
        print(f"Using agent ID: {self.agent_id}, version: {self.agent_version}")

        # Conversation history persists across turns as a list of messages
        self.conversation_history: list[dict] = []
    
    def get_agentic_chat_response(self, input_text: str) -> str:
        # Append the new user message to history
        self.conversation_history.append({
            "role": "user",
            "content": input_text,
        })

        response = self.openai.responses.create(
            extra_body={"agent_reference": {"name": self.agent_id, "version": self.agent_version, "type": "agent_reference"}},
            input=self.conversation_history,
        )

        assistant_reply = response.output_text
        
        # Append assistant reply to history to maintain context
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_reply,
        })

        return assistant_reply
    
    def get_agentic_kpi_response(self) -> str:
        
        response = self.openai.responses.create(
            extra_body={"agent_reference": {"name": self.kpi_agent_id, "version": self.kpi_agent_version, "type": "agent_reference"}},
            input=self.conversation_history,
        )

        assistant_reply = response.output_text      
        
        return assistant_reply

    def reset_conversation(self) -> None:
        """Start a fresh conversation."""
        self.conversation_history = []
        print("Conversation history cleared.")