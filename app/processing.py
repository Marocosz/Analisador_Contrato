import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_unstructured import UnstructuredLoader
from . import schemas

load_dotenv()

def analyze_contract_with_ai(file_path: str) -> schemas.ContractData:
    """
    Carrega um documento, extrai o texto e usa a IA para analisar o conteúdo.
    """
    loader = UnstructuredLoader(file_path)
    document_text = loader.load()[0].page_content

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )
    
    parser = PydanticOutputParser(pydantic_object=schemas.ContractData)

    prompt = PromptTemplate(
        template="Analise o texto do contrato abaixo e extraia as informações solicitadas. \n{format_instructions}\n\nTexto do Contrato:\n---\n{contract_text}\n---",
        input_variables=["contract_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({"contract_text": document_text})
        return result
    except Exception as e:
        print(f"Erro ao invocar a cadeia da IA: {e}")
        raise