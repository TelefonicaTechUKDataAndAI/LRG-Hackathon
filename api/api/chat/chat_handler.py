import os
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class ChatHandler:
    def __init__(self) -> None:
        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
        )

    def get_chat_response(self, input_text):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful assistant that is responsible for categorising customer complaint emails. For each complaint you receive you will take the content of the email and categorise it into one of the following categories: 'Roads', 'Planning', 'Rubbish Collection', 'Flytipping'.
                    You will return your response in a JSON object that contains the following attributes:
                    - 'category': The category that you have assigned to the complaint.
                    - 'confidence': A number between 0 and 1 that represents how confident you are in your categorisation.
                    - 'response': A string that contains the response that you would like to send to the customer.

                    Only return the JSON object. Do not include any additional information.                
                    """,
                ),
                ("human", "{input}"),
            ]
        )

        chain = prompt | self.llm
        response = chain.invoke(
            {
                "input": input_text,
            }
        )

        return response
