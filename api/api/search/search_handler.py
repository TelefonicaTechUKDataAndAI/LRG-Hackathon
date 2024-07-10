import os
import dotenv

from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_community.retrievers import AzureAISearchRetriever


dotenv.load_dotenv()

class SearchHandler:
    def __init__(self) -> None:

        self.embeddings = AzureOpenAIEmbeddings(
                azure_deployment=os.environ["AZURE_EMBEDDINGS_DEPLOYMENT_NAME"],
                openai_api_version=os.environ["EMBEDDINGS_OPENAI_API_VERSION"],
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
        )

        self.vector_store = AzureSearch(
                azure_search_endpoint=os.environ["AZURE_AI_SEARCH_SERVICE_NAME"],
                azure_search_key=os.environ["AZURE_AI_SEARCH_API_KEY"],
                index_name=os.environ["AZURE_AI_SEARCH_INDEX_NAME"],
                embedding_function=self.embeddings.embed_query,
        )

        self.llm = AzureChatOpenAI(
            azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
        )
    
    def create_vector_index(self):

        folder_path = "./docs/"

        for doc in os.listdir(folder_path):

            doc_path = os.path.join(folder_path, doc)
            loader = TextLoader(doc_path, encoding="utf-8")

            documents = loader.load()
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.split_documents(documents)

            self.vector_store.add_documents(documents=docs)

    def get_query_response(self, input_text):

        docs = self.vector_store.similarity_search(
            query=input_text,
            k=1
        )

        return docs[0].page_content

    def get_chat_response(self, input_text):
        search_response = self.get_query_response(input_text)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant that answers questions based only on the information provided.",
                ),
                ("human", "{input}. Respond using only the following information: {information}"),
            ]
        )

        chain = prompt | self.llm
        response = chain.invoke(
            {
                "input": input_text,
                "information": search_response
            }
        )

        return response

#SearchHandler().create_vector_index()