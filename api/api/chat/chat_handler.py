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
                    "You are a helpful assistant that translates {input_language} to {output_language}.",
                ),
                ("human", "{input}"),
            ]
        )

        chain = prompt | self.llm
        response = chain.invoke(
            {
                "input_language": "English",
                "output_language": "German",
                "input": input_text,
            }
        )

        return response
